"""
Exchange Rate Update Worker module.

This module contains the ExchangeRateUpdateWorker class that handles
background updates of exchange rates from various data sources.
"""

from datetime import datetime, timedelta

from PySide6.QtCore import QThread, Signal


class ExchangeRateUpdateWorker(QThread):
    """Worker thread for updating and adding exchange rate records from yfinance."""

    # Signals
    progress_updated = Signal(str)  # Progress message
    currency_started = Signal(str)  # Currency being processed
    rates_added = Signal(str, float, str)  # currency_code, rate, date
    finished_success = Signal(int, int)  # Total processed count, total operations
    finished_error = Signal(str)  # Error message

    def __init__(self, db_manager, currencies_to_process):
        super().__init__()
        self.db_manager = db_manager
        self.currencies_to_process = currencies_to_process  # List of (currency_id, code, records_dict)
        self.should_stop = False

    def run(self):
        """Main worker execution."""
        try:
            # Import required libraries
            import pandas as pd
            import yfinance as yf

            total_processed = 0
            total_operations = sum(
                len(records['missing_dates']) + len(records['existing_records'])
                for _, _, records in self.currencies_to_process
            )

            # Clean invalid exchange rates first
            self.progress_updated.emit("🧹 Cleaning invalid exchange rates...")
            cleaned_count = self.db_manager.clean_invalid_exchange_rates()
            if cleaned_count > 0:
                self.progress_updated.emit(f"🧹 Cleaned {cleaned_count} invalid exchange rate records")

            def get_yfinance_data(currency_code: str, date: str) -> float | None:
                """Get exchange rate data from yfinance for a specific date.

                Returns the rate as: 1 CURRENCY = X USD (currency to USD rate)
                For example: 1 RUB = 0.012 USD
                """

                # Primary ticker formats - these should give us CURRENCY/USD rates directly
                primary_tickers = [
                    f"{currency_code}USD=X",  # RUBUSD=X gives RUB to USD rate
                    f"{currency_code}/USD",   # RUB/USD gives RUB to USD rate
                    f"{currency_code}USD",    # RUBUSD gives RUB to USD rate
                ]

                # Inverse ticker formats - these give us USD/CURRENCY rates (need to invert)
                inverse_tickers = [
                    f"USD{currency_code}=X",  # USDRUB=X gives USD to RUB rate (need to invert)
                    f"USD/{currency_code}",   # USD/RUB gives USD to RUB rate (need to invert)
                    f"USD{currency_code}",    # USDRUB gives USD to RUB rate (need to invert)
                ]

                # Special cases for known problematic currencies
                special_cases = {
                    "RUB": {
                        "primary": ["RUBUSD=X", "RUB=X"],
                        "inverse": ["USDRUB=X", "USD/RUB=X"]
                    },
                    "EUR": {
                        "primary": ["EURUSD=X", "EUR=X"],
                        "inverse": ["USDEUR=X", "USD/EUR=X"]
                    },
                    "CNY": {
                        "primary": ["CNYUSD=X", "CNY=X"],
                        "inverse": ["USDCNY=X", "USD/CNY=X"]
                    },
                    "TRY": {
                        "primary": ["TRYUSD=X", "TRY=X"],
                        "inverse": ["USDTRY=X", "USD/TRY=X"]
                    },
                    "VND": {
                        "primary": ["VNDUSD=X", "VND=X"],
                        "inverse": ["USDVND=X", "USD/VND=X"]
                    }
                }

                # Build the ticker list
                if currency_code in special_cases:
                    primary_list = special_cases[currency_code]["primary"]
                    inverse_list = special_cases[currency_code]["inverse"]
                else:
                    primary_list = primary_tickers
                    inverse_list = inverse_tickers

                # Try to get data with a date range
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                start_date = date_obj.strftime("%Y-%m-%d")
                end_date = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")

                # First try primary tickers (no inversion needed)
                for ticker_symbol in primary_list:
                    if self.should_stop:
                        return None

                    try:
                        self.progress_updated.emit(f"🔄 Trying primary ticker: {ticker_symbol}")

                        ticker = yf.Ticker(ticker_symbol)

                        # Try both single date and date range
                        for date_range in [(start_date, start_date), (start_date, end_date)]:
                            try:
                                hist = ticker.history(start=date_range[0], end=date_range[1], interval="1d")

                                if not hist.empty:
                                    close_price = hist.iloc[0]["Close"]

                                    if not pd.isna(close_price) and close_price > 0:
                                        rate = float(close_price)
                                        self.progress_updated.emit(f"✅ Found primary rate with {ticker_symbol}: {rate:.6f} (1 {currency_code} = {rate:.6f} USD)")
                                        return rate

                            except Exception:
                                continue  # Try next date range

                    except Exception as e:
                        if "delisted" not in str(e).lower():
                            self.progress_updated.emit(f"⚠️ Error with primary ticker {ticker_symbol}: {str(e)[:50]}...")
                        continue

                # If primary tickers failed, try inverse tickers (need inversion)
                for ticker_symbol in inverse_list:
                    if self.should_stop:
                        return None

                    try:
                        self.progress_updated.emit(f"🔄 Trying inverse ticker: {ticker_symbol}")

                        ticker = yf.Ticker(ticker_symbol)

                        # Try both single date and date range
                        for date_range in [(start_date, start_date), (start_date, end_date)]:
                            try:
                                hist = ticker.history(start=date_range[0], end=date_range[1], interval="1d")

                                if not hist.empty:
                                    close_price = hist.iloc[0]["Close"]

                                    if not pd.isna(close_price) and close_price > 0:
                                        # This is USD to CURRENCY rate, we need CURRENCY to USD rate
                                        usd_to_currency_rate = float(close_price)
                                        currency_to_usd_rate = 1.0 / usd_to_currency_rate
                                        self.progress_updated.emit(f"✅ Found inverse rate with {ticker_symbol}: {usd_to_currency_rate:.6f} USD/{currency_code}")
                                        self.progress_updated.emit(f"🔄 Inverted to: {currency_to_usd_rate:.6f} (1 {currency_code} = {currency_to_usd_rate:.6f} USD)")
                                        return currency_to_usd_rate

                            except Exception:
                                continue  # Try next date range

                    except Exception as e:
                        if "delisted" not in str(e).lower():
                            self.progress_updated.emit(f"⚠️ Error with inverse ticker {ticker_symbol}: {str(e)[:50]}...")
                        continue

                # If we get here, no ticker worked
                self.progress_updated.emit(f"❌ No valid data found for {currency_code} on {date} with any ticker format")
                return None

            def get_fallback_rate(currency_code: str, date: str) -> float | None:
                """Get fallback rate using the most recent available rate."""
                try:
                    # Get the most recent rate for this currency before the requested date
                    query = """
                        SELECT rate FROM exchange_rates
                        WHERE _id_currency = (SELECT _id FROM currencies WHERE code = :currency_code)
                        AND date < :date
                        ORDER BY date DESC
                        LIMIT 1
                    """

                    rows = self.db_manager.get_rows(query, {"currency_code": currency_code, "date": date})
                    if rows and rows[0][0]:
                        fallback_rate = float(rows[0][0])
                        self.progress_updated.emit(f"📊 Using fallback rate for {currency_code} on {date}: {fallback_rate:.6f}")
                        return fallback_rate

                except Exception as e:
                    self.progress_updated.emit(f"⚠️ Error getting fallback rate for {currency_code}: {e}")

                return None

            # Process each currency
            for currency_id, currency_code, records_dict in self.currencies_to_process:
                if self.should_stop:
                    break

                self.currency_started.emit(currency_code)
                missing_dates = records_dict['missing_dates']
                existing_records = records_dict['existing_records']

                self.progress_updated.emit(
                    f"📈 Processing {currency_code}: {len(missing_dates)} missing + {len(existing_records)} updates"
                )

                currency_processed = 0

                # First, add missing records
                for date_str in missing_dates:
                    if self.should_stop:
                        break

                    try:
                        self.progress_updated.emit(f"➕ Adding {currency_code} rate for {date_str}...")

                        # Get rate from yfinance
                        new_rate = get_yfinance_data(currency_code, date_str)

                        # If yfinance fails, try fallback rate for weekends/holidays
                        if new_rate is None:
                            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                            # Check if it's weekend
                            if date_obj.weekday() >= 5:  # Saturday = 5, Sunday = 6
                                self.progress_updated.emit(f"📅 {date_str} is a weekend, trying fallback rate...")
                                new_rate = get_fallback_rate(currency_code, date_str)

                        if new_rate is not None and new_rate > 0:
                            # Add new record
                            if self.db_manager.add_exchange_rate(currency_id, new_rate, date_str):
                                total_processed += 1
                                currency_processed += 1
                                self.rates_added.emit(currency_code, new_rate, date_str)
                                self.progress_updated.emit(
                                    f"✅ Added {currency_code} rate for {date_str}: {new_rate:.6f}"
                                )
                            else:
                                self.progress_updated.emit(f"❌ Failed to add {currency_code} rate for {date_str}")
                        else:
                            self.progress_updated.emit(
                                f"⚠️ Skipping {currency_code} on {date_str}: no valid rate available"
                            )
                    except Exception as e:
                        self.progress_updated.emit(f"❌ Error adding rate for {currency_code} on {date_str}: {e}")
                        continue

                # Then, update existing records (only for recent dates, not weekends)
                for date_str, old_rate in existing_records:
                    if self.should_stop:
                        break

                    try:
                        # Skip weekend updates to avoid unnecessary API calls
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        if date_obj.weekday() >= 5:  # Weekend
                            self.progress_updated.emit(f"📅 Skipping weekend update for {currency_code} on {date_str}")
                            continue

                        self.progress_updated.emit(f"🔄 Updating {currency_code} rate for {date_str}...")

                        # Get new rate from yfinance
                        new_rate = get_yfinance_data(currency_code, date_str)

                        if new_rate is not None and new_rate > 0:
                            # Only update if the rate is significantly different
                            rate_diff = abs(new_rate - old_rate) / old_rate
                            if rate_diff > 0.001:  # Update if difference > 0.1%
                                if self.db_manager.update_exchange_rate(currency_id, date_str, new_rate):
                                    total_processed += 1
                                    currency_processed += 1
                                    self.rates_added.emit(currency_code, new_rate, date_str)
                                    self.progress_updated.emit(
                                        f"✅ Updated {currency_code} rate for {date_str}: {old_rate:.6f} → {new_rate:.6f}"
                                    )
                                else:
                                    self.progress_updated.emit(f"❌ Failed to update {currency_code} rate for {date_str}")
                            else:
                                self.progress_updated.emit(
                                    f"📊 {currency_code} rate for {date_str} unchanged (diff: {rate_diff:.4f})"
                                )
                        else:
                            self.progress_updated.emit(
                                f"⚠️ Skipping update for {currency_code} on {date_str}: no valid rate from yfinance"
                            )
                    except Exception as e:
                        self.progress_updated.emit(f"❌ Error updating rate for {currency_code} on {date_str}: {e}")
                        continue

                self.progress_updated.emit(f"📊 Processed {currency_processed} operations for {currency_code}")

            # Update last update date
            if not self.should_stop:
                today = datetime.now().strftime("%Y-%m-%d")
                if self.db_manager.set_last_exchange_rates_update_date(today):
                    self.progress_updated.emit(f"📅 Updated last exchange rates update date to {today}")

                self.finished_success.emit(total_processed, total_operations)

        except Exception as e:
            self.finished_error.emit(f"Exchange rate update error: {e}")

    def stop(self):
        """Request worker to stop."""
        self.should_stop = True
