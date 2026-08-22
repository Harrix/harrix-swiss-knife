---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ticktick_api.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TickTickApiError`](#%EF%B8%8F-class-ticktickapierror)
- [🏛️ Class `TickTickHabitsClient`](#%EF%B8%8F-class-ticktickhabitsclient)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `checkin_done`](#%EF%B8%8F-method-checkin_done)
  - [⚙️ Method `create_boolean_habit`](#%EF%B8%8F-method-create_boolean_habit)
  - [⚙️ Method `export_habits_payload`](#%EF%B8%8F-method-export_habits_payload)
  - [⚙️ Method `get_done_dates_by_habit`](#%EF%B8%8F-method-get_done_dates_by_habit)
  - [⚙️ Method `list_habits`](#%EF%B8%8F-method-list_habits)
- [🔧 Function `iso_to_ticktick_stamp`](#-function-iso_to_ticktick_stamp)
- [🔧 Function `resolve_ticktick_api_token`](#-function-resolve_ticktick_api_token)

</details>

## 🏛️ Class `TickTickApiError`

```python
class TickTickApiError(RuntimeError)
```

TickTick Open API request failed.

<details>
<summary>Code:</summary>

```python
class TickTickApiError(RuntimeError):
```

</details>

## 🏛️ Class `TickTickHabitsClient`

```python
class TickTickHabitsClient
```

Minimal TickTick Open API client for habits.

<details>
<summary>Code:</summary>

```python
class TickTickHabitsClient:

    def __init__(self, token: str, *, opener: Any | None = None) -> None:
        """Create a client authenticated with a personal `tp_*` Bearer token.

        Args:

        - `token` (`str`): TickTick API token.
        - `opener` (`Any | None`): Optional urllib opener. Defaults to certifi HTTPS.

        """
        cleaned = token.strip()
        if not cleaned:
            msg = "TickTick API token is empty"
            raise ValueError(msg)
        self._token = cleaned
        self._opener = opener if opener is not None else build_https_opener()

    def checkin_done(self, habit_id: str, stamp: int) -> None:
        """Mark a habit Done on `stamp` (`YYYYMMDD`)."""
        self._request(
            "POST",
            f"/habit/{habit_id}/checkin",
            body={
                "stamp": stamp,
                "value": 1.0,
                "goal": 1.0,
                "status": _TICKTICK_DONE_STATUS,
            },
        )

    def create_boolean_habit(self, name: str) -> dict[str, Any]:
        """Create a daily Boolean habit and return the API object."""
        payload = self._request(
            "POST",
            "/habit",
            body={
                "name": name,
                "type": "Boolean",
                "goal": 1.0,
                "step": 1.0,
                "unit": "Count",
                "repeatRule": "RRULE:FREQ=DAILY;INTERVAL=1",
                "recordEnable": False,
            },
        )
        if not isinstance(payload, dict):
            msg = "TickTick create habit returned unexpected payload"
            raise TickTickApiError(msg)
        return payload

    def export_habits_payload(self, *, to_stamp: int, from_stamp: int = FALLBACK_FROM_STAMP) -> dict[str, Any]:
        """Return a payload shaped like `export_ticktick_habits_json` from the API."""
        habits = self.list_habits()
        habit_ids = [str(h.get("id") or "") for h in habits if h.get("id")]
        dates_by_id = self.get_done_dates_by_habit(habit_ids, from_stamp=from_stamp, to_stamp=to_stamp)
        payload_habits: list[dict[str, Any]] = []
        for habit in habits:
            habit_id = str(habit.get("id") or "")
            dates = dates_by_id.get(habit_id, [])
            status = habit.get("status")
            archived = status not in (None, 0, "0")
            payload_habits.append(
                {
                    "id": habit_id,
                    "name": str(habit.get("name") or ""),
                    "type": str(habit.get("type") or ""),
                    "archived": archived,
                    "archived_time": None,
                    "created_time": str(habit.get("createdTime") or "").strip() or None,
                    "total_check_ins": int(habit.get("totalCheckIns") or 0),
                    "dates": dates,
                    "date_count": len(dates),
                }
            )
        return {
            "database": "ticktick-open-api",
            "habit_count": len(payload_habits),
            "habits": payload_habits,
        }

    def get_done_dates_by_habit(
        self,
        habit_ids: list[str],
        *,
        from_stamp: int,
        to_stamp: int,
    ) -> dict[str, list[str]]:
        """Return ISO Done dates keyed by habit ID."""
        if not habit_ids:
            return {}
        raw = self._request(
            "GET",
            "/habit/checkins",
            query={
                "habitIds": ",".join(habit_ids),
                "from": str(from_stamp),
                "to": str(to_stamp),
            },
        )
        if not isinstance(raw, list):
            msg = "TickTick check-ins response must be a list"
            raise TickTickApiError(msg)
        grouped: dict[str, set[str]] = {}
        for block in raw:
            if not isinstance(block, dict):
                continue
            habit_id = str(block.get("habitId") or block.get("id") or "")
            if not habit_id:
                continue
            for checkin in block.get("checkins") or []:
                if not isinstance(checkin, dict):
                    continue
                status = checkin.get("status")
                if status is None:
                    try:
                        value = float(checkin.get("value") or 0)
                    except (TypeError, ValueError):
                        value = 0.0
                    if value < 1.0:
                        continue
                elif status != _TICKTICK_DONE_STATUS:
                    continue
                iso = stamp_to_iso_date(checkin.get("stamp"))
                if iso is None:
                    continue
                grouped.setdefault(habit_id, set()).add(iso)
        return {habit_id: sorted(dates) for habit_id, dates in grouped.items()}

    def list_habits(self) -> list[dict[str, Any]]:
        """Return all habits from TickTick."""
        payload = self._request("GET", "/habit")
        if not isinstance(payload, list):
            msg = "TickTick habit list response must be a list"
            raise TickTickApiError(msg)
        return [item for item in payload if isinstance(item, dict)]

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        query: dict[str, str] | None = None,
    ) -> Any:
        url = f"{_TICKTICK_API_BASE}{path}"
        if query:
            url = f"{url}?{urlencode(query)}"
        data = None if body is None else json.dumps(body).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
        }
        if body is not None:
            headers["Content-Type"] = "application/json"
        request = Request(url, data=data, headers=headers, method=method)  # noqa: S310
        try:
            with self._opener.open(request, timeout=120) as response:
                raw = response.read()
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
            msg = f"TickTick API HTTP {exc.code} for {method} {path}: {detail or exc.reason}"
            raise TickTickApiError(msg) from exc
        except URLError as exc:
            msg = f"TickTick API network error for {method} {path}: {exc.reason}"
            raise TickTickApiError(msg) from exc
        if not raw:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            msg = f"TickTick API returned invalid JSON for {method} {path}"
            raise TickTickApiError(msg) from exc
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, token: str, *, opener: Any | None = None) -> None
```

Create a client authenticated with a personal `tp_*` Bearer token.

Args:

- `token` (`str`): TickTick API token.
- `opener` (`Any | None`): Optional urllib opener. Defaults to certifi HTTPS.

<details>
<summary>Code:</summary>

```python
def __init__(self, token: str, *, opener: Any | None = None) -> None:
        cleaned = token.strip()
        if not cleaned:
            msg = "TickTick API token is empty"
            raise ValueError(msg)
        self._token = cleaned
        self._opener = opener if opener is not None else build_https_opener()
```

</details>

### ⚙️ Method `checkin_done`

```python
def checkin_done(self, habit_id: str, stamp: int) -> None
```

Mark a habit Done on `stamp` (`YYYYMMDD`).

<details>
<summary>Code:</summary>

```python
def checkin_done(self, habit_id: str, stamp: int) -> None:
        self._request(
            "POST",
            f"/habit/{habit_id}/checkin",
            body={
                "stamp": stamp,
                "value": 1.0,
                "goal": 1.0,
                "status": _TICKTICK_DONE_STATUS,
            },
        )
```

</details>

### ⚙️ Method `create_boolean_habit`

```python
def create_boolean_habit(self, name: str) -> dict[str, Any]
```

Create a daily Boolean habit and return the API object.

<details>
<summary>Code:</summary>

```python
def create_boolean_habit(self, name: str) -> dict[str, Any]:
        payload = self._request(
            "POST",
            "/habit",
            body={
                "name": name,
                "type": "Boolean",
                "goal": 1.0,
                "step": 1.0,
                "unit": "Count",
                "repeatRule": "RRULE:FREQ=DAILY;INTERVAL=1",
                "recordEnable": False,
            },
        )
        if not isinstance(payload, dict):
            msg = "TickTick create habit returned unexpected payload"
            raise TickTickApiError(msg)
        return payload
```

</details>

### ⚙️ Method `export_habits_payload`

```python
def export_habits_payload(self, *, to_stamp: int, from_stamp: int = FALLBACK_FROM_STAMP) -> dict[str, Any]
```

Return a payload shaped like [`export_ticktick_habits_json`](ticktick_habits.g.md#-function-export_ticktick_habits_json) from the API.

<details>
<summary>Code:</summary>

```python
def export_habits_payload(self, *, to_stamp: int, from_stamp: int = FALLBACK_FROM_STAMP) -> dict[str, Any]:
        habits = self.list_habits()
        habit_ids = [str(h.get("id") or "") for h in habits if h.get("id")]
        dates_by_id = self.get_done_dates_by_habit(habit_ids, from_stamp=from_stamp, to_stamp=to_stamp)
        payload_habits: list[dict[str, Any]] = []
        for habit in habits:
            habit_id = str(habit.get("id") or "")
            dates = dates_by_id.get(habit_id, [])
            status = habit.get("status")
            archived = status not in (None, 0, "0")
            payload_habits.append(
                {
                    "id": habit_id,
                    "name": str(habit.get("name") or ""),
                    "type": str(habit.get("type") or ""),
                    "archived": archived,
                    "archived_time": None,
                    "created_time": str(habit.get("createdTime") or "").strip() or None,
                    "total_check_ins": int(habit.get("totalCheckIns") or 0),
                    "dates": dates,
                    "date_count": len(dates),
                }
            )
        return {
            "database": "ticktick-open-api",
            "habit_count": len(payload_habits),
            "habits": payload_habits,
        }
```

</details>

### ⚙️ Method `get_done_dates_by_habit`

```python
def get_done_dates_by_habit(self, habit_ids: list[str], *, from_stamp: int, to_stamp: int) -> dict[str, list[str]]
```

Return ISO Done dates keyed by habit ID.

<details>
<summary>Code:</summary>

```python
def get_done_dates_by_habit(
        self,
        habit_ids: list[str],
        *,
        from_stamp: int,
        to_stamp: int,
    ) -> dict[str, list[str]]:
        if not habit_ids:
            return {}
        raw = self._request(
            "GET",
            "/habit/checkins",
            query={
                "habitIds": ",".join(habit_ids),
                "from": str(from_stamp),
                "to": str(to_stamp),
            },
        )
        if not isinstance(raw, list):
            msg = "TickTick check-ins response must be a list"
            raise TickTickApiError(msg)
        grouped: dict[str, set[str]] = {}
        for block in raw:
            if not isinstance(block, dict):
                continue
            habit_id = str(block.get("habitId") or block.get("id") or "")
            if not habit_id:
                continue
            for checkin in block.get("checkins") or []:
                if not isinstance(checkin, dict):
                    continue
                status = checkin.get("status")
                if status is None:
                    try:
                        value = float(checkin.get("value") or 0)
                    except (TypeError, ValueError):
                        value = 0.0
                    if value < 1.0:
                        continue
                elif status != _TICKTICK_DONE_STATUS:
                    continue
                iso = stamp_to_iso_date(checkin.get("stamp"))
                if iso is None:
                    continue
                grouped.setdefault(habit_id, set()).add(iso)
        return {habit_id: sorted(dates) for habit_id, dates in grouped.items()}
```

</details>

### ⚙️ Method `list_habits`

```python
def list_habits(self) -> list[dict[str, Any]]
```

Return all habits from TickTick.

<details>
<summary>Code:</summary>

```python
def list_habits(self) -> list[dict[str, Any]]:
        payload = self._request("GET", "/habit")
        if not isinstance(payload, list):
            msg = "TickTick habit list response must be a list"
            raise TickTickApiError(msg)
        return [item for item in payload if isinstance(item, dict)]
```

</details>

## 🔧 Function `iso_to_ticktick_stamp`

```python
def iso_to_ticktick_stamp(day: str) -> int
```

Convert `YYYY-MM-DD` to TickTick `YYYYMMDD` integer.

<details>
<summary>Code:</summary>

```python
def iso_to_ticktick_stamp(day: str) -> int:
    text = day.strip().replace("-", "")
    if len(text) != _STAMP_LENGTH or not text.isdigit():
        msg = f"Invalid ISO date for TickTick stamp: {day}"
        raise ValueError(msg)
    return int(text)
```

</details>

## 🔧 Function `resolve_ticktick_api_token`

```python
def resolve_ticktick_api_token(*, config: dict[str, Any] | None = None, project_root: Path | None = None) -> str
```

Return TickTick API token from env, config, or `api-keys` files.

Resolution order:

1. `TICKTICK_API_TOKEN` / `TICKTICK_API_KEY` environment variables
2. `ticktick_api_key` from config (after snippet expansion)
3. `api-keys/ticktick-api-key.txt` then `api-keys/ticktick-apy-key.txt`

<details>
<summary>Code:</summary>

```python
def resolve_ticktick_api_token(
    *,
    config: dict[str, Any] | None = None,
    project_root: Path | None = None,
) -> str:
    for env_name in ("TICKTICK_API_TOKEN", "TICKTICK_API_KEY"):
        env_token = _normalize_token(os.environ.get(env_name, ""))
        if env_token:
            return env_token

    if config is not None:
        cfg_token = _normalize_token(str(config.get("ticktick_api_key") or ""))
        if cfg_token:
            return cfg_token

    root = project_root if project_root is not None else get_project_root()
    for filename in _TOKEN_FILENAMES:
        token = _read_token_file(root / "api-keys" / filename)
        if token:
            return token
    return ""
```

</details>
