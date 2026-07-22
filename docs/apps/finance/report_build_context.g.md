---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `report_build_context.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ReportBuildContext`](#%EF%B8%8F-class-reportbuildcontext)
  - [⚙️ Method `load`](#%EF%B8%8F-method-load)

</details>

## 🏛️ Class `ReportBuildContext`

```python
class ReportBuildContext
```

Preloaded database state for building finance reports off the UI thread.

<details>
<summary>Code:</summary>

```python
class ReportBuildContext:

    db_manager: DatabaseManager
    currency_id: int
    rates: PreloadedExchangeRates
    currencies_by_code: dict[str, tuple[int, str, str]]
    currencies_by_id: dict[int, tuple[str, str, str]]

    @classmethod
    def load(cls, db_filename: str) -> ReportBuildContext:
        """Open the database and preload currencies and exchange rates."""
        db_manager = DatabaseManager(db_filename)
        currencies_by_code, currencies_by_id = db_manager.get_all_currencies_map()
        return cls(
            db_manager=db_manager,
            currency_id=db_manager.get_default_currency_id(),
            rates=db_manager.exchange_rates.preload_all_rates(),
            currencies_by_code=currencies_by_code,
            currencies_by_id=currencies_by_id,
        )
```

</details>

### ⚙️ Method `load`

```python
def load(cls, db_filename: str) -> ReportBuildContext
```

Open the database and preload currencies and exchange rates.

<details>
<summary>Code:</summary>

```python
def load(cls, db_filename: str) -> ReportBuildContext:
        db_manager = DatabaseManager(db_filename)
        currencies_by_code, currencies_by_id = db_manager.get_all_currencies_map()
        return cls(
            db_manager=db_manager,
            currency_id=db_manager.get_default_currency_id(),
            rates=db_manager.exchange_rates.preload_all_rates(),
            currencies_by_code=currencies_by_code,
            currencies_by_id=currencies_by_id,
        )
```

</details>
