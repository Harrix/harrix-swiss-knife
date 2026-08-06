---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `set_exif_datetime.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnSetExifDatetime`](#%EF%B8%8F-class-onsetexifdatetime)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnSetExifDatetime`

```python
class OnSetExifDatetime(ActionBase)
```

Set EXIF DateTime / DateTimeOriginal / DateTimeDigitized in a folder.

Prompts for a folder, then a date and hour (minutes and seconds are set to
`00:00`). Updates JPEG, TIFF, and WEBP images recursively.

<details>
<summary>Code:</summary>

```python
class OnSetExifDatetime(ActionBase):

    icon = "🕒"
    title = "Set EXIF date and hour in …"

    @ActionBase.handle_exceptions("setting EXIF date and hour")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Ask for folder and datetime, then update EXIF tags in a worker thread."""
        self.folder_path = self.dialogs.get_existing_directory(
            "Select folder with images",
            self.config["path_3d"],
        )
        if self.folder_path is None:
            return

        selected = self._ask_date_and_hour()
        if selected is None:
            return

        self._exif_datetime = selected
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("setting EXIF date and hour thread")
    def in_thread(self) -> str | None:
        """Write EXIF date/time tags for images under the selected folder."""
        if self.folder_path is None:
            return None

        value = getattr(self, "_exif_datetime", None)
        if not isinstance(value, datetime):
            return None

        self.add_line(f"🔵 Setting EXIF date/time to {value:%Y-%m-%d %H:00:00}")
        self.add_line(f"Folder: {self.folder_path}")
        results = set_exif_datetime_in_folder(self.folder_path, value, recursive=True)
        summary = summarize_exif_datetime_results(results)
        self.add_line(summary)
        return summary

    @ActionBase.handle_exceptions("setting EXIF date and hour thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and result log after EXIF updates finish."""
        self.show_toast(f"{self.title} completed")
        self.show_result()

    def _ask_date_and_hour(self) -> datetime | None:
        """Show a dialog for date and hour; minutes/seconds are always zero."""
        widgets: dict[str, QWidget] = {}

        def build(dialog: QDialog, layout: QVBoxLayout) -> None:
            qt_modality.set_owner_window_modal(dialog)
            intro = QLabel(
                "EXIF DateTime, DateTimeOriginal, and DateTimeDigitized will be set "
                "to the selected date and hour (minutes and seconds = 00:00).\n"
                "Applies recursively to JPEG, TIFF, and WEBP files."
            )
            intro.setWordWrap(True)
            layout.addWidget(intro)

            form = QFormLayout()
            date_edit = QDateEdit(dialog)
            date_edit.setCalendarPopup(True)
            date_edit.setDisplayFormat("yyyy-MM-dd")
            date_edit.setDate(QDate.currentDate())
            form.addRow("Date:", date_edit)

            hour_spin = QSpinBox(dialog)
            hour_spin.setRange(0, 23)
            hour_spin.setValue(QTime.currentTime().hour())
            hour_spin.setAlignment(Qt.AlignmentFlag.AlignRight)
            form.addRow("Hour (0-23):", hour_spin)

            layout.addLayout(form)
            widgets["date"] = date_edit
            widgets["hour"] = hour_spin

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

        result, _dialog = self._exec_standard_dialog(
            "EXIF date and hour",
            build,
            stretch_row=0,
        )
        if result != QDialog.DialogCode.Accepted:
            return None

        date_edit = widgets["date"]
        hour_spin = widgets["hour"]
        if not isinstance(date_edit, QDateEdit) or not isinstance(hour_spin, QSpinBox):
            return None

        qdate = date_edit.date()
        # EXIF DateTime has no timezone; store wall-clock local values as naive.
        return datetime(  # noqa: DTZ001
            qdate.year(),
            qdate.month(),
            qdate.day(),
            hour_spin.value(),
            0,
            0,
        )
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Ask for folder and datetime, then update EXIF tags in a worker thread.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.dialogs.get_existing_directory(
            "Select folder with images",
            self.config["path_3d"],
        )
        if self.folder_path is None:
            return

        selected = self._ask_date_and_hour()
        if selected is None:
            return

        self._exif_datetime = selected
        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
```

Write EXIF date/time tags for images under the selected folder.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        if self.folder_path is None:
            return None

        value = getattr(self, "_exif_datetime", None)
        if not isinstance(value, datetime):
            return None

        self.add_line(f"🔵 Setting EXIF date/time to {value:%Y-%m-%d %H:00:00}")
        self.add_line(f"Folder: {self.folder_path}")
        results = set_exif_datetime_in_folder(self.folder_path, value, recursive=True)
        summary = summarize_exif_datetime_results(results)
        self.add_line(summary)
        return summary
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Show toast and result log after EXIF updates finish.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>
