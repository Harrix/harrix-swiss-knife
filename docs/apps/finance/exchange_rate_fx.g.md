---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `exchange_rate_fx.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `configure_yfinance_logging`](#-function-configure_yfinance_logging)
- [🔧 Function `dates_through_closed_fx_day`](#-function-dates_through_closed_fx_day)
- [🔧 Function `latest_closed_fx_date`](#-function-latest_closed_fx_date)

</details>

## 🔧 Function `configure_yfinance_logging`

```python
def configure_yfinance_logging() -> None
```

Silence yfinance WARNING/ERROR spam (SSL crumb, empty history / delisted).

<details>
<summary>Code:</summary>

```python
def configure_yfinance_logging() -> None:
    for name in _YFINANCE_LOGGERS:
        logging.getLogger(name).setLevel(logging.CRITICAL)
```

</details>

## 🔧 Function `dates_through_closed_fx_day`

```python
def dates_through_closed_fx_day(dates: list[str], *, now: datetime | None = None) -> list[str]
```

Drop today/future dates that yfinance often returns empty for.

<details>
<summary>Code:</summary>

```python
def dates_through_closed_fx_day(dates: list[str], *, now: datetime | None = None) -> list[str]:
    cutoff = latest_closed_fx_date(now=now).strftime("%Y-%m-%d")
    return [day for day in dates if day <= cutoff]
```

</details>

## 🔧 Function `latest_closed_fx_date`

```python
def latest_closed_fx_date(*, now: datetime | None = None) -> date
```

Return yesterday in local time — the latest day Yahoo daily FX bars are reliable.

<details>
<summary>Code:</summary>

```python
def latest_closed_fx_date(*, now: datetime | None = None) -> date:
    current = (now or datetime.now(UTC).astimezone()).date()
    return current - timedelta(days=1)
```

</details>
