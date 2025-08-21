---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `exchange_rate_worker.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ExchangeRateUpdateWorker`](#%EF%B8%8F-class-exchangerateupdateworker)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `run`](#%EF%B8%8F-method-run)
  - [⚙️ Method `stop`](#%EF%B8%8F-method-stop)

</details>

## 🏛️ Class `ExchangeRateUpdateWorker`

```python
class ExchangeRateUpdateWorker(QThread)
```

Worker thread for updating existing exchange rate records from yfinance.

<details>
<summary>Code:</summary>

```python
class ExchangeRateUpdateWorker(QThread):

    # Signals
    progress_updated = Signal(str)  # Progress message
    currency_started = Signal(str)  # Currency being processed
    rates_added = Signal(str, float, str)  # currency_code, rate, date
    finished_success = Signal(int, int)  # Updated records count, total records
    finished_error = Signal(str)  # Error message

    def __init__(self, db_manager, currencies_to_update):
        super().__init__()
        self.db_manager = db_manager
        self.currencies_to_update = currencies_to_update  # List of (currency_id, code, records)
        self.should_stop = False

    def run(self):
        """Main worker execution."""
        try:
            # Import required libraries
            import pandas as pd
            import yfinance as yf

            total_updated = 0
            total_records = sum(len(records) for _, _, records in self.currencies_to_update)

            # Clean invalid exchange rates first
            self.progress_updated.emit("🧹 Cleaning invalid exchange rates...")
            cleaned_count = self.db_manager.clean_invalid_exchange_rates()
            if cleaned_count > 0:
                self.progress_updated.emit(f"🧹 Cleaned {cleaned_count} invalid exchange rate records")

            def get_yfinance_data(currency_code: str, date: str) -> float | None:
                """Get exchange rate data from yfinance for a specific date."""
                ticker_symbol = f"{currency_code}USD=X"

                # Alternative ticker formats for problematic currencies
                alternative_tickers = {
                    "VND": ["USD/VND=X", "USDVND=X"],  # Vietnamese Dong alternatives
                    "TRY": ["USD/TRY=X", "USDTRY=X"],  # Turkish Lira alternatives
                    "RUB": ["USD/RUB=X", "USDRUB=X"],  # Russian Ruble alternatives
                }

                try:
                    # Download data for the specific date
                    ticker = yf.Ticker(ticker_symbol)
                    hist = ticker.history(start=date, end=date, interval="1d")

                    # If no data found, try alternative ticker formats
                    if hist.empty and currency_code in alternative_tickers:
                        self.progress_updated.emit(f"⚠️ No data found for {ticker_symbol}, trying alternatives...")

                        for alt_ticker in alternative_tickers[currency_code]:
                            if self.should_stop:
                                return None
                            self.progress_updated.emit(f"🔄 Trying alternative ticker: {alt_ticker}")
                            ticker = yf.Ticker(alt_ticker)
                            hist = ticker.history(start=date, end=date, interval="1d")

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
                            f"⚠️ No data found for {currency_code} with any yfinance ticker format on {date}"
                        )
                        return None

                    # Get the close price for the date
                    close_price = hist.iloc[0]["Close"] if not hist.empty else None

                    if not pd.isna(close_price) and close_price > 0:
                        return float(close_price)
                    else:
                        self.progress_updated.emit(
                            f"⚠️ Invalid yfinance price for {currency_code} on {date}: {close_price}"
                        )
                        return None

                except Exception as e:
                    self.progress_updated.emit(f"❌ Error with yfinance for {currency_code} on {date}: {e}")
                    return None

            # Process each currency that needs updates
            for currency_id, currency_code, records in self.currencies_to_update:
                if self.should_stop:
                    break

                self.currency_started.emit(currency_code)
                self.progress_updated.emit(f"📈 Updating {len(records)} existing records for {currency_code}")

                currency_updated = 0

                # Process each record for this currency
                for date_str, old_rate in records:
                    if self.should_stop:
                        break

                    try:
                        self.progress_updated.emit(f"🔄 Updating {currency_code} rate for {date_str}...")

                        # Get new rate from yfinance
                        new_rate = get_yfinance_data(currency_code, date_str)

                        if new_rate is not None and new_rate > 0:
                            # Update the existing record
                            if self.db_manager.update_exchange_rate(currency_id, date_str, new_rate):
                                total_updated += 1
                                currency_updated += 1
                                self.rates_added.emit(currency_code, new_rate, date_str)
                                self.progress_updated.emit(
                                    f"✅ Updated {currency_code} rate for {date_str}: {old_rate:.6f} → {new_rate:.6f}"
                                )
                            else:
                                self.progress_updated.emit(f"❌ Failed to update {currency_code} rate for {date_str}")
                        else:
                            self.progress_updated.emit(
                                f"⚠️ Skipping update for {currency_code} on {date_str}: invalid rate from yfinance"
                            )
                    except Exception as e:
                        self.progress_updated.emit(f"❌ Error updating rate for {currency_code} on {date_str}: {e}")
                        continue

                self.progress_updated.emit(f"📊 Updated {currency_updated} rates for {currency_code}")

            # Update last update date
            if not self.should_stop:
                today = datetime.now().strftime("%Y-%m-%d")
                if self.db_manager.set_last_exchange_rates_update_date(today):
                    self.progress_updated.emit(f"📅 Updated last exchange rates update date to {today}")

                self.finished_success.emit(total_updated, total_records)

        except Exception as e:
            self.finished_error.emit(f"Exchange rate update error: {e}")

    def stop(self):
        """Request worker to stop."""
        self.should_stop = True
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, db_manager, currencies_to_update)
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(self, db_manager, currencies_to_update):
        super().__init__()
        self.db_manager = db_manager
        self.currencies_to_update = currencies_to_update  # List of (currency_id, code, records)
        self.should_stop = False
```

</details>

### ⚙️ Method `run`

```python
def run(self)
```

Main worker execution.

<details>
<summary>Code:</summary>

```python
def run(self):
        try:
            # Import required libraries
            import pandas as pd
            import yfinance as yf

            total_updated = 0
            total_records = sum(len(records) for _, _, records in self.currencies_to_update)

            # Clean invalid exchange rates first
            self.progress_updated.emit("🧹 Cleaning invalid exchange rates...")
            cleaned_count = self.db_manager.clean_invalid_exchange_rates()
            if cleaned_count > 0:
                self.progress_updated.emit(f"🧹 Cleaned {cleaned_count} invalid exchange rate records")

            def get_yfinance_data(currency_code: str, date: str) -> float | None:
                """Get exchange rate data from yfinance for a specific date."""
                ticker_symbol = f"{currency_code}USD=X"

                # Alternative ticker formats for problematic currencies
                alternative_tickers = {
                    "VND": ["USD/VND=X", "USDVND=X"],  # Vietnamese Dong alternatives
                    "TRY": ["USD/TRY=X", "USDTRY=X"],  # Turkish Lira alternatives
                    "RUB": ["USD/RUB=X", "USDRUB=X"],  # Russian Ruble alternatives
                }

                try:
                    # Download data for the specific date
                    ticker = yf.Ticker(ticker_symbol)
                    hist = ticker.history(start=date, end=date, interval="1d")

                    # If no data found, try alternative ticker formats
                    if hist.empty and currency_code in alternative_tickers:
                        self.progress_updated.emit(f"⚠️ No data found for {ticker_symbol}, trying alternatives...")

                        for alt_ticker in alternative_tickers[currency_code]:
                            if self.should_stop:
                                return None
                            self.progress_updated.emit(f"🔄 Trying alternative ticker: {alt_ticker}")
                            ticker = yf.Ticker(alt_ticker)
                            hist = ticker.history(start=date, end=date, interval="1d")

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
                            f"⚠️ No data found for {currency_code} with any yfinance ticker format on {date}"
                        )
                        return None

                    # Get the close price for the date
                    close_price = hist.iloc[0]["Close"] if not hist.empty else None

                    if not pd.isna(close_price) and close_price > 0:
                        return float(close_price)
                    else:
                        self.progress_updated.emit(
                            f"⚠️ Invalid yfinance price for {currency_code} on {date}: {close_price}"
                        )
                        return None

                except Exception as e:
                    self.progress_updated.emit(f"❌ Error with yfinance for {currency_code} on {date}: {e}")
                    return None

            # Process each currency that needs updates
            for currency_id, currency_code, records in self.currencies_to_update:
                if self.should_stop:
                    break

                self.currency_started.emit(currency_code)
                self.progress_updated.emit(f"📈 Updating {len(records)} existing records for {currency_code}")

                currency_updated = 0

                # Process each record for this currency
                for date_str, old_rate in records:
                    if self.should_stop:
                        break

                    try:
                        self.progress_updated.emit(f"🔄 Updating {currency_code} rate for {date_str}...")

                        # Get new rate from yfinance
                        new_rate = get_yfinance_data(currency_code, date_str)

                        if new_rate is not None and new_rate > 0:
                            # Update the existing record
                            if self.db_manager.update_exchange_rate(currency_id, date_str, new_rate):
                                total_updated += 1
                                currency_updated += 1
                                self.rates_added.emit(currency_code, new_rate, date_str)
                                self.progress_updated.emit(
                                    f"✅ Updated {currency_code} rate for {date_str}: {old_rate:.6f} → {new_rate:.6f}"
                                )
                            else:
                                self.progress_updated.emit(f"❌ Failed to update {currency_code} rate for {date_str}")
                        else:
                            self.progress_updated.emit(
                                f"⚠️ Skipping update for {currency_code} on {date_str}: invalid rate from yfinance"
                            )
                    except Exception as e:
                        self.progress_updated.emit(f"❌ Error updating rate for {currency_code} on {date_str}: {e}")
                        continue

                self.progress_updated.emit(f"📊 Updated {currency_updated} rates for {currency_code}")

            # Update last update date
            if not self.should_stop:
                today = datetime.now().strftime("%Y-%m-%d")
                if self.db_manager.set_last_exchange_rates_update_date(today):
                    self.progress_updated.emit(f"📅 Updated last exchange rates update date to {today}")

                self.finished_success.emit(total_updated, total_records)

        except Exception as e:
            self.finished_error.emit(f"Exchange rate update error: {e}")
```

</details>

### ⚙️ Method `stop`

```python
def stop(self)
```

Request worker to stop.

<details>
<summary>Code:</summary>

```python
def stop(self):
        self.should_stop = True
```

</details>
