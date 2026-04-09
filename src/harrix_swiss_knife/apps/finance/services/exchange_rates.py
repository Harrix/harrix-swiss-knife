"""Exchange rates: CRUD, queries, and short-lived rate cache for finance DB."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from harrix_swiss_knife.apps.finance.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class ExchangeRatesService:
    """Exchange rate operations and caching; uses `DatabaseManager` as DB access."""

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
            logger.error("Error cleaning exchange rates: %s", cursor.lastError().text())
            return 0

        affected_rows = cursor.numRowsAffected()
        cursor.clear()
        logger.info("Cleaned %s invalid exchange rate records", affected_rows)
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
        except Exception:
            logger.exception("Error deleting exchange rates by days")
            return False, 0
        return False, 0

    def fill_missing_exchange_rates(self) -> int:
        """Forward-fill missing daily rates from earliest transaction date through today."""
        currencies = self._db.get_currencies_except_usd()
        total_filled = 0

        earliest_transaction_date = self._db.get_earliest_transaction_date()
        if not earliest_transaction_date:
            logger.info("No transactions found; cannot determine start date for filling rates")
            return 0

        start_date_dt = datetime.fromisoformat(earliest_transaction_date)
        start_date = start_date_dt.date()
        end_date = datetime.now(UTC).astimezone().date()

        logger.info("Filling missing exchange rates from %s to %s", start_date, end_date)

        for currency_id, currency_code, _, _ in currencies:
            logger.debug("Processing %s", currency_code)

            query = """
                SELECT date, rate FROM exchange_rates
                WHERE _id_currency = :currency_id
                ORDER BY date ASC
            """
            rows = self._db.get_rows(query, {"currency_id": currency_id})

            if not rows:
                logger.warning("No exchange rates found for %s; skipping", currency_code)
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
                    logger.debug("Filled %s for %s with rate %s", date_str, currency_code, last_known_rate)

                current_date = current_date + timedelta(days=1)

            logger.info("Filled %s missing dates for %s", currency_filled, currency_code)

        self._invalidate_rate_cache()
        logger.info("Total filled: %s exchange rate records", total_filled)
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
        except Exception:
            logger.exception("Error getting currency exchange rate by date")
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
        except Exception:
            logger.exception("Error getting filtered exchange rates")
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

        logger.info("Checking exchange rates from %s to %s (%s days)", date_from, date_to, len(all_dates))

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
                logger.info("%s: %s missing rates", currency_code, len(missing_dates))

                max_sample_size = 10
                sample_size = min(max_sample_size, len(missing_dates))
                sample_dates = missing_dates[:sample_size]
                logger.debug("First %s missing dates for %s: %s", sample_size, currency_code, ", ".join(sample_dates))

                if len(missing_dates) > max_sample_size:
                    logger.debug("... and %s more dates", len(missing_dates) - max_sample_size)

                if len(missing_dates) > 1:
                    logger.debug("Range: from %s to %s", missing_dates[0], missing_dates[-1])

                missing_info[currency_id] = missing_dates
            else:
                logger.debug("%s: all rates present", currency_code)

        if not missing_info:
            logger.info("All exchange rates are present in the specified date range")
        else:
            total_missing = sum(len(dates) for dates in missing_info.values())
            logger.info("TOTAL: %s missing records for %s currencies", total_missing, len(missing_info))

            if missing_info:
                first_currency_id = next(iter(missing_info))
                first_currency_code = next(code for id_item, code, _1, _2 in currencies if id_item == first_currency_id)
                first_missing = missing_info[first_currency_id]

                logger.debug("FULL LIST for %s (%s dates)", first_currency_code, len(first_missing))
                for i, one_date in enumerate(first_missing, 1):
                    logger.debug("%4d. %s", i, one_date)
                    max_dates = 50
                    if i >= max_dates:
                        logger.debug("... and %s more dates", len(first_missing) - max_dates)
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
        except Exception:
            logger.exception("Error checking exchange rates data")
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
                    logger.info(
                        "Exchange rates need update for %s (last: %s, today: %s)",
                        currency_code,
                        last_date,
                        today,
                    )
                    return True

            logger.info("All currencies are up to date (last update: %s)", today)
        except Exception:
            logger.exception("Error checking exchange rates update status")
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
        except Exception:
            logger.exception("Error updating exchange rate")
            return False
        else:
            return ok

    def _invalidate_rate_cache(self) -> None:
        self._exchange_rate_cache.clear()
        self._cache_timestamp = None
