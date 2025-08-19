"""
Exchange Rate Update Worker module.

This module contains the ExchangeRateUpdateWorker class that handles
background updates of exchange rates from various data sources.
"""

from datetime import datetime, timedelta

from PySide6.QtCore import QThread, Signal


class ExchangeRateUpdateWorker(QThread):
    """Worker thread for updating exchange rates."""

    # Signals
    progress_updated = Signal(str)  # Progress message
    currency_started = Signal(str)  # Currency being processed
    rates_added = Signal(str, float, str)  # currency_code, rate, date
    finished_success = Signal(int, int)  # Downloaded updates, filled updates
    finished_error = Signal(str)  # Error message

    def __init__(self, db_manager, currencies_to_update, start_date, end_date):
        super().__init__()
        self.db_manager = db_manager
        self.currencies_to_update = currencies_to_update  # List of (currency_id, code, start_date, end_date)
        self.start_date = start_date
        self.end_date = end_date
        self.should_stop = False

    def run(self):
        """Main worker execution."""
        try:
            # Import required libraries
            import pandas as pd
            import requests
            import yfinance as yf

            total_downloaded = 0

            # Clean invalid exchange rates first
            self.progress_updated.emit("🧹 Cleaning invalid exchange rates...")
            cleaned_count = self.db_manager.clean_invalid_exchange_rates()
            if cleaned_count > 0:
                self.progress_updated.emit(f"🧹 Cleaned {cleaned_count} invalid exchange rate records")

            # Methods for getting exchange rates from different sources
            def get_exchangerate_api_data(currency: str, start_date: str, end_date: str) -> dict:
                """Get historical exchange rates from ExchangeRate-API."""
                rates_data = {}
                try:
                    # ExchangeRate-API provides historical data
                    base_url = "https://api.exchangerate-api.com/v4/history"

                    # Get data for date range (API has limitations, so we'll get recent data)
                    current_date = datetime.now().date()
                    url = f"{base_url}/USD/{current_date.strftime('%Y-%m-%d')}"

                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if currency in data.get("rates", {}):
                            # For USD base, we get XXX/USD rate (how many XXX for 1 USD)
                            # Store this directly as USD→currency rate (more intuitive)
                            usd_to_currency_rate = data["rates"][currency]

                            # For simplicity, use the same rate for all dates in range
                            current = datetime.strptime(start_date, "%Y-%m-%d").date()
                            end = datetime.strptime(end_date, "%Y-%m-%d").date()

                            while current <= end:
                                rates_data[current.strftime("%Y-%m-%d")] = usd_to_currency_rate
                                current += timedelta(days=1)

                            self.progress_updated.emit(
                                f"📊 Got USD/{currency} rate from ExchangeRate-API: {usd_to_currency_rate:.6f}"
                            )
                        else:
                            self.progress_updated.emit(f"⚠️ Currency {currency} not found in ExchangeRate-API")
                    else:
                        self.progress_updated.emit(f"❌ ExchangeRate-API error: {response.status_code}")

                except Exception as e:
                    self.progress_updated.emit(f"❌ Error with ExchangeRate-API for {currency}: {e}")

                return rates_data

            def get_yfinance_data(currency_code: str, start_date, end_date) -> dict:
                """Get exchange rate data from yfinance."""
                rates_data = {}
                ticker_symbol = f"{currency_code}USD=X"

                # Alternative ticker formats for problematic currencies
                alternative_tickers = {
                    "VND": ["USD/VND=X", "USDVND=X"],  # Vietnamese Dong alternatives
                    "TRY": ["USD/TRY=X", "USDTRY=X"],  # Turkish Lira alternatives
                    "RUB": ["USD/RUB=X", "USDRUB=X"],  # Russian Ruble alternatives
                }

                try:
                    # Download historical data
                    ticker = yf.Ticker(ticker_symbol)
                    hist = ticker.history(start=start_date, end=end_date + timedelta(days=1))

                    # If no data found, try alternative ticker formats
                    if hist.empty and currency_code in alternative_tickers:
                        self.progress_updated.emit(f"⚠️ No data found for {ticker_symbol}, trying alternatives...")

                        for alt_ticker in alternative_tickers[currency_code]:
                            if self.should_stop:
                                return {}
                            self.progress_updated.emit(f"🔄 Trying alternative ticker: {alt_ticker}")
                            ticker = yf.Ticker(alt_ticker)
                            hist = ticker.history(start=start_date, end=end_date + timedelta(days=1))

                            if not hist.empty:
                                self.progress_updated.emit(f"✅ Found data with alternative ticker: {alt_ticker}")
                                ticker_symbol = alt_ticker  # Update for logging

                                # For inverse rates (USD/XXX), we need to invert the values
                                if alt_ticker.startswith("USD/") or alt_ticker.startswith("USD"):
                                    self.progress_updated.emit(f"🔄 Inverting rates for {alt_ticker}")
                                    hist = hist.copy()
                                    for col in ["Open", "High", "Low", "Close"]:
                                        if col in hist.columns:
                                            hist[col] = 1.0 / hist[col]
                                break

                    if hist.empty:
                        self.progress_updated.emit(
                            f"⚠️ No data found for {currency_code} with any yfinance ticker format"
                        )
                        return {}

                    self.progress_updated.emit(f"📊 Processing {len(hist)} days of yfinance data for {ticker_symbol}")

                    # Process each day
                    for date_idx, row in hist.iterrows():
                        if self.should_stop:
                            return {}
                        date_str = date_idx.strftime("%Y-%m-%d")
                        close_price = row["Close"]

                        if not pd.isna(close_price) and close_price > 0:
                            rates_data[date_str] = float(close_price)
                        else:
                            self.progress_updated.emit(
                                f"⚠️ Invalid yfinance price for {currency_code} on {date_str}: {close_price}"
                            )

                except Exception as e:
                    self.progress_updated.emit(f"❌ Error with yfinance for {currency_code}: {e}")

                return rates_data

            # Process each currency that needs updates
            for currency_id, currency_code, currency_start_date, currency_end_date in self.currencies_to_update:
                if self.should_stop:
                    break

                self.currency_started.emit(currency_code)
                self.progress_updated.emit(
                    f"📈 Updating {currency_code} from {currency_start_date} to {currency_end_date}"
                )

                success = False
                rates_data = {}

                # Try multiple data sources in order of preference
                data_sources = [
                    ("yfinance", lambda: get_yfinance_data(currency_code, currency_start_date, currency_end_date)),
                    (
                        "ExchangeRate-API",
                        lambda: get_exchangerate_api_data(
                            currency_code,
                            currency_start_date.strftime("%Y-%m-%d"),
                            currency_end_date.strftime("%Y-%m-%d"),
                        ),
                    ),
                ]

                for source_name, get_data_func in data_sources:
                    if self.should_stop:
                        break
                    try:
                        self.progress_updated.emit(f"🔄 Trying {source_name} for {currency_code}...")
                        rates_data = get_data_func()

                        if rates_data:
                            self.progress_updated.emit(
                                f"✅ Successfully got {len(rates_data)} rates from {source_name} for {currency_code}"
                            )
                            success = True
                            break
                        else:
                            self.progress_updated.emit(f"⚠️ No data from {source_name} for {currency_code}")

                    except Exception as e:
                        self.progress_updated.emit(f"❌ Error with {source_name} for {currency_code}: {e}")
                        continue

                if not success or not rates_data:
                    self.progress_updated.emit(
                        f"❌ Failed to get exchange rate data for {currency_code} from any source"
                    )
                    continue

                # Save the rates to database
                self.progress_updated.emit(f"💾 Saving {len(rates_data)} exchange rates for {currency_code}")
                currency_downloaded = 0

                for date_str, rate in rates_data.items():
                    if self.should_stop:
                        break
                    try:
                        # Check if exchange rate already exists
                        if not self.db_manager.check_exchange_rate_exists(currency_id, date_str):
                            if rate is not None and rate > 0:
                                if self.db_manager.add_exchange_rate(currency_id, rate, date_str):
                                    total_downloaded += 1
                                    currency_downloaded += 1
                                    self.rates_added.emit(currency_code, rate, date_str)
                                else:
                                    self.progress_updated.emit(
                                        f"❌ Failed to add {currency_code}/USD rate for {date_str}"
                                    )
                            else:
                                self.progress_updated.emit(
                                    f"⚠️ Skipping invalid rate for {currency_code} on {date_str}: {rate}"
                                )
                    except Exception as e:
                        self.progress_updated.emit(f"❌ Error saving rate for {currency_code} on {date_str}: {e}")
                        continue

                self.progress_updated.emit(f"📊 Downloaded {currency_downloaded} new rates for {currency_code}")

            # Fill missing exchange rates
            if not self.should_stop:
                self.progress_updated.emit("🔄 Filling missing exchange rates...")
                filled_count = self.db_manager.fill_missing_exchange_rates()
                self.progress_updated.emit(f"✅ Filled {filled_count} missing exchange rate records")

                # Update last update date
                today = datetime.now().strftime("%Y-%m-%d")
                if self.db_manager.set_last_exchange_rates_update_date(today):
                    self.progress_updated.emit(f"📅 Updated last exchange rates update date to {today}")

                self.finished_success.emit(total_downloaded, filled_count)

        except Exception as e:
            self.finished_error.emit(f"Exchange rate update error: {e}")

    def stop(self):
        """Request worker to stop."""
        self.should_stop = True
