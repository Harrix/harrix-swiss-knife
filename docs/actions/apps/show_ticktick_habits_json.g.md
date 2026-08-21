---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `show_ticktick_habits_json.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnShowTickTickHabitsJson`](#%EF%B8%8F-class-onshowticktickhabitsjson)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnShowTickTickHabitsJson`

```python
class OnShowTickTickHabitsJson(ActionBase)
```

Show TickTick desktop habits and check-in dates as JSON.

Reads the local TickTick SQLite file (`%APPDATA%/Tick_Tick/TickTick.db`) and
lists each habit with the dates it was checked in.

<details>
<summary>Code:</summary>

```python
class OnShowTickTickHabitsJson(ActionBase):

    icon = "📋"
    title = "Show TickTick habits JSON"

    @ActionBase.handle_exceptions("show TickTick habits JSON")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Load TickTick habits and show them as formatted JSON."""
        raw_path = kwargs.get("db_path")
        db_path = Path(str(raw_path)).expanduser() if raw_path else default_ticktick_db_path()
        try:
            payload = export_ticktick_habits_json(db_path)
        except (FileNotFoundError, OSError, ValueError, sqlite3.Error) as exc:
            self.add_line(f"❌ {exc}")
            self.show_result()
            return

        self.add_line(json.dumps(payload, ensure_ascii=False, indent=2))
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Load TickTick habits and show them as formatted JSON.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        raw_path = kwargs.get("db_path")
        db_path = Path(str(raw_path)).expanduser() if raw_path else default_ticktick_db_path()
        try:
            payload = export_ticktick_habits_json(db_path)
        except (FileNotFoundError, OSError, ValueError, sqlite3.Error) as exc:
            self.add_line(f"❌ {exc}")
            self.show_result()
            return

        self.add_line(json.dumps(payload, ensure_ascii=False, indent=2))
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>
