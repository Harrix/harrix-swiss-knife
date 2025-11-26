"""Worker thread for checking exchange rates that need updates."""

from datetime import datetime, timedelta, timezone

from PySide6.QtCore import QThread, Signal


class ExchangeRateCheckerWorker(QThread):
    """Worker thread for checking which exchange rates need updates.

    Attributes:

    - `progress_updated` (`Signal`): Signal for progress message updates.
    - `check_completed` (`Signal`): Signal emitted when check is completed with list of currencies to process.
    - `check_failed` (`Signal`): Signal emitted when check fails with error message.
    - `should_stop` (`bool`): Flag to request worker to stop.

    """

    # Signals
    progress_updated: Signal = Signal(str)  # Progress message
    check_completed: Signal = Signal(list)  # List of currencies to process
    check_failed: Signal = Signal(str)  # Error message

    db_manager: object
    check_from_first_transaction: bool
    should_stop: bool

    def __init__(self, db_manager: object, *, check_from_first_transaction: bool = True) -> None:
        """Initialize the checker worker.

        Args:

        - `db_manager (`worker`): Database manager instance.
        - `check_from_first_transaction` (`bool`): If `True`, check from first transaction;
          if `False`, check from last exchange rate. Defaults to `True`.

        """
        super().__init__()
        self.db_manager = db_manager
        self.check_from_first_transaction = check_from_first_transaction
        self.should_stop = False

    def run(self) -> None:
        """Execute worker to check which exchange rates need updates."""
        try:
            self.progress_updated.emit("🔍 Starting exchange rates check...")

            # Get all currencies except USD (base currency)
            currencies = self.db_manager.get_currencies_except_usd()
            if not currencies:
                self.check_failed.emit("No currencies found except USD")
                return

            # Calculate which currencies need updates and missing records
            currencies_to_process = []
            today = datetime.now(timezone.utc).date()
            today_str = today.strftime("%Y-%m-%d")

            self.progress_updated.emit(f"📅 Checking rates up to {today_str}")

            # Determine start date based on configuration
            if self.check_from_first_transaction:
                # Get earliest transaction date
                earliest_transaction_date = self.db_manager.get_earliest_transaction_date()
                if not earliest_transaction_date:
                    self.check_failed.emit("No transactions found to determine start date.")
                    return

                global_start_date = datetime.fromisoformat(earliest_transaction_date).date()
                self.progress_updated.emit(f"📊 Checking from first transaction date: {global_start_date}")
            else:
                # Start from last exchange rate date for each currency
                global_start_date = None
                self.progress_updated.emit("📊 Checking from last exchange rate date for each currency")

            # Process each currency
            total_currencies = len(currencies)
            for idx, (currency_id, currency_code, _currency_name, _currency_symbol) in enumerate(currencies, 1):
                if self.should_stop:
                    self.check_failed.emit("Check cancelled by user")
                    return

                self.progress_updated.emit(f"🔄 Checking {currency_code} ({idx}/{total_currencies})...")

                # Determine start date for this currency
                if self.check_from_first_transaction:
                    # Use global start date from first transaction
                    start_date = global_start_date
                else:
                    # Get the last exchange rate date for this currency
                    last_date_str = self.db_manager.get_last_exchange_rate_date(currency_id)
                    if not last_date_str:
                        self.progress_updated.emit(f"⚠️ {currency_code}: No exchange rate records found - skipping")
                        continue
                    start_date = datetime.fromisoformat(last_date_str).date()

                # Calculate missing dates from start_date to today
                missing_dates = []
                current_date = start_date

                # Check in batches to avoid blocking
                batch_size = 100
                batch_count = 0

                while current_date <= today:
                    if self.should_stop:
                        self.check_failed.emit("Check cancelled by user")
                        return

                    date_str = current_date.strftime("%Y-%m-%d")
                    if not self.db_manager.check_exchange_rate_exists(currency_id, date_str):
                        missing_dates.append(date_str)

                    current_date = current_date + timedelta(days=1)
                    batch_count += 1

                    # Update progress every batch_size dates
                    if batch_count % batch_size == 0:
                        self.progress_updated.emit(
                            f"🔄 {currency_code}: Checked {batch_count} dates, found {len(missing_dates)} missing"
                        )

                # Get the last few existing records for potential updates
                if self.check_from_first_transaction:
                    # When checking all history, don't update existing records
                    last_records = []
                else:
                    # Get last 7 days of records for updates
                    last_records = self.db_manager.get_last_two_exchange_rate_records(currency_id)

                # Combine missing dates and existing records to update
                records_to_process = {"missing_dates": missing_dates, "existing_records": last_records}

                if missing_dates or last_records:
                    currencies_to_process.append((currency_id, currency_code, records_to_process))
                    self.progress_updated.emit(
                        f"✅ {currency_code}: {len(missing_dates)} missing, {len(last_records)} to update"
                    )
                else:
                    self.progress_updated.emit(f"✅ {currency_code}: Up to date")

            # Emit the result
            self.progress_updated.emit(f"✅ Check completed: {len(currencies_to_process)} currencies need updates")
            self.check_completed.emit(currencies_to_process)

        except Exception as e:
            self.check_failed.emit(f"Check error: {e!s}")

    def stop(self) -> None:
        """Request worker to stop."""
        self.should_stop = True
