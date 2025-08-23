"""
Exchange Rate Update Worker module.

This module contains the ExchangeRateUpdateWorker class that handles
background updates of exchange rates from various data sources.
"""

from datetime import datetime, timedelta

from PySide6.QtCore import QThread, Signal


class AutoExchangeRateUpdateWorker(QThread):
    """Worker thread for automatic exchange rate updates on startup."""

    # Signals
    progress_updated = Signal(str)  # Progress message
    finished_success = Signal(int)  # Total processed count
    finished_error = Signal(str)  # Error message

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.should_stop = False

        # Cache for working tickers
        self.working_tickers = {}

    def run(self):
        """Main worker execution for automatic updates."""
        try:
            from datetime import datetime, timedelta

            import pandas as pd
            import yfinance as yf

            self.progress_updated.emit("🔄 Starting automatic exchange rate update...")

            # Get last update date
            last_update_date = self.db_manager.get_last_exchange_rates_update_date()
            if not last_update_date:
                self.progress_updated.emit("⚠️ No last update date found, skipping automatic update")
                self.finished_success.emit(0)
                return

            # Calculate date range for updates
            last_update = datetime.strptime(last_update_date, "%Y-%m-%d").date()
            today = datetime.now().date()

            # Start from the day AFTER last update
            start_date = last_update + timedelta(days=1)

            # DEBUG: Детальное логирование дат
            self.progress_updated.emit(f"🔍 DEBUG: last_update_date from DB = {last_update_date}")
            self.progress_updated.emit(f"🔍 DEBUG: last_update (parsed) = {last_update}")
            self.progress_updated.emit(f"🔍 DEBUG: today = {today}")
            self.progress_updated.emit(f"🔍 DEBUG: start_date (should be day after last_update) = {start_date}")

            # Only update if there's at least one day gap
            if start_date > today:
                self.progress_updated.emit(f"✅ Exchange rates are up to date (last update: {last_update_date})")
                self.finished_success.emit(0)
                return

            self.progress_updated.emit(f"📅 Updating exchange rates from {start_date} to {today}")

            # Get currencies to update (excluding USD)
            currencies = self.db_manager.get_currencies_except_usd()
            if not currencies:
                self.progress_updated.emit("⚠️ No currencies found for update")
                self.finished_success.emit(0)
                return

            total_processed = 0

            # Clean invalid exchange rates first
            self.progress_updated.emit("🧹 Cleaning invalid exchange rates...")
            cleaned_count = self.db_manager.clean_invalid_exchange_rates()
            if cleaned_count > 0:
                self.progress_updated.emit(f"🧹 Cleaned {cleaned_count} invalid records")

            # Generate all dates that need to be processed
            all_missing_dates = []
            current_date = start_date

            self.progress_updated.emit(f"🔍 DEBUG: Generating dates from {start_date} to {today}")

            while current_date <= today:
                date_str = current_date.strftime("%Y-%m-%d")
                all_missing_dates.append(date_str)
                self.progress_updated.emit(f"🔍 DEBUG: Added date to process: {date_str}")
                current_date += timedelta(days=1)

            if not all_missing_dates:
                self.progress_updated.emit("✅ No dates to process")
                self.finished_success.emit(0)
                return

            self.progress_updated.emit(f"📊 Processing {len(all_missing_dates)} dates: {all_missing_dates}")

            # Define ticker functions (keeping existing implementation)
            def get_working_ticker_for_currency(currency_code: str) -> tuple[str, bool] | None:
                """Find and cache the working ticker for a currency."""
                if currency_code in self.working_tickers:
                    return self.working_tickers[currency_code]

                # Predefined ticker formats for common currencies
                predefined_tickers = {
                    "RUB": {"primary": ["RUBUSD=X", "RUB=X"], "inverse": ["USDRUB=X", "USD/RUB=X"]},
                    "EUR": {"primary": ["EURUSD=X", "EUR=X"], "inverse": ["USDEUR=X", "USD/EUR=X"]},
                    "GBP": {"primary": ["GBPUSD=X", "GBP=X"], "inverse": ["USDGBP=X", "USD/GBP=X"]},
                    "JPY": {"primary": ["JPYUSD=X", "JPY=X"], "inverse": ["USDJPY=X", "USD/JPY=X"]},
                    "CNY": {"primary": ["CNYUSD=X", "CNY=X"], "inverse": ["USDCNY=X", "USD/CNY=X"]},
                    "CHF": {"primary": ["CHFUSD=X", "CHF=X"], "inverse": ["USDCHF=X", "USD/CHF=X"]},
                    "CAD": {"primary": ["CADUSD=X", "CAD=X"], "inverse": ["USDCAD=X", "USD/CAD=X"]},
                    "AUD": {"primary": ["AUDUSD=X", "AUD=X"], "inverse": ["USDAUD=X", "USD/AUD=X"]},
                    "NZD": {"primary": ["NZDUSD=X", "NZD=X"], "inverse": ["USDNZD=X", "USD/NZD=X"]},
                    "SEK": {"primary": ["SEKUSD=X", "SEK=X"], "inverse": ["USDSEK=X", "USD/SEK=X"]},
                    "NOK": {"primary": ["NOKUSD=X", "NOK=X"], "inverse": ["USDNOK=X", "USD/NOK=X"]},
                    "DKK": {"primary": ["DKKUSD=X", "DKK=X"], "inverse": ["USDDKK=X", "USD/DKK=X"]},
                }

                # Get predefined tickers or generate generic ones
                if currency_code in predefined_tickers:
                    primary_tickers = predefined_tickers[currency_code]["primary"]
                    inverse_tickers = predefined_tickers[currency_code]["inverse"]
                else:
                    primary_tickers = [f"{currency_code}USD=X", f"{currency_code}=X"]
                    inverse_tickers = [f"USD{currency_code}=X", f"USD/{currency_code}=X"]

                self.progress_updated.emit(f"🔍 Finding working ticker for {currency_code}...")

                # Test a recent date to find working ticker
                test_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                test_start = test_date
                test_end = (datetime.strptime(test_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

                # Try primary tickers first
                for ticker_symbol in primary_tickers:
                    if self.should_stop:
                        return None

                    try:
                        ticker = yf.Ticker(ticker_symbol)
                        hist = ticker.history(start=test_start, end=test_end, interval="1d")

                        if not hist.empty and not pd.isna(hist.iloc[0]["Close"]) and hist.iloc[0]["Close"] > 0:
                            self.progress_updated.emit(f"✅ Found working ticker for {currency_code}: {ticker_symbol}")
                            result = (ticker_symbol, False)
                            self.working_tickers[currency_code] = result
                            return result

                    except Exception:
                        continue

                # Try inverse tickers if primary failed
                for ticker_symbol in inverse_tickers:
                    if self.should_stop:
                        return None

                    try:
                        ticker = yf.Ticker(ticker_symbol)
                        hist = ticker.history(start=test_start, end=test_end, interval="1d")

                        if not hist.empty and not pd.isna(hist.iloc[0]["Close"]) and hist.iloc[0]["Close"] > 0:
                            self.progress_updated.emit(
                                f"✅ Found working inverse ticker for {currency_code}: {ticker_symbol}"
                            )
                            result = (ticker_symbol, True)
                            self.working_tickers[currency_code] = result
                            return result

                    except Exception:
                        continue

                self.progress_updated.emit(f"❌ No working ticker found for {currency_code}")
                self.working_tickers[currency_code] = None
                return None

            def get_bulk_exchange_rates(currency_code: str, dates: list[str]) -> dict[str, float]:
                """Get exchange rates for multiple dates at once."""
                if not dates:
                    return {}

                ticker_info = get_working_ticker_for_currency(currency_code)
                if not ticker_info:
                    return {}

                ticker_symbol, is_inverse = ticker_info

                try:
                    start_date_str = min(dates)
                    end_date_str = max(dates)

                    start_dt = datetime.strptime(start_date_str, "%Y-%m-%d") - timedelta(days=2)
                    end_dt = datetime.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=2)

                    start_str = start_dt.strftime("%Y-%m-%d")
                    end_str = end_dt.strftime("%Y-%m-%d")

                    self.progress_updated.emit(
                        f"📥 Downloading data for {currency_code} from {start_date_str} to {end_date_str}"
                    )

                    ticker = yf.Ticker(ticker_symbol)
                    hist = ticker.history(start=start_str, end=end_str, interval="1d")

                    if hist.empty:
                        self.progress_updated.emit(f"⚠️ No data received for {currency_code}")
                        return {}

                    rates = {}
                    for date_str in dates:
                        if self.should_stop:
                            break

                        try:
                            target_date_naive = datetime.strptime(date_str, "%Y-%m-%d")
                            target_date = pd.Timestamp(target_date_naive)

                            hist_index_tz_naive = hist.index
                            if hasattr(hist_index_tz_naive, "tz") and hist_index_tz_naive.tz is not None:
                                hist_index_tz_naive = hist_index_tz_naive.tz_localize(None)

                            if target_date in hist_index_tz_naive:
                                close_price = hist.loc[hist_index_tz_naive == target_date]["Close"].iloc[0]
                            else:
                                if len(hist_index_tz_naive) > 0:
                                    date_diffs = abs(hist_index_tz_naive - target_date)
                                    closest_idx = date_diffs.argmin()
                                    close_price = hist.iloc[closest_idx]["Close"]
                                else:
                                    continue

                            if pd.isna(close_price) or close_price <= 0:
                                continue

                            rate = float(close_price)

                            if is_inverse:
                                currency_to_usd_rate = 1.0 / rate
                                rates[date_str] = currency_to_usd_rate
                            else:
                                rates[date_str] = rate

                        except Exception as e:
                            self.progress_updated.emit(f"⚠️ Error processing {date_str} for {currency_code}: {e}")
                            continue

                    self.progress_updated.emit(f"✅ Got {len(rates)} rates for {currency_code}")
                    return rates

                except Exception as e:
                    self.progress_updated.emit(f"❌ Bulk download failed for {currency_code}: {e}")
                    return {}

            # Process each currency
            for currency_id, currency_code, _, _ in currencies:
                if self.should_stop:
                    break

                self.progress_updated.emit(f"📈 Processing {currency_code}...")

                # Check which dates are actually missing for this currency
                missing_dates = []
                for date_str in all_missing_dates:
                    exists = self.db_manager.check_exchange_rate_exists(currency_id, date_str)
                    self.progress_updated.emit(f"🔍 DEBUG: {currency_code} {date_str} exists = {exists}")
                    if not exists:
                        missing_dates.append(date_str)

                if not missing_dates:
                    self.progress_updated.emit(f"✅ {currency_code}: No missing dates")
                    continue

                self.progress_updated.emit(
                    f"📊 {currency_code}: Found {len(missing_dates)} missing dates: {missing_dates}"
                )

                # Get bulk rates
                bulk_rates = get_bulk_exchange_rates(currency_code, missing_dates)

                # Prepare batch data for insertion
                batch_insert_data = []
                for date_str in missing_dates:
                    if self.should_stop:
                        break

                    new_rate = bulk_rates.get(date_str)

                    # Try fallback rate for weekends/holidays
                    if new_rate is None:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        if date_obj.weekday() >= 5:  # Weekend
                            # Get most recent rate
                            query = """
                                SELECT rate FROM exchange_rates
                                WHERE _id_currency = :currency_id AND date < :date
                                ORDER BY date DESC LIMIT 1
                            """
                            rows = self.db_manager.get_rows(query, {"currency_id": currency_id, "date": date_str})
                            if rows and rows[0][0]:
                                new_rate = float(rows[0][0])
                                self.progress_updated.emit(
                                    f"📊 Using fallback rate for {currency_code} on {date_str}: {new_rate:.6f}"
                                )

                    if new_rate is not None and new_rate > 0:
                        batch_insert_data.append((currency_id, new_rate, date_str))
                        self.progress_updated.emit(
                            f"✅ Prepared rate for {currency_code} on {date_str}: {new_rate:.6f}"
                        )
                    else:
                        self.progress_updated.emit(f"⚠️ No rate found for {currency_code} on {date_str}")

                # Execute batch insert
                if batch_insert_data:
                    self.progress_updated.emit(f"💾 Inserting {len(batch_insert_data)} rates for {currency_code}...")
                    inserted_count = self.db_manager.add_exchange_rates_batch(batch_insert_data)
                    total_processed += inserted_count
                    self.progress_updated.emit(
                        f"✅ {currency_code}: Inserted {inserted_count}/{len(batch_insert_data)} rates"
                    )

            # Fill missing rates with previous rates (gap filling) - only for the processed date range
            if not self.should_stop and total_processed > 0:
                self.progress_updated.emit("🔄 Filling remaining gaps with previous values...")
                filled_count = self._fill_missing_rates_from_date(start_date, today)
                if filled_count > 0:
                    total_processed += filled_count
                    self.progress_updated.emit(f"✅ Filled {filled_count} missing rates")

            # Update last update date ONLY if we processed something successfully
            if not self.should_stop and total_processed > 0:
                today_str = today.strftime("%Y-%m-%d")
                if self.db_manager.set_last_exchange_rates_update_date(today_str):
                    self.progress_updated.emit(f"📅 Updated last update date to {today_str}")

            self.finished_success.emit(total_processed)

        except Exception as e:
            error_msg = f"Automatic exchange rate update error: {e}"
            self.progress_updated.emit(f"❌ {error_msg}")
            self.finished_error.emit(error_msg)

    def stop(self):
        """Request worker to stop."""
        self.should_stop = True

    def _fill_missing_rates_from_date(self, start_date, end_date) -> int:
        """Fill missing exchange rates from start_date to end_date."""
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        self.progress_updated.emit(f"🔄 Filling gaps from {start_date_str} to {end_date_str}")

        # Fill missing exchange rates after processing
        if not self.should_stop:
            self.progress_updated.emit("🔄 Filling missing exchange rates...")
            filled_count = self.db_manager.fill_missing_exchange_rates()
            if filled_count > 0:
                total_processed += filled_count
                self.progress_updated.emit(f"✅ Filled {filled_count} missing rates")

        return filled_count


class ExchangeRateAnalysisWorker(QThread):
    """Worker thread for analyzing missing exchange rate records."""

    # Signals
    progress_updated = Signal(str)  # Progress message
    currency_analyzed = Signal(str, int, int)  # currency_code, missing_count, existing_count
    finished_success = Signal(list)  # List of (currency_id, currency_code, records_dict)
    finished_error = Signal(str)  # Error message

    def __init__(self, db_manager, currencies, earliest_date, today):
        super().__init__()
        self.db_manager = db_manager
        self.currencies = currencies
        self.earliest_date = earliest_date
        self.today = today
        self.should_stop = False

    def run(self):
        """Main worker execution for analysis."""
        try:
            currencies_to_process = []
            total_currencies = len(self.currencies)

            self.progress_updated.emit(f"🔍 Analyzing {total_currencies} currencies for missing exchange rates...")

            for index, (currency_id, currency_code, currency_name, currency_symbol) in enumerate(self.currencies):
                if self.should_stop:
                    break

                self.progress_updated.emit(f"🔍 Analyzing {currency_code} ({index + 1}/{total_currencies})...")

                # Get ALL missing dates in the entire range
                missing_dates = []

                # Check each date in the range from earliest transaction to today
                current_date = self.earliest_date
                dates_checked = 0

                while current_date <= self.today:
                    if self.should_stop:
                        break

                    date_str = current_date.strftime("%Y-%m-%d")

                    if not self.db_manager.check_exchange_rate_exists(currency_id, date_str):
                        missing_dates.append(date_str)

                    current_date += timedelta(days=1)
                    dates_checked += 1

                    # Update progress every 100 dates
                    if dates_checked % 100 == 0:
                        self.progress_updated.emit(
                            f"🔍 {currency_code}: Checked {dates_checked} dates, found {len(missing_dates)} missing..."
                        )

                if self.should_stop:
                    break

                # Get the last two existing records for updates
                last_two_records = self.db_manager.get_last_two_exchange_rate_records(currency_id)

                # Emit analysis result for this currency
                self.currency_analyzed.emit(currency_code, len(missing_dates), len(last_two_records))

                # Only add to processing list if there are missing dates or records to update
                if missing_dates or last_two_records:
                    records_to_process = {"missing_dates": missing_dates, "existing_records": last_two_records}
                    currencies_to_process.append((currency_id, currency_code, records_to_process))

                    self.progress_updated.emit(
                        f"📊 {currency_code}: {len(missing_dates)} missing + {len(last_two_records)} to update"
                    )
                else:
                    self.progress_updated.emit(f"✅ {currency_code}: All records up to date")

            if not self.should_stop:
                self.finished_success.emit(currencies_to_process)

        except Exception as e:
            self.finished_error.emit(f"Analysis error: {e}")

    def stop(self):
        """Request worker to stop."""
        self.should_stop = True


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

        # Cache for working tickers - once we find a working ticker for a currency, we use it
        self.working_tickers = {}

    def run(self):
        """Main worker execution."""
        try:
            # Import required libraries
            import pandas as pd
            import yfinance as yf

            total_processed = 0
            total_operations = sum(
                len(records["missing_dates"]) + len(records["existing_records"])
                for _, _, records in self.currencies_to_process
            )

            # Clean invalid exchange rates first
            self.progress_updated.emit("🧹 Cleaning invalid exchange rates...")
            cleaned_count = self.db_manager.clean_invalid_exchange_rates()
            if cleaned_count > 0:
                self.progress_updated.emit(f"🧹 Cleaned {cleaned_count} invalid exchange rate records")

            def get_working_ticker_for_currency(currency_code: str) -> tuple[str, bool] | None:
                """Find and cache the working ticker for a currency.

                Returns:
                    Tuple of (ticker_symbol, is_inverse) or None if no working ticker found
                """
                if currency_code in self.working_tickers:
                    return self.working_tickers[currency_code]

                # Predefined ticker formats for common currencies
                predefined_tickers = {
                    "RUB": {"primary": ["RUBUSD=X", "RUB=X"], "inverse": ["USDRUB=X", "USD/RUB=X"]},
                    "EUR": {"primary": ["EURUSD=X", "EUR=X"], "inverse": ["USDEUR=X", "USD/EUR=X"]},
                    "GBP": {"primary": ["GBPUSD=X", "GBP=X"], "inverse": ["USDGBP=X", "USD/GBP=X"]},
                    "JPY": {"primary": ["JPYUSD=X", "JPY=X"], "inverse": ["USDJPY=X", "USD/JPY=X"]},
                    "CNY": {"primary": ["CNYUSD=X", "CNY=X"], "inverse": ["USDCNY=X", "USD/CNY=X"]},
                    "CHF": {"primary": ["CHFUSD=X", "CHF=X"], "inverse": ["USDCHF=X", "USD/CHF=X"]},
                    "CAD": {"primary": ["CADUSD=X", "CAD=X"], "inverse": ["USDCAD=X", "USD/CAD=X"]},
                    "AUD": {"primary": ["AUDUSD=X", "AUD=X"], "inverse": ["USDAUD=X", "USD/AUD=X"]},
                    "NZD": {"primary": ["NZDUSD=X", "NZD=X"], "inverse": ["USDNZD=X", "USD/NZD=X"]},
                    "SEK": {"primary": ["SEKUSD=X", "SEK=X"], "inverse": ["USDSEK=X", "USD/SEK=X"]},
                    "NOK": {"primary": ["NOKUSD=X", "NOK=X"], "inverse": ["USDNOK=X", "USD/NOK=X"]},
                    "DKK": {"primary": ["DKKUSD=X", "DKK=X"], "inverse": ["USDDKK=X", "USD/DKK=X"]},
                }

                # Get predefined tickers or generate generic ones
                if currency_code in predefined_tickers:
                    primary_tickers = predefined_tickers[currency_code]["primary"]
                    inverse_tickers = predefined_tickers[currency_code]["inverse"]
                else:
                    # Generate generic ticker formats
                    primary_tickers = [f"{currency_code}USD=X", f"{currency_code}=X"]
                    inverse_tickers = [f"USD{currency_code}=X", f"USD/{currency_code}=X"]

                self.progress_updated.emit(f"🔍 Finding working ticker for {currency_code}...")

                # Test a recent date to find working ticker
                test_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                test_start = test_date
                test_end = (datetime.strptime(test_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

                # Try primary tickers first (no inversion needed)
                for ticker_symbol in primary_tickers:
                    if self.should_stop:
                        return None

                    try:
                        self.progress_updated.emit(f"🔄 Testing primary ticker: {ticker_symbol}")
                        ticker = yf.Ticker(ticker_symbol)
                        hist = ticker.history(start=test_start, end=test_end, interval="1d")

                        if not hist.empty and not pd.isna(hist.iloc[0]["Close"]) and hist.iloc[0]["Close"] > 0:
                            self.progress_updated.emit(
                                f"✅ Found working primary ticker for {currency_code}: {ticker_symbol}"
                            )
                            result = (ticker_symbol, False)  # False = not inverse
                            self.working_tickers[currency_code] = result
                            return result

                    except Exception as e:
                        error_msg = str(e).lower()
                        if "delisted" not in error_msg and "not found" not in error_msg:
                            self.progress_updated.emit(f"⚠️ Error testing {ticker_symbol}: {str(e)[:50]}...")

                # Try inverse tickers if primary failed
                for ticker_symbol in inverse_tickers:
                    if self.should_stop:
                        return None

                    try:
                        self.progress_updated.emit(f"🔄 Testing inverse ticker: {ticker_symbol}")
                        ticker = yf.Ticker(ticker_symbol)
                        hist = ticker.history(start=test_start, end=test_end, interval="1d")

                        if not hist.empty and not pd.isna(hist.iloc[0]["Close"]) and hist.iloc[0]["Close"] > 0:
                            self.progress_updated.emit(
                                f"✅ Found working inverse ticker for {currency_code}: {ticker_symbol}"
                            )
                            result = (ticker_symbol, True)  # True = inverse
                            self.working_tickers[currency_code] = result
                            return result

                    except Exception as e:
                        error_msg = str(e).lower()
                        if "delisted" not in error_msg and "not found" not in error_msg:
                            self.progress_updated.emit(f"⚠️ Error testing {ticker_symbol}: {str(e)[:50]}...")

                # No working ticker found
                self.progress_updated.emit(f"❌ No working ticker found for {currency_code}")
                self.working_tickers[currency_code] = None
                return None

            def get_bulk_exchange_rates(currency_code: str, dates: list[str]) -> dict[str, float]:
                """Get exchange rates for multiple dates at once."""
                if not dates:
                    return {}

                # Get working ticker for this currency
                ticker_info = get_working_ticker_for_currency(currency_code)
                if not ticker_info:
                    return {}

                ticker_symbol, is_inverse = ticker_info

                try:
                    # Get date range for bulk download
                    start_date = min(dates)
                    end_date = max(dates)

                    # Add buffer days to ensure we get all data
                    start_dt = datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days=2)
                    end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=2)

                    start_str = start_dt.strftime("%Y-%m-%d")
                    end_str = end_dt.strftime("%Y-%m-%d")

                    self.progress_updated.emit(
                        f"📥 Downloading bulk data for {currency_code} from {start_date} to {end_date}..."
                    )

                    ticker = yf.Ticker(ticker_symbol)
                    hist = ticker.history(start=start_str, end=end_str, interval="1d")

                    if hist.empty:
                        self.progress_updated.emit(f"⚠️ No bulk data received for {currency_code}")
                        return {}

                    # Process the bulk data
                    rates = {}
                    for date_str in dates:
                        if self.should_stop:
                            break

                        try:
                            # Создаем timezone-naive datetime для сравнения
                            target_date_naive = datetime.strptime(date_str, "%Y-%m-%d")
                            target_date = pd.Timestamp(target_date_naive)

                            # Убираем timezone информацию из индекса если она есть
                            hist_index_tz_naive = hist.index
                            if hasattr(hist_index_tz_naive, "tz") and hist_index_tz_naive.tz is not None:
                                hist_index_tz_naive = hist_index_tz_naive.tz_localize(None)

                            # Try to find exact date first
                            if target_date in hist_index_tz_naive:
                                close_price = hist.loc[hist_index_tz_naive == target_date]["Close"].iloc[0]
                            else:
                                # Find closest date
                                if len(hist_index_tz_naive) > 0:
                                    # Находим ближайшую дату
                                    date_diffs = abs(hist_index_tz_naive - target_date)
                                    closest_idx = date_diffs.argmin()
                                    closest_date = hist_index_tz_naive[closest_idx]
                                    close_price = hist.iloc[closest_idx]["Close"]
                                else:
                                    continue

                            if pd.isna(close_price) or close_price <= 0:
                                continue

                            rate = float(close_price)

                            if is_inverse:
                                # This is USD to CURRENCY rate, we need CURRENCY to USD rate
                                currency_to_usd_rate = 1.0 / rate
                                rates[date_str] = currency_to_usd_rate
                            else:
                                rates[date_str] = rate

                        except Exception as e:
                            self.progress_updated.emit(f"⚠️ Error processing {date_str} for {currency_code}: {e}")
                            continue

                    self.progress_updated.emit(f"✅ Got {len(rates)} rates for {currency_code} from bulk download")
                    return rates

                except Exception as e:
                    self.progress_updated.emit(f"❌ Bulk download failed for {currency_code}: {e}")
                    return {}

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
                        self.progress_updated.emit(
                            f"📊 Using fallback rate for {currency_code} on {date}: {fallback_rate:.6f}"
                        )
                        return fallback_rate

                except Exception as e:
                    self.progress_updated.emit(f"⚠️ Error getting fallback rate for {currency_code}: {e}")

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

                # Process missing dates in bulk with batch insert
                if missing_dates:
                    self.progress_updated.emit(
                        f"📥 Bulk downloading {len(missing_dates)} missing rates for {currency_code}..."
                    )

                    # Get bulk rates for all missing dates
                    bulk_rates = get_bulk_exchange_rates(currency_code, missing_dates)

                    # Prepare batch data for insertion
                    batch_insert_data = []

                    for date_str in missing_dates:
                        if self.should_stop:
                            break

                        try:
                            new_rate = bulk_rates.get(date_str)

                            # If bulk download failed for this date, try fallback rate for weekends/holidays
                            if new_rate is None:
                                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                                # Check if it's weekend
                                if date_obj.weekday() >= 5:  # Saturday = 5, Sunday = 6
                                    self.progress_updated.emit(f"📅 {date_str} is a weekend, trying fallback rate...")
                                    new_rate = get_fallback_rate(currency_code, date_str)

                            if new_rate is not None and new_rate > 0:
                                # Add to batch data instead of individual insert
                                batch_insert_data.append((currency_id, new_rate, date_str))
                            else:
                                self.progress_updated.emit(
                                    f"⚠️ Skipping {currency_code} on {date_str}: no valid rate available"
                                )
                        except Exception as e:
                            self.progress_updated.emit(
                                f"❌ Error preparing rate for {currency_code} on {date_str}: {e}"
                            )
                            continue

                    # Execute batch insert
                    if batch_insert_data:
                        self.progress_updated.emit(
                            f"💾 Batch inserting {len(batch_insert_data)} rates for {currency_code}..."
                        )

                        # Use batch insert method (need to add this to DatabaseManager)
                        inserted_count = self.db_manager.add_exchange_rates_batch(batch_insert_data)
                        total_processed += inserted_count
                        currency_processed += inserted_count

                        self.progress_updated.emit(
                            f"✅ Batch inserted {inserted_count}/{len(batch_insert_data)} rates for {currency_code}"
                        )

                        # Emit signals for successfully inserted rates (for UI updates)
                        for i, (currency_id_item, rate, date_str) in enumerate(batch_insert_data):
                            if i < inserted_count:  # Only emit for successfully inserted records
                                self.rates_added.emit(currency_code, rate, date_str)

                # Process existing records for updates (keep individual updates for precision)
                if existing_records:
                    update_dates = [record[0] for record in existing_records]
                    self.progress_updated.emit(
                        f"📥 Bulk downloading {len(update_dates)} rates for updates for {currency_code}..."
                    )

                    # Get bulk rates for update dates
                    bulk_rates = get_bulk_exchange_rates(currency_code, update_dates)

                    for date_str, old_rate in existing_records:
                        if self.should_stop:
                            break

                        try:
                            # Skip weekend updates to avoid unnecessary processing
                            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                            if date_obj.weekday() >= 5:  # Weekend
                                self.progress_updated.emit(
                                    f"📅 Skipping weekend update for {currency_code} on {date_str}"
                                )
                                continue

                            # Get new rate from bulk download
                            new_rate = bulk_rates.get(date_str)

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
                                        self.progress_updated.emit(
                                            f"❌ Failed to update {currency_code} rate for {date_str}"
                                        )
                                else:
                                    self.progress_updated.emit(
                                        f"📊 {currency_code} rate for {date_str} unchanged (diff: {rate_diff:.4f})"
                                    )
                            else:
                                self.progress_updated.emit(
                                    f"⚠️ Skipping update for {currency_code} on {date_str}: no valid rate from bulk download"
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
