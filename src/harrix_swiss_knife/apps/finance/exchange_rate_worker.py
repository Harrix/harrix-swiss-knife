"""Exchange Rate Update Worker module.

This module contains the ExchangeRateUpdateWorker class that handles
background updates of exchange rates from various data sources.
"""

from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
from PySide6.QtCore import QThread, Signal


class ExchangeRateUpdateWorker(QThread):
    """Worker thread for updating and adding exchange rate records from yfinance.

    Attributes:

    - `progress_updated` (`Signal`): Signal for progress message updates.
    - `currency_started` (`Signal`): Signal emitted when currency processing starts.
    - `rates_added` (`Signal`): Signal emitted when rate is added (currency_code, rate, date).
    - `finished_success` (`Signal`): Signal emitted on success (total_processed, total_operations).
    - `finished_error` (`Signal`): Signal emitted on error with error message.
    - `should_stop` (`bool`): Flag to request worker to stop.

    """

    # Signals
    progress_updated: Signal = Signal(str)  # Progress message
    currency_started: Signal = Signal(str)  # Currency being processed
    rates_added: Signal = Signal(str, float, str)  # currency_code, rate, date
    finished_success: Signal = Signal(int, int)  # Total processed count, total operations
    finished_error: Signal = Signal(str)  # Error message

    db_manager: object
    currencies_to_process: list
    should_stop: bool

    def __init__(self, db_manager: object, currencies_to_process: list) -> None:
        """Initialize the exchange rate update worker.

        Args:

        - `db_manager` (`object`): Database manager instance.
        - `currencies_to_process` (`list`): List of tuples (currency_id, code, records_dict).

        """
        super().__init__()
        self.db_manager = db_manager
        self.currencies_to_process = currencies_to_process  # List of (currency_id, code, records_dict)
        self.should_stop = False

    def run(self) -> None:
        """Execute worker main logic."""
        try:
            total_processed = 0
            total_operations = sum(
                len(records["missing_dates"]) + len(records["existing_records"])
                for _, _, records in self.currencies_to_process
            )

            # Clean invalid exchange rates before processing
            self.progress_updated.emit("🧹 Cleaning invalid exchange rates...")
            cleaned_count = self.db_manager.clean_invalid_exchange_rates()
            if cleaned_count > 0:
                self.progress_updated.emit(f"🧹 Cleaned {cleaned_count} invalid exchange rate records")

            def get_yfinance_data_batch(currency_code: str, dates: list[str], currency_id: int) -> dict[str, float]:
                """Get exchange rate data from yfinance for multiple dates at once.

                Args:

                - `currency_code` (`str`): Currency code (e.g., 'EUR', 'RUB').
                - `dates` (`list[str]`): List of dates in YYYY-MM-DD format.
                - `currency_id` (`int`): Currency ID in database.

                Returns:

                - `dict[str, float]`: Dictionary mapping date to rate (currency to USD rate).

                """
                if not dates:
                    return {}

                # Sort dates to get range
                sorted_dates = sorted(dates)
                start_date = sorted_dates[0]
                end_date = sorted_dates[-1]

                # Add one day to end_date for yfinance API
                end_date_obj = datetime.fromisoformat(end_date)
                end_date_plus = (end_date_obj + timedelta(days=1)).strftime("%Y-%m-%d")

                self.progress_updated.emit(f"📊 Fetching {currency_code} rates from {start_date} to {end_date}...")

                # Check if currency has a saved ticker
                saved_ticker = self.db_manager.get_currency_ticker(currency_id)

                if saved_ticker:
                    # Use saved ticker
                    self.progress_updated.emit(f"🔄 Using saved ticker: {saved_ticker}")
                    ticker_lists = {"primary": [saved_ticker], "inverse": []}
                else:
                    # Define ticker configurations for fallback
                    special_cases = {
                        "RUB": {"primary": ["RUBUSD=X", "RUB=X"], "inverse": ["USDRUB=X", "USD/RUB=X"]},
                        "EUR": {"primary": ["EURUSD=X", "EUR=X"], "inverse": ["USDEUR=X", "USD/EUR=X"]},
                        "CNY": {"primary": ["CNYUSD=X", "CNY=X"], "inverse": ["USDCNY=X", "USD/CNY=X"]},
                        "TRY": {"primary": ["TRYUSD=X", "TRY=X"], "inverse": ["USDTRY=X", "USD/TRY=X"]},
                        "VND": {"primary": ["VNDUSD=X", "VND=X"], "inverse": ["USDVND=X", "USD/VND=X"]},
                    }

                    # Get ticker lists for this currency
                    if currency_code in special_cases:
                        ticker_lists = special_cases[currency_code]
                    else:
                        # Default ticker formats
                        ticker_lists = {
                            "primary": [
                                f"{currency_code}USD=X",
                                f"{currency_code}/USD",
                                f"{currency_code}USD",
                            ],
                            "inverse": [
                                f"USD{currency_code}=X",
                                f"USD/{currency_code}",
                                f"USD{currency_code}",
                            ],
                        }

                primary_list = ticker_lists["primary"]
                inverse_list = ticker_lists["inverse"]

                # Try primary tickers first (no inversion needed)
                for ticker_symbol in primary_list:
                    if self.should_stop:
                        return {}

                    try:
                        self.progress_updated.emit(f"🔄 Trying primary ticker: {ticker_symbol}")
                        ticker = yf.Ticker(ticker_symbol)

                        # Download historical data for the date range
                        hist = ticker.history(start=start_date, end=end_date_plus, interval="1d")

                        if not hist.empty:
                            # Convert to dictionary of date -> rate
                            result = {}
                            for date_idx in hist.index:
                                date_str = date_idx.strftime("%Y-%m-%d")
                                if date_str in dates:  # Only include requested dates
                                    close_price = hist.loc[date_idx, "Close"]
                                    if not pd.isna(close_price) and close_price > 0:
                                        result[date_str] = float(close_price)

                            if result:
                                self.progress_updated.emit(
                                    f"✅ Found {len(result)} rates with {ticker_symbol} (primary)"
                                )
                                # Save successful ticker if not already saved
                                if not saved_ticker:
                                    self.db_manager.update_currency_ticker(currency_id, ticker_symbol)
                                    self.progress_updated.emit(f"💾 Saved successful ticker: {ticker_symbol}")
                                return result

                    except Exception as e:
                        if "delisted" not in str(e).lower():
                            self.progress_updated.emit(f"⚠️ Error with {ticker_symbol}: {str(e)[:50]}...")
                        continue

                # Try inverse tickers (need inversion)
                for ticker_symbol in inverse_list:
                    if self.should_stop:
                        return {}

                    try:
                        self.progress_updated.emit(f"🔄 Trying inverse ticker: {ticker_symbol}")
                        ticker = yf.Ticker(ticker_symbol)

                        # Download historical data for the date range
                        hist = ticker.history(start=start_date, end=end_date_plus, interval="1d")

                        if not hist.empty:
                            # Convert to dictionary of date -> rate (inverted)
                            result = {}
                            for date_idx in hist.index:
                                date_str = date_idx.strftime("%Y-%m-%d")
                                if date_str in dates:  # Only include requested dates
                                    close_price = hist.loc[date_idx, "Close"]
                                    if not pd.isna(close_price) and close_price > 0:
                                        # Invert the rate: USD/CURRENCY -> CURRENCY/USD
                                        result[date_str] = 1.0 / float(close_price)

                            if result:
                                self.progress_updated.emit(
                                    f"✅ Found {len(result)} rates with {ticker_symbol} (inverted)"
                                )
                                # Save successful ticker if not already saved
                                if not saved_ticker:
                                    self.db_manager.update_currency_ticker(currency_id, ticker_symbol)
                                    self.progress_updated.emit(f"💾 Saved successful ticker: {ticker_symbol}")
                                return result

                    except Exception as e:
                        if "delisted" not in str(e).lower():
                            self.progress_updated.emit(f"⚠️ Error with {ticker_symbol}: {str(e)[:50]}...")
                        continue

                # No ticker worked
                self.progress_updated.emit(
                    f"❌ No valid data found for {currency_code} in range {start_date} to {end_date}"
                )
                return {}

            def get_fallback_rate(currency_code: str, date: str) -> float | None:
                """Get fallback rate using the most recent available rate.

                Args:

                - `currency_code` (`str`): Currency code.
                - `date` (`str`): Date in YYYY-MM-DD format.

                Returns:

                - `float | None`: Fallback rate or None if not found.

                """
                try:
                    query = """
                        SELECT rate FROM exchange_rates
                        WHERE _id_currency = (SELECT _id FROM currencies WHERE code = :currency_code)
                        AND date < :date
                        ORDER BY date DESC
                        LIMIT 1
                    """
                    rows = self.db_manager.get_rows(query, {"currency_code": currency_code, "date": date})
                    if rows and rows[0][0]:
                        return float(rows[0][0])
                except Exception as e:
                    self.progress_updated.emit(f"⚠️ Error getting fallback rate: {e}")
                return None

            # Process each currency
            for currency_id, currency_code, records_dict in self.currencies_to_process:
                if self.should_stop:
                    break

                self.currency_started.emit(currency_code)
                missing_dates = records_dict["missing_dates"]
                existing_records = records_dict["existing_records"]

                self.progress_updated.emit(
                    f"📈 Processing {currency_code}: {len(missing_dates)} missing + {len(existing_records)} updates"
                )

                currency_processed = 0

                # Batch process missing dates
                if missing_dates:
                    # Download all missing dates at once
                    rates_dict = get_yfinance_data_batch(currency_code, missing_dates, currency_id)

                    # Prepare batch insert data
                    batch_data = []

                    for date_str in missing_dates:
                        if self.should_stop:
                            break

                        if date_str in rates_dict:
                            # Use downloaded rate
                            new_rate = rates_dict[date_str]
                        else:
                            # Try fallback for weekends/holidays
                            date_obj = datetime.fromisoformat(date_str)
                            weekend_days = (5, 6)  # Saturday=5, Sunday=6
                            if date_obj.weekday() in weekend_days:
                                self.progress_updated.emit(f"📅 {date_str} is weekend, using fallback...")
                                new_rate = get_fallback_rate(currency_code, date_str)
                            else:
                                new_rate = None

                        if new_rate is not None and new_rate > 0:
                            batch_data.append((currency_id, new_rate, date_str))
                            currency_processed += 1
                            self.rates_added.emit(currency_code, new_rate, date_str)
                        else:
                            self.progress_updated.emit(f"⚠️ Skipping {currency_code} on {date_str}: no valid rate")

                    # Batch insert all rates at once
                    if batch_data:
                        success_count = self._batch_insert_rates(batch_data)
                        total_processed += success_count
                        self.progress_updated.emit(f"✅ Batch inserted {success_count} rates for {currency_code}")

                # Update existing records (only recent ones, not weekends)
                if existing_records:
                    # Only update last 7 days of records
                    recent_cutoff = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                    recent_records = [(date, rate) for date, rate in existing_records if date >= recent_cutoff]

                    if recent_records:
                        # Get dates for batch download
                        update_dates = [date for date, _ in recent_records]
                        rates_dict = get_yfinance_data_batch(currency_code, update_dates, currency_id)

                        for date_str, old_rate in recent_records:
                            if self.should_stop:
                                break

                            if date_str in rates_dict:
                                new_rate = rates_dict[date_str]

                                # Only update if significantly different
                                rate_diff = abs(new_rate - old_rate) / old_rate if old_rate != 0 else 1
                                min_rate_diff = 0.001
                                if rate_diff > min_rate_diff and self.db_manager.update_exchange_rate(
                                    currency_id, date_str, new_rate
                                ):
                                    total_processed += 1
                                    currency_processed += 1
                                    self.rates_added.emit(currency_code, new_rate, date_str)
                                    self.progress_updated.emit(
                                        f"✅ Updated {currency_code} rate for {date_str}: "
                                        f"{old_rate:.6f} → {new_rate:.6f}"
                                    )

                self.progress_updated.emit(f"📊 Processed {currency_processed} operations for {currency_code}")

            # Exchange rates update completed
            if not self.should_stop:
                self.finished_success.emit(total_processed, total_operations)

        except Exception as e:
            self.finished_error.emit(f"Exchange rate update error: {e}")

    def stop(self) -> None:
        """Request worker to stop."""
        self.should_stop = True

    def _batch_insert_rates(self, batch_data: list[tuple]) -> int:
        """Batch insert exchange rates.

        Args:

        - `batch_data` (`list[tuple]`): List of tuples (currency_id, rate, date).

        Returns:

        - `int`: Number of successfully inserted records.

        """
        try:
            success_count = 0
            batch_size = 500  # Insert in batches of batch_size

            for i in range(0, len(batch_data), batch_size):
                batch = batch_data[i : i + batch_size]

                # Prepare batch insert query
                for currency_id, rate, date in batch:
                    if self.db_manager.add_exchange_rate(currency_id, rate, date):
                        success_count += 1
        except Exception as e:
            self.progress_updated.emit(f"❌ Batch insert error: {e}")
            return 0
        return success_count
