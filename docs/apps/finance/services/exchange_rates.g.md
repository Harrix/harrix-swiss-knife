---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `exchange_rates.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ExchangeRatesService`](#%EF%B8%8F-class-exchangeratesservice)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `add_exchange_rate`](#%EF%B8%8F-method-add_exchange_rate)
  - [⚙️ Method `check_exchange_rate_exists`](#%EF%B8%8F-method-check_exchange_rate_exists)
  - [⚙️ Method `clean_invalid_exchange_rates`](#%EF%B8%8F-method-clean_invalid_exchange_rates)
  - [⚙️ Method `clear_cache`](#%EF%B8%8F-method-clear_cache)
  - [⚙️ Method `delete_exchange_rate`](#%EF%B8%8F-method-delete_exchange_rate)
  - [⚙️ Method `delete_exchange_rates_by_days`](#%EF%B8%8F-method-delete_exchange_rates_by_days)
  - [⚙️ Method `fill_missing_exchange_rates`](#%EF%B8%8F-method-fill_missing_exchange_rates)
  - [⚙️ Method `get_all_exchange_rates`](#%EF%B8%8F-method-get_all_exchange_rates)
  - [⚙️ Method `get_currency_exchange_rate_by_date`](#%EF%B8%8F-method-get_currency_exchange_rate_by_date)
  - [⚙️ Method `get_exchange_rate`](#%EF%B8%8F-method-get_exchange_rate)
  - [⚙️ Method `get_filtered_exchange_rates`](#%EF%B8%8F-method-get_filtered_exchange_rates)
  - [⚙️ Method `get_last_exchange_rate_date`](#%EF%B8%8F-method-get_last_exchange_rate_date)
  - [⚙️ Method `get_last_two_exchange_rate_records`](#%EF%B8%8F-method-get_last_two_exchange_rate_records)
  - [⚙️ Method `get_missing_exchange_rates_info`](#%EF%B8%8F-method-get_missing_exchange_rates_info)
  - [⚙️ Method `get_usd_to_currency_rate`](#%EF%B8%8F-method-get_usd_to_currency_rate)
  - [⚙️ Method `has_exchange_rates_data`](#%EF%B8%8F-method-has_exchange_rates_data)
  - [⚙️ Method `should_update_exchange_rates`](#%EF%B8%8F-method-should_update_exchange_rates)
  - [⚙️ Method `update_exchange_rate`](#%EF%B8%8F-method-update_exchange_rate)
  - [⚙️ Method `_invalidate_rate_cache`](#%EF%B8%8F-method-_invalidate_rate_cache)

</details>

## 🏛️ Class `ExchangeRatesService`

```python
class ExchangeRatesService
```

Exchange rate operations and caching; uses `DatabaseManager` as DB access.

<details>
<summary>Code:</summary>

```python
class ExchangeRatesService:

    def __init__(self, db: DatabaseManager) -> None:
        """Wire service to an open finance `DatabaseManager` instance."""
        self._db = db
        self._exchange_rate_cache: dict[str, float] = {}
        self._cache_timestamp: datetime | None = None

    def add_exchange_rate(self, currency_id: int, rate: float, date: str, *, invalidate_cache: bool = True) -> bool:
        """Insert one USD-quoted rate row."""
        query = """INSERT INTO exchange_rates (_id_currency, rate, date)
                   VALUES (:currency_id, :rate, :date)"""
        params = {
            "currency_id": currency_id,
            "rate": rate,
            "date": date,
        }
        ok = self._db.execute_simple_query(query, params)
        if ok and invalidate_cache:
            self._invalidate_rate_cache()
        return ok

    def check_exchange_rate_exists(self, currency_id: int, date: str) -> bool:
        """Return True if a row exists in ``exchange_rates`` for currency and date."""
        rows = self._db.get_rows(
            "SELECT COUNT(*) FROM exchange_rates WHERE _id_currency = :currency_id AND date = :date",
            {"currency_id": currency_id, "date": date},
        )
        return rows[0][0] > 0 if rows else False

    def clean_invalid_exchange_rates(self) -> int:
        """Delete rows with null, empty, or zero rate; return affected row count."""
        if self._db.db is None:
            return 0
        query = """DELETE FROM exchange_rates WHERE rate IS NULL OR rate = '' OR rate = 0"""
        cursor = self._db.db.exec(query)
        if cursor.lastError().isValid():
            print(f"❌ Error cleaning exchange rates: {cursor.lastError().text()}")
            return 0

        affected_rows = cursor.numRowsAffected()
        cursor.clear()
        print(f"🧹 Cleaned {affected_rows} invalid exchange rate records")
        self._invalidate_rate_cache()
        return affected_rows

    def clear_cache(self) -> None:
        """Drop in-memory rate cache (e.g. on DB close)."""
        self._exchange_rate_cache.clear()
        self._cache_timestamp = None

    def delete_exchange_rate(self, rate_id: int) -> bool:
        """Delete one ``exchange_rates`` row by primary key."""
        ok = self._db.execute_simple_query("DELETE FROM exchange_rates WHERE _id = :id", {"id": rate_id})
        if ok:
            self._invalidate_rate_cache()
        return ok

    def delete_exchange_rates_by_days(self, days: int) -> tuple[bool, int]:
        """Delete rates with ``date >= today - days``; return success and deleted count."""
        if days <= 0:
            return False, 0

        try:
            cutoff_date = (datetime.now(UTC).astimezone() - timedelta(days=days)).strftime("%Y-%m-%d")
            query = "DELETE FROM exchange_rates WHERE date >= :cutoff_date"
            params = {"cutoff_date": cutoff_date}

            success = self._db.execute_simple_query(query, params)
            if success:
                self._invalidate_rate_cache()
                query_obj = self._db.execute_query("SELECT changes()")
                if query_obj and query_obj.next():
                    deleted_count = query_obj.value(0)
                    return True, deleted_count
                return True, 0
        except Exception as e:
            print(f"❌ Error deleting exchange rates by days: {e}")
            return False, 0
        return False, 0

    def fill_missing_exchange_rates(self) -> int:
        """Forward-fill missing daily rates from earliest transaction date through today."""
        currencies = self._db.get_currencies_except_usd()
        total_filled = 0

        earliest_transaction_date = self._db.get_earliest_transaction_date()
        if not earliest_transaction_date:
            print("No transactions found, cannot determine start date for filling rates")
            return 0

        start_date_dt = datetime.fromisoformat(earliest_transaction_date)
        start_date = start_date_dt.date()
        end_date = datetime.now(UTC).astimezone().date()

        print(f"🔄 Filling missing exchange rates from {start_date} to {end_date}")

        for currency_id, currency_code, _, _ in currencies:
            print(f"📊 Processing {currency_code}...")

            query = """
                SELECT date, rate FROM exchange_rates
                WHERE _id_currency = :currency_id
                ORDER BY date ASC
            """
            rows = self._db.get_rows(query, {"currency_id": currency_id})

            if not rows:
                print(f"⚠️ No exchange rates found for {currency_code}, skipping")
                continue

            existing_rates = {row[0]: row[1] for row in rows}
            current_date = start_date
            last_known_rate = None
            currency_filled = 0

            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")

                if date_str in existing_rates:
                    last_known_rate = existing_rates[date_str]
                elif last_known_rate is not None and self.add_exchange_rate(
                    currency_id, last_known_rate, date_str, invalidate_cache=False
                ):
                    currency_filled += 1
                    total_filled += 1
                    print(f"  ✅ Filled {date_str} with rate {last_known_rate}")

                current_date = current_date + timedelta(days=1)

            print(f"  📈 Filled {currency_filled} missing dates for {currency_code}")

        self._invalidate_rate_cache()
        print(f"🎉 Total filled: {total_filled} exchange rate records")
        return total_filled

    def get_all_exchange_rates(self, limit: int | None = None) -> list[list[Any]]:
        """Return all USD-quoted rate rows joined with currency code (newest first)."""
        query = """
            SELECT er._id, 'USD', c.code, er.rate, er.date
            FROM exchange_rates er
            JOIN currencies c ON er._id_currency = c._id
            ORDER BY er.date DESC, er._id DESC
        """

        params: dict[str, Any] | None = None
        if limit is not None:
            query += " LIMIT :limit"
            params = {"limit": limit}

        rows = self._db.get_rows(query, params)
        exchange_rate_index = 3

        for row in rows:
            if (
                len(row) >= exchange_rate_index + 1
                and row[exchange_rate_index] is not None
                and row[exchange_rate_index] != ""
            ):
                try:
                    row[exchange_rate_index] = float(row[exchange_rate_index])
                except (ValueError, TypeError):
                    row[exchange_rate_index] = 0.0
            elif len(row) >= exchange_rate_index + 1:
                row[exchange_rate_index] = 0.0

        return rows

    def get_currency_exchange_rate_by_date(self, currency_id: int, date: str) -> float:
        """Return stored rate for exact currency and date (1.0 for USD or if missing)."""
        try:
            usd_currency = self._db.get_currency_by_code("USD")
            if usd_currency and currency_id == usd_currency[0]:
                return 1.0

            query = """
                SELECT rate FROM exchange_rates
                WHERE _id_currency = :currency_id AND date = :date
                LIMIT 1
            """
            params = {"currency_id": currency_id, "date": date}

            rows = self._db.get_rows(query, params)
            if rows and rows[0][0] is not None and rows[0][0] != "":
                try:
                    return float(rows[0][0])
                except (ValueError, TypeError):
                    return 1.0
        except Exception as e:
            print(f"Error getting currency exchange rate by date: {e}")
            return 1.0
        return 1.0

    def get_exchange_rate(self, from_currency_id: int, to_currency_id: int, date: str | None = None) -> float:
        """Convert between two currencies using USD as pivot (same semantics as before)."""
        if from_currency_id == to_currency_id:
            return 1.0

        try:
            check_query = "SELECT COUNT(*) FROM exchange_rates LIMIT 1"
            rows = self._db.get_rows(check_query)
            if not rows or rows[0][0] == 0:
                return 1.0
        except Exception:
            return 1.0

        usd_currency = self._db.get_currency_by_code("USD")
        if not usd_currency:
            return 1.0
        usd_currency_id = usd_currency[0]

        if from_currency_id == usd_currency_id:
            currency_to_usd_rate = self.get_usd_to_currency_rate(to_currency_id, date)
            return 1.0 / currency_to_usd_rate if currency_to_usd_rate != 0 else 1.0
        if to_currency_id == usd_currency_id:
            return self.get_usd_to_currency_rate(from_currency_id, date)
        from_currency_to_usd_rate = self.get_usd_to_currency_rate(from_currency_id, date)
        to_currency_to_usd_rate = self.get_usd_to_currency_rate(to_currency_id, date)
        if from_currency_to_usd_rate != 0 and to_currency_to_usd_rate != 0:
            return from_currency_to_usd_rate / to_currency_to_usd_rate
        return 1.0

    def get_filtered_exchange_rates(
        self,
        currency_id: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        limit: int | None = None,
    ) -> list[list[Any]]:
        """Query exchange rates with optional currency and date range filters."""
        query = """
            SELECT er._id, 'USD', c.code, er.rate, er.date
            FROM exchange_rates er
            JOIN currencies c ON er._id_currency = c._id
        """

        conditions = []
        params: dict[str, Any] = {}

        if currency_id is not None:
            conditions.append("er._id_currency = :currency_id")
            params["currency_id"] = currency_id

        if date_from is not None:
            conditions.append("er.date >= :date_from")
            params["date_from"] = date_from

        if date_to is not None:
            conditions.append("er.date <= :date_to")
            params["date_to"] = date_to

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY er.date DESC, er._id DESC"

        if limit is not None:
            query += " LIMIT :limit"
            params["limit"] = limit

        try:
            query_obj = self._db.execute_query(query, params)
            if not query_obj:
                return []

            rows = self._db.rows_from_query(query_obj)
            rate_index = 3
            for row in rows:
                if len(row) > rate_index:
                    value = row[rate_index]
                    try:
                        row[rate_index] = float(value) if value not in (None, "") else 0.0
                    except (ValueError, TypeError):
                        row[rate_index] = 0.0
        except Exception as e:
            print(f"❌ Error getting filtered exchange rates: {e}")
            return []
        return rows

    def get_last_exchange_rate_date(self, currency_id: int) -> str | None:
        """Return latest ``date`` string for a currency or None."""
        rows = self._db.get_rows(
            "SELECT MAX(date) FROM exchange_rates WHERE _id_currency = :currency_id", {"currency_id": currency_id}
        )
        return rows[0][0] if rows and rows[0][0] else None

    def get_last_two_exchange_rate_records(self, currency_id: int) -> list[tuple[str, float]]:
        """Return up to two most recent (date, rate) pairs in chronological order."""
        rows = self._db.get_rows(
            """SELECT date, rate
               FROM exchange_rates
               WHERE _id_currency = :currency_id
               ORDER BY date DESC
               LIMIT 2""",
            {"currency_id": currency_id},
        )
        return [(row[0], float(row[1])) for row in reversed(rows)] if rows else []

    def get_missing_exchange_rates_info(self, date_from: str, date_to: str) -> dict[int, list[str]]:
        """Map non-USD currency id to dates in range with no rate row (with console logging)."""
        missing_info: dict[int, list[str]] = {}
        currencies = self._db.get_currencies_except_usd()

        start_date = datetime.fromisoformat(date_from).date()
        end_date = datetime.fromisoformat(date_to).date()

        all_dates: list[str] = []
        current_date = start_date
        while current_date <= end_date:
            all_dates.append(current_date.strftime("%Y-%m-%d"))
            current_date = current_date + timedelta(days=1)

        print(f"Checking exchange rates from {date_from} to {date_to} ({len(all_dates)} days)")

        for currency_id, currency_code, _, _ in currencies:
            query = """
                SELECT DISTINCT date FROM exchange_rates
                WHERE _id_currency = :currency_id
                AND date BETWEEN :date_from AND :date_to
                ORDER BY date
            """

            rows = self._db.get_rows(query, {"currency_id": currency_id, "date_from": date_from, "date_to": date_to})
            existing_dates = {row[0] for row in rows}
            missing_dates = [date_str for date_str in all_dates if date_str not in existing_dates]

            if missing_dates:
                print(f"📊 {currency_code}: {len(missing_dates)} missing rates")

                max_sample_size = 10
                sample_size = min(max_sample_size, len(missing_dates))
                sample_dates = missing_dates[:sample_size]
                print(f"    First {sample_size} missing dates: {', '.join(sample_dates)}")

                if len(missing_dates) > max_sample_size:
                    print(f"    ... and {len(missing_dates) - max_sample_size} more dates")

                if len(missing_dates) > 1:
                    print(f"    Range: from {missing_dates[0]} to {missing_dates[-1]}")

                missing_info[currency_id] = missing_dates
            else:
                print(f"✅ {currency_code}: all rates present")

        if not missing_info:
            print("✅ All exchange rates are present in the specified date range")
        else:
            total_missing = sum(len(dates) for dates in missing_info.values())
            print(f"\n📈 TOTAL: {total_missing} missing records for {len(missing_info)} currencies")

            if missing_info:
                first_currency_id = next(iter(missing_info))
                first_currency_code = next(code for id_item, code, _1, _2 in currencies if id_item == first_currency_id)
                first_missing = missing_info[first_currency_id]

                print(f"\n🔍 FULL LIST for {first_currency_code} ({len(first_missing)} dates):")
                for i, one_date in enumerate(first_missing, 1):
                    print(f"  {i:4d}. {one_date}")
                    max_dates = 50
                    if i >= max_dates:
                        print(f"  ... and {len(first_missing) - max_dates} more dates")
                        break

        return missing_info

    def get_usd_to_currency_rate(self, currency_id: int, date: str | None = None) -> float:
        """Return currency→USD rate (minor naming quirk); cached briefly in memory."""
        usd_currency = self._db.get_currency_by_code("USD")
        if usd_currency and currency_id == usd_currency[0]:
            return 1.0

        cache_key = f"{currency_id}_{date or 'latest'}"
        now = datetime.now(UTC).astimezone()
        if (
            self._cache_timestamp
            and (now - self._cache_timestamp) < timedelta(minutes=5)
            and cache_key in self._exchange_rate_cache
        ):
            return self._exchange_rate_cache[cache_key]

        if date:
            query = """
                SELECT rate FROM exchange_rates
                WHERE _id_currency = :currency_id AND date <= :date
                ORDER BY date DESC LIMIT 1
            """
            params: dict[str, Any] = {"currency_id": currency_id, "date": date}
        else:
            query = """
                SELECT rate FROM exchange_rates
                WHERE _id_currency = :currency_id
                ORDER BY date DESC LIMIT 1
            """
            params = {"currency_id": currency_id}

        rows = self._db.get_rows(query, params)
        if rows and rows[0][0] is not None and rows[0][0] != "":
            try:
                rate = float(rows[0][0])
                self._exchange_rate_cache[cache_key] = rate
                self._cache_timestamp = now
            except (ValueError, TypeError):
                return 1.0
            return rate

        return 1.0

    def has_exchange_rates_data(self) -> bool:
        """Return True if ``exchange_rates`` has at least one row."""
        try:
            rows = self._db.get_rows("SELECT COUNT(*) FROM exchange_rates")
            return rows[0][0] > 0 if rows else False
        except Exception as e:
            print(f"Error checking exchange rates data: {e}")
            return False

    def should_update_exchange_rates(self) -> bool:
        """Return True if any non-USD currency lacks a rate dated today."""
        try:
            today = datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")
            currencies = self._db.get_currencies_except_usd()

            if not currencies:
                return False

            for currency_id, currency_code, _, _ in currencies:
                last_date = self.get_last_exchange_rate_date(currency_id)
                if not last_date or last_date != today:
                    print(f"📊 [Exchange Rates] {currency_code} needs update (last: {last_date}, today: {today})")
                    return True

            print(f"✅ [Exchange Rates] All currencies are up to date (last update: {today})")
        except Exception as e:
            print(f"❌ Error checking exchange rates update status: {e}")
            return True
        return False

    def update_exchange_rate(self, currency_id: int, date: str, rate: float) -> bool:
        """Upsert rate for currency and date (no-op for USD id)."""
        try:
            usd_currency = self._db.get_currency_by_code("USD")
            if usd_currency and currency_id == usd_currency[0]:
                return False

            check_query = """
                SELECT _id FROM exchange_rates
                WHERE _id_currency = :currency_id AND date = :date
                LIMIT 1
            """
            check_params = {"currency_id": currency_id, "date": date}
            existing_rows = self._db.get_rows(check_query, check_params)

            if existing_rows:
                update_query = """
                    UPDATE exchange_rates
                    SET rate = :rate
                    WHERE _id_currency = :currency_id AND date = :date
                """
                params_u = {"currency_id": currency_id, "date": date, "rate": rate}
                ok = self._db.execute_simple_query(update_query, params_u)
            else:
                insert_query = """
                    INSERT INTO exchange_rates (_id_currency, date, rate)
                    VALUES (:currency_id, :date, :rate)
                """
                params_i = {"currency_id": currency_id, "date": date, "rate": rate}
                ok = self._db.execute_simple_query(insert_query, params_i)
            if ok:
                self._invalidate_rate_cache()
        except Exception as e:
            print(f"Error updating exchange rate: {e}")
            return False
        else:
            return ok

    def _invalidate_rate_cache(self) -> None:
        self._exchange_rate_cache.clear()
        self._cache_timestamp = None
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, db: DatabaseManager) -> None
```

Wire service to an open finance `DatabaseManager` instance.

<details>
<summary>Code:</summary>

```python
def __init__(self, db: DatabaseManager) -> None:
        self._db = db
        self._exchange_rate_cache: dict[str, float] = {}
        self._cache_timestamp: datetime | None = None
```

</details>

### ⚙️ Method `add_exchange_rate`

```python
def add_exchange_rate(self, currency_id: int, rate: float, date: str) -> bool
```

Insert one USD-quoted rate row.

<details>
<summary>Code:</summary>

```python
def add_exchange_rate(self, currency_id: int, rate: float, date: str, *, invalidate_cache: bool = True) -> bool:
        query = """INSERT INTO exchange_rates (_id_currency, rate, date)
                   VALUES (:currency_id, :rate, :date)"""
        params = {
            "currency_id": currency_id,
            "rate": rate,
            "date": date,
        }
        ok = self._db.execute_simple_query(query, params)
        if ok and invalidate_cache:
            self._invalidate_rate_cache()
        return ok
```

</details>

### ⚙️ Method `check_exchange_rate_exists`

```python
def check_exchange_rate_exists(self, currency_id: int, date: str) -> bool
```

Return True if a row exists in `exchange_rates` for currency and date.

<details>
<summary>Code:</summary>

```python
def check_exchange_rate_exists(self, currency_id: int, date: str) -> bool:
        rows = self._db.get_rows(
            "SELECT COUNT(*) FROM exchange_rates WHERE _id_currency = :currency_id AND date = :date",
            {"currency_id": currency_id, "date": date},
        )
        return rows[0][0] > 0 if rows else False
```

</details>

### ⚙️ Method `clean_invalid_exchange_rates`

```python
def clean_invalid_exchange_rates(self) -> int
```

Delete rows with null, empty, or zero rate; return affected row count.

<details>
<summary>Code:</summary>

```python
def clean_invalid_exchange_rates(self) -> int:
        if self._db.db is None:
            return 0
        query = """DELETE FROM exchange_rates WHERE rate IS NULL OR rate = '' OR rate = 0"""
        cursor = self._db.db.exec(query)
        if cursor.lastError().isValid():
            print(f"❌ Error cleaning exchange rates: {cursor.lastError().text()}")
            return 0

        affected_rows = cursor.numRowsAffected()
        cursor.clear()
        print(f"🧹 Cleaned {affected_rows} invalid exchange rate records")
        self._invalidate_rate_cache()
        return affected_rows
```

</details>

### ⚙️ Method `clear_cache`

```python
def clear_cache(self) -> None
```

Drop in-memory rate cache (e.g. on DB close).

<details>
<summary>Code:</summary>

```python
def clear_cache(self) -> None:
        self._exchange_rate_cache.clear()
        self._cache_timestamp = None
```

</details>

### ⚙️ Method `delete_exchange_rate`

```python
def delete_exchange_rate(self, rate_id: int) -> bool
```

Delete one `exchange_rates` row by primary key.

<details>
<summary>Code:</summary>

```python
def delete_exchange_rate(self, rate_id: int) -> bool:
        ok = self._db.execute_simple_query("DELETE FROM exchange_rates WHERE _id = :id", {"id": rate_id})
        if ok:
            self._invalidate_rate_cache()
        return ok
```

</details>

### ⚙️ Method `delete_exchange_rates_by_days`

```python
def delete_exchange_rates_by_days(self, days: int) -> tuple[bool, int]
```

Delete rates with `date >= today - days`; return success and deleted count.

<details>
<summary>Code:</summary>

```python
def delete_exchange_rates_by_days(self, days: int) -> tuple[bool, int]:
        if days <= 0:
            return False, 0

        try:
            cutoff_date = (datetime.now(UTC).astimezone() - timedelta(days=days)).strftime("%Y-%m-%d")
            query = "DELETE FROM exchange_rates WHERE date >= :cutoff_date"
            params = {"cutoff_date": cutoff_date}

            success = self._db.execute_simple_query(query, params)
            if success:
                self._invalidate_rate_cache()
                query_obj = self._db.execute_query("SELECT changes()")
                if query_obj and query_obj.next():
                    deleted_count = query_obj.value(0)
                    return True, deleted_count
                return True, 0
        except Exception as e:
            print(f"❌ Error deleting exchange rates by days: {e}")
            return False, 0
        return False, 0
```

</details>

### ⚙️ Method `fill_missing_exchange_rates`

```python
def fill_missing_exchange_rates(self) -> int
```

Forward-fill missing daily rates from earliest transaction date through today.

<details>
<summary>Code:</summary>

```python
def fill_missing_exchange_rates(self) -> int:
        currencies = self._db.get_currencies_except_usd()
        total_filled = 0

        earliest_transaction_date = self._db.get_earliest_transaction_date()
        if not earliest_transaction_date:
            print("No transactions found, cannot determine start date for filling rates")
            return 0

        start_date_dt = datetime.fromisoformat(earliest_transaction_date)
        start_date = start_date_dt.date()
        end_date = datetime.now(UTC).astimezone().date()

        print(f"🔄 Filling missing exchange rates from {start_date} to {end_date}")

        for currency_id, currency_code, _, _ in currencies:
            print(f"📊 Processing {currency_code}...")

            query = """
                SELECT date, rate FROM exchange_rates
                WHERE _id_currency = :currency_id
                ORDER BY date ASC
            """
            rows = self._db.get_rows(query, {"currency_id": currency_id})

            if not rows:
                print(f"⚠️ No exchange rates found for {currency_code}, skipping")
                continue

            existing_rates = {row[0]: row[1] for row in rows}
            current_date = start_date
            last_known_rate = None
            currency_filled = 0

            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")

                if date_str in existing_rates:
                    last_known_rate = existing_rates[date_str]
                elif last_known_rate is not None and self.add_exchange_rate(
                    currency_id, last_known_rate, date_str, invalidate_cache=False
                ):
                    currency_filled += 1
                    total_filled += 1
                    print(f"  ✅ Filled {date_str} with rate {last_known_rate}")

                current_date = current_date + timedelta(days=1)

            print(f"  📈 Filled {currency_filled} missing dates for {currency_code}")

        self._invalidate_rate_cache()
        print(f"🎉 Total filled: {total_filled} exchange rate records")
        return total_filled
```

</details>

### ⚙️ Method `get_all_exchange_rates`

```python
def get_all_exchange_rates(self, limit: int | None = None) -> list[list[Any]]
```

Return all USD-quoted rate rows joined with currency code (newest first).

<details>
<summary>Code:</summary>

```python
def get_all_exchange_rates(self, limit: int | None = None) -> list[list[Any]]:
        query = """
            SELECT er._id, 'USD', c.code, er.rate, er.date
            FROM exchange_rates er
            JOIN currencies c ON er._id_currency = c._id
            ORDER BY er.date DESC, er._id DESC
        """

        params: dict[str, Any] | None = None
        if limit is not None:
            query += " LIMIT :limit"
            params = {"limit": limit}

        rows = self._db.get_rows(query, params)
        exchange_rate_index = 3

        for row in rows:
            if (
                len(row) >= exchange_rate_index + 1
                and row[exchange_rate_index] is not None
                and row[exchange_rate_index] != ""
            ):
                try:
                    row[exchange_rate_index] = float(row[exchange_rate_index])
                except (ValueError, TypeError):
                    row[exchange_rate_index] = 0.0
            elif len(row) >= exchange_rate_index + 1:
                row[exchange_rate_index] = 0.0

        return rows
```

</details>

### ⚙️ Method `get_currency_exchange_rate_by_date`

```python
def get_currency_exchange_rate_by_date(self, currency_id: int, date: str) -> float
```

Return stored rate for exact currency and date (1.0 for USD or if missing).

<details>
<summary>Code:</summary>

```python
def get_currency_exchange_rate_by_date(self, currency_id: int, date: str) -> float:
        try:
            usd_currency = self._db.get_currency_by_code("USD")
            if usd_currency and currency_id == usd_currency[0]:
                return 1.0

            query = """
                SELECT rate FROM exchange_rates
                WHERE _id_currency = :currency_id AND date = :date
                LIMIT 1
            """
            params = {"currency_id": currency_id, "date": date}

            rows = self._db.get_rows(query, params)
            if rows and rows[0][0] is not None and rows[0][0] != "":
                try:
                    return float(rows[0][0])
                except (ValueError, TypeError):
                    return 1.0
        except Exception as e:
            print(f"Error getting currency exchange rate by date: {e}")
            return 1.0
        return 1.0
```

</details>

### ⚙️ Method `get_exchange_rate`

```python
def get_exchange_rate(self, from_currency_id: int, to_currency_id: int, date: str | None = None) -> float
```

Convert between two currencies using USD as pivot (same semantics as before).

<details>
<summary>Code:</summary>

```python
def get_exchange_rate(self, from_currency_id: int, to_currency_id: int, date: str | None = None) -> float:
        if from_currency_id == to_currency_id:
            return 1.0

        try:
            check_query = "SELECT COUNT(*) FROM exchange_rates LIMIT 1"
            rows = self._db.get_rows(check_query)
            if not rows or rows[0][0] == 0:
                return 1.0
        except Exception:
            return 1.0

        usd_currency = self._db.get_currency_by_code("USD")
        if not usd_currency:
            return 1.0
        usd_currency_id = usd_currency[0]

        if from_currency_id == usd_currency_id:
            currency_to_usd_rate = self.get_usd_to_currency_rate(to_currency_id, date)
            return 1.0 / currency_to_usd_rate if currency_to_usd_rate != 0 else 1.0
        if to_currency_id == usd_currency_id:
            return self.get_usd_to_currency_rate(from_currency_id, date)
        from_currency_to_usd_rate = self.get_usd_to_currency_rate(from_currency_id, date)
        to_currency_to_usd_rate = self.get_usd_to_currency_rate(to_currency_id, date)
        if from_currency_to_usd_rate != 0 and to_currency_to_usd_rate != 0:
            return from_currency_to_usd_rate / to_currency_to_usd_rate
        return 1.0
```

</details>

### ⚙️ Method `get_filtered_exchange_rates`

```python
def get_filtered_exchange_rates(self, currency_id: int | None = None, date_from: str | None = None, date_to: str | None = None, limit: int | None = None) -> list[list[Any]]
```

Query exchange rates with optional currency and date range filters.

<details>
<summary>Code:</summary>

```python
def get_filtered_exchange_rates(
        self,
        currency_id: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        limit: int | None = None,
    ) -> list[list[Any]]:
        query = """
            SELECT er._id, 'USD', c.code, er.rate, er.date
            FROM exchange_rates er
            JOIN currencies c ON er._id_currency = c._id
        """

        conditions = []
        params: dict[str, Any] = {}

        if currency_id is not None:
            conditions.append("er._id_currency = :currency_id")
            params["currency_id"] = currency_id

        if date_from is not None:
            conditions.append("er.date >= :date_from")
            params["date_from"] = date_from

        if date_to is not None:
            conditions.append("er.date <= :date_to")
            params["date_to"] = date_to

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY er.date DESC, er._id DESC"

        if limit is not None:
            query += " LIMIT :limit"
            params["limit"] = limit

        try:
            query_obj = self._db.execute_query(query, params)
            if not query_obj:
                return []

            rows = self._db.rows_from_query(query_obj)
            rate_index = 3
            for row in rows:
                if len(row) > rate_index:
                    value = row[rate_index]
                    try:
                        row[rate_index] = float(value) if value not in (None, "") else 0.0
                    except (ValueError, TypeError):
                        row[rate_index] = 0.0
        except Exception as e:
            print(f"❌ Error getting filtered exchange rates: {e}")
            return []
        return rows
```

</details>

### ⚙️ Method `get_last_exchange_rate_date`

```python
def get_last_exchange_rate_date(self, currency_id: int) -> str | None
```

Return latest `date` string for a currency or None.

<details>
<summary>Code:</summary>

```python
def get_last_exchange_rate_date(self, currency_id: int) -> str | None:
        rows = self._db.get_rows(
            "SELECT MAX(date) FROM exchange_rates WHERE _id_currency = :currency_id", {"currency_id": currency_id}
        )
        return rows[0][0] if rows and rows[0][0] else None
```

</details>

### ⚙️ Method `get_last_two_exchange_rate_records`

```python
def get_last_two_exchange_rate_records(self, currency_id: int) -> list[tuple[str, float]]
```

Return up to two most recent (date, rate) pairs in chronological order.

<details>
<summary>Code:</summary>

```python
def get_last_two_exchange_rate_records(self, currency_id: int) -> list[tuple[str, float]]:
        rows = self._db.get_rows(
            """SELECT date, rate
               FROM exchange_rates
               WHERE _id_currency = :currency_id
               ORDER BY date DESC
               LIMIT 2""",
            {"currency_id": currency_id},
        )
        return [(row[0], float(row[1])) for row in reversed(rows)] if rows else []
```

</details>

### ⚙️ Method `get_missing_exchange_rates_info`

```python
def get_missing_exchange_rates_info(self, date_from: str, date_to: str) -> dict[int, list[str]]
```

Map non-USD currency id to dates in range with no rate row (with console logging).

<details>
<summary>Code:</summary>

```python
def get_missing_exchange_rates_info(self, date_from: str, date_to: str) -> dict[int, list[str]]:
        missing_info: dict[int, list[str]] = {}
        currencies = self._db.get_currencies_except_usd()

        start_date = datetime.fromisoformat(date_from).date()
        end_date = datetime.fromisoformat(date_to).date()

        all_dates: list[str] = []
        current_date = start_date
        while current_date <= end_date:
            all_dates.append(current_date.strftime("%Y-%m-%d"))
            current_date = current_date + timedelta(days=1)

        print(f"Checking exchange rates from {date_from} to {date_to} ({len(all_dates)} days)")

        for currency_id, currency_code, _, _ in currencies:
            query = """
                SELECT DISTINCT date FROM exchange_rates
                WHERE _id_currency = :currency_id
                AND date BETWEEN :date_from AND :date_to
                ORDER BY date
            """

            rows = self._db.get_rows(query, {"currency_id": currency_id, "date_from": date_from, "date_to": date_to})
            existing_dates = {row[0] for row in rows}
            missing_dates = [date_str for date_str in all_dates if date_str not in existing_dates]

            if missing_dates:
                print(f"📊 {currency_code}: {len(missing_dates)} missing rates")

                max_sample_size = 10
                sample_size = min(max_sample_size, len(missing_dates))
                sample_dates = missing_dates[:sample_size]
                print(f"    First {sample_size} missing dates: {', '.join(sample_dates)}")

                if len(missing_dates) > max_sample_size:
                    print(f"    ... and {len(missing_dates) - max_sample_size} more dates")

                if len(missing_dates) > 1:
                    print(f"    Range: from {missing_dates[0]} to {missing_dates[-1]}")

                missing_info[currency_id] = missing_dates
            else:
                print(f"✅ {currency_code}: all rates present")

        if not missing_info:
            print("✅ All exchange rates are present in the specified date range")
        else:
            total_missing = sum(len(dates) for dates in missing_info.values())
            print(f"\n📈 TOTAL: {total_missing} missing records for {len(missing_info)} currencies")

            if missing_info:
                first_currency_id = next(iter(missing_info))
                first_currency_code = next(code for id_item, code, _1, _2 in currencies if id_item == first_currency_id)
                first_missing = missing_info[first_currency_id]

                print(f"\n🔍 FULL LIST for {first_currency_code} ({len(first_missing)} dates):")
                for i, one_date in enumerate(first_missing, 1):
                    print(f"  {i:4d}. {one_date}")
                    max_dates = 50
                    if i >= max_dates:
                        print(f"  ... and {len(first_missing) - max_dates} more dates")
                        break

        return missing_info
```

</details>

### ⚙️ Method `get_usd_to_currency_rate`

```python
def get_usd_to_currency_rate(self, currency_id: int, date: str | None = None) -> float
```

Return currency→USD rate (minor naming quirk); cached briefly in memory.

<details>
<summary>Code:</summary>

```python
def get_usd_to_currency_rate(self, currency_id: int, date: str | None = None) -> float:
        usd_currency = self._db.get_currency_by_code("USD")
        if usd_currency and currency_id == usd_currency[0]:
            return 1.0

        cache_key = f"{currency_id}_{date or 'latest'}"
        now = datetime.now(UTC).astimezone()
        if (
            self._cache_timestamp
            and (now - self._cache_timestamp) < timedelta(minutes=5)
            and cache_key in self._exchange_rate_cache
        ):
            return self._exchange_rate_cache[cache_key]

        if date:
            query = """
                SELECT rate FROM exchange_rates
                WHERE _id_currency = :currency_id AND date <= :date
                ORDER BY date DESC LIMIT 1
            """
            params: dict[str, Any] = {"currency_id": currency_id, "date": date}
        else:
            query = """
                SELECT rate FROM exchange_rates
                WHERE _id_currency = :currency_id
                ORDER BY date DESC LIMIT 1
            """
            params = {"currency_id": currency_id}

        rows = self._db.get_rows(query, params)
        if rows and rows[0][0] is not None and rows[0][0] != "":
            try:
                rate = float(rows[0][0])
                self._exchange_rate_cache[cache_key] = rate
                self._cache_timestamp = now
            except (ValueError, TypeError):
                return 1.0
            return rate

        return 1.0
```

</details>

### ⚙️ Method `has_exchange_rates_data`

```python
def has_exchange_rates_data(self) -> bool
```

Return True if `exchange_rates` has at least one row.

<details>
<summary>Code:</summary>

```python
def has_exchange_rates_data(self) -> bool:
        try:
            rows = self._db.get_rows("SELECT COUNT(*) FROM exchange_rates")
            return rows[0][0] > 0 if rows else False
        except Exception as e:
            print(f"Error checking exchange rates data: {e}")
            return False
```

</details>

### ⚙️ Method `should_update_exchange_rates`

```python
def should_update_exchange_rates(self) -> bool
```

Return True if any non-USD currency lacks a rate dated today.

<details>
<summary>Code:</summary>

```python
def should_update_exchange_rates(self) -> bool:
        try:
            today = datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")
            currencies = self._db.get_currencies_except_usd()

            if not currencies:
                return False

            for currency_id, currency_code, _, _ in currencies:
                last_date = self.get_last_exchange_rate_date(currency_id)
                if not last_date or last_date != today:
                    print(f"📊 [Exchange Rates] {currency_code} needs update (last: {last_date}, today: {today})")
                    return True

            print(f"✅ [Exchange Rates] All currencies are up to date (last update: {today})")
        except Exception as e:
            print(f"❌ Error checking exchange rates update status: {e}")
            return True
        return False
```

</details>

### ⚙️ Method `update_exchange_rate`

```python
def update_exchange_rate(self, currency_id: int, date: str, rate: float) -> bool
```

Upsert rate for currency and date (no-op for USD id).

<details>
<summary>Code:</summary>

```python
def update_exchange_rate(self, currency_id: int, date: str, rate: float) -> bool:
        try:
            usd_currency = self._db.get_currency_by_code("USD")
            if usd_currency and currency_id == usd_currency[0]:
                return False

            check_query = """
                SELECT _id FROM exchange_rates
                WHERE _id_currency = :currency_id AND date = :date
                LIMIT 1
            """
            check_params = {"currency_id": currency_id, "date": date}
            existing_rows = self._db.get_rows(check_query, check_params)

            if existing_rows:
                update_query = """
                    UPDATE exchange_rates
                    SET rate = :rate
                    WHERE _id_currency = :currency_id AND date = :date
                """
                params_u = {"currency_id": currency_id, "date": date, "rate": rate}
                ok = self._db.execute_simple_query(update_query, params_u)
            else:
                insert_query = """
                    INSERT INTO exchange_rates (_id_currency, date, rate)
                    VALUES (:currency_id, :date, :rate)
                """
                params_i = {"currency_id": currency_id, "date": date, "rate": rate}
                ok = self._db.execute_simple_query(insert_query, params_i)
            if ok:
                self._invalidate_rate_cache()
        except Exception as e:
            print(f"Error updating exchange rate: {e}")
            return False
        else:
            return ok
```

</details>

### ⚙️ Method `_invalidate_rate_cache`

```python
def _invalidate_rate_cache(self) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _invalidate_rate_cache(self) -> None:
        self._exchange_rate_cache.clear()
        self._cache_timestamp = None
```

</details>
