"""Modal dialog to confirm metadata when adding a vector icon note."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.apps.common.date_edit_quick import attach_date_edit_quick_controls
from harrix_swiss_knife.apps.icons.add_vector_ai import AddVectorAiFill, request_add_vector_fill
from harrix_swiss_knife.apps.icons.add_vector_meta import (
    NoteMeta,
    RepoMetaDefaults,
    defaults_from_source_stem,
    extract_permalink_base,
    extract_permalink_source_base,
    join_permalink,
    permalink_suffixes,
    sync_family_id_category,
)
from harrix_swiss_knife.apps.icons.family_id import title_from_family_id
from harrix_swiss_knife.apps.icons.keywords_update import parse_keywords_text
from harrix_swiss_knife.apps.icons.vector_render import render_icon_to_image
from harrix_swiss_knife.integrations.bothub import BothubRequestState
from harrix_swiss_knife.qt_emoji_icon import make_emoji_push_button

if TYPE_CHECKING:
    from pathlib import Path

_PREVIEW_SIDE = 256


class AddVectorImageDialog(QDialog):
    """Preview + metadata form for adding or editing one note-icon."""

    def __init__(
        self,
        parent: QWidget | None,
        *,
        source_path: Path,
        defaults: RepoMetaDefaults,
        app_config: dict[str, Any],
        initial_meta: NoteMeta | None = None,
        window_title: str | None = None,
    ) -> None:
        """Build the dialog prefilled from `source_path` and repo consensus."""
        super().__init__(parent)
        self._source_path = source_path
        self._defaults = defaults
        self._app_config = app_config
        self._initial_meta = initial_meta
        self._bothub_state = BothubRequestState()
        self._updating = False
        family_id, title, category = defaults_from_source_stem(source_path.stem)
        if initial_meta is not None:
            family_id = initial_meta.family_id
            title = initial_meta.title
            category = initial_meta.category
        self._initial_family_id = family_id
        self._initial_title = title
        self._initial_category = category
        self.setWindowTitle(window_title or f"Add Vector Image — {source_path.name}")
        self.setMinimumSize(1100, 600)
        self.resize(1200, 640)
        qt_modality.set_owner_window_modal(self)
        self._setup_ui()
        self._apply_initial_values()

    def get_meta(self) -> NoteMeta:
        """Return confirmed metadata from the form."""
        family_id = self._filename_edit.text().strip()
        category = self._category_edit.currentText().strip()
        site_suffix = self._permalink_suffix.text().strip()
        source_suffix = self._permalink_source_suffix.text().strip()
        if self._initial_meta is not None and self._initial_meta.featured_name:
            featured_name = self._initial_meta.featured_name
        else:
            featured_name = f"featured-image{self._source_path.suffix.casefold()}"
        return NoteMeta(
            family_id=family_id,
            title=self._name_edit.text().strip() or title_from_family_id(family_id or self._source_path.stem),
            date=self._date_edit.date().toString("yyyy-MM-dd"),
            category=category,
            tags=parse_keywords_text(self._tags_edit.toPlainText()),
            author=self._author_edit.currentText().strip(),
            author_email=self._author_email_edit.currentText().strip(),
            license=self._license_edit.currentText().strip(),
            license_url=self._license_url_edit.currentText().strip(),
            permalink=join_permalink(self._permalink_base.text(), site_suffix),
            permalink_source=join_permalink(self._permalink_source_base.text(), source_suffix),
            lang=self._lang_edit.text().strip() or "en",
            featured_name=featured_name,
        )

    def _apply_ai_fill(self, fill: AddVectorAiFill) -> None:
        self._updating = True
        try:
            if fill.filename:
                self._filename_edit.setText(fill.filename)
            if fill.name:
                self._name_edit.setText(fill.name)
            if fill.category:
                self._category_edit.setCurrentText(fill.category)
            if fill.tags:
                self._tags_edit.setPlainText("\n".join(fill.tags))
            if fill.filename or fill.category:
                synced = sync_family_id_category(
                    self._filename_edit.text().strip(),
                    self._category_edit.currentText().strip(),
                )
                if synced:
                    self._filename_edit.setText(synced)
                self._refresh_derived_fields(rebuild_name=not bool(fill.name))
        finally:
            self._updating = False

    def _apply_initial_values(self) -> None:
        self._updating = True
        try:
            meta = self._initial_meta
            self._filename_edit.setText(self._initial_family_id)
            self._name_edit.setText(self._initial_title)
            self._category_edit.setCurrentText(self._initial_category)
            if meta is not None:
                self._tags_edit.setPlainText("\n".join(meta.tags))
                self._author_edit.setCurrentText(meta.author or self._defaults.author)
                self._author_email_edit.setCurrentText(meta.author_email or self._defaults.author_email)
                self._license_edit.setCurrentText(meta.license or self._defaults.license)
                self._license_url_edit.setCurrentText(meta.license_url or self._defaults.license_url)
                parsed = QDate.fromString(meta.date, "yyyy-MM-dd")
                self._date_edit.setDate(parsed if parsed.year() > 0 else QDate.currentDate())
                permalink_base = extract_permalink_base(meta.permalink) or self._defaults.permalink_base
                source_base = (
                    extract_permalink_source_base(meta.permalink_source) or self._defaults.permalink_source_base
                )
                self._permalink_base.setText(permalink_base)
                self._permalink_source_base.setText(source_base)
                self._lang_edit.setText(meta.lang or "en")
                self._refresh_derived_fields(rebuild_name=False)
                return
            self._author_edit.setCurrentText(self._defaults.author)
            self._author_email_edit.setCurrentText(self._defaults.author_email)
            self._license_edit.setCurrentText(self._defaults.license)
            self._license_url_edit.setCurrentText(self._defaults.license_url)
            self._permalink_base.setText(self._defaults.permalink_base)
            self._permalink_source_base.setText(self._defaults.permalink_source_base)
            self._lang_edit.setText("en")
            self._date_edit.setDate(QDate.currentDate())
            self._refresh_derived_fields(rebuild_name=True)
        finally:
            self._updating = False

    def _editable_combo(self, values: list[str]) -> QComboBox:
        combo = QComboBox()
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        combo.setMinimumContentsLength(24)
        for value in values:
            combo.addItem(value)
        combo.setCurrentText("")
        return combo

    def _on_category_changed(self, _text: str = "") -> None:
        if self._updating:
            return
        self._updating = True
        try:
            synced = sync_family_id_category(
                self._filename_edit.text().strip(),
                self._category_edit.currentText().strip(),
            )
            if synced:
                self._filename_edit.setText(synced)
            self._refresh_derived_fields(rebuild_name=False)
        finally:
            self._updating = False

    def _on_filename_changed(self, _text: str = "") -> None:
        if self._updating:
            return
        self._updating = True
        try:
            self._refresh_derived_fields(rebuild_name=True)
        finally:
            self._updating = False

    def _on_fill_with_ai(self) -> None:
        request_add_vector_fill(
            self,
            app_config=self._app_config,
            bothub_state=self._bothub_state,
            icon_path=self._source_path,
            existing_stems=self._defaults.existing_variant_stems,
            category=self._category_edit.currentText().strip(),
            filename=self._filename_edit.text().strip(),
            name=self._name_edit.text().strip(),
            tags=parse_keywords_text(self._tags_edit.toPlainText()),
            fill_button=self._ai_button,
            on_fill=self._apply_ai_fill,
        )

    def _refresh_derived_fields(self, *, rebuild_name: bool) -> None:
        family_id = self._filename_edit.text().strip()
        category = self._category_edit.currentText().strip()
        if rebuild_name and family_id:
            self._name_edit.setText(title_from_family_id(family_id))
        site_suffix, source_suffix = permalink_suffixes(category, family_id)
        self._permalink_suffix.setText(site_suffix)
        self._permalink_source_suffix.setText(source_suffix)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        content = QHBoxLayout()

        preview = QLabel()
        preview.setFixedSize(_PREVIEW_SIDE, _PREVIEW_SIDE)
        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview.setStyleSheet("QLabel { background-color: #f0f0f0; border-radius: 8px; }")
        image = render_icon_to_image(self._source_path, _PREVIEW_SIDE)
        if image is not None and not image.isNull():
            preview.setPixmap(QPixmap.fromImage(image))
        content.addWidget(preview, 0, Qt.AlignmentFlag.AlignTop)

        form_host = QWidget()
        form = QFormLayout(form_host)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self._filename_edit = QLineEdit()
        self._filename_edit.textChanged.connect(self._on_filename_changed)
        form.addRow("filename", self._filename_edit)

        self._name_edit = QLineEdit()
        form.addRow("name", self._name_edit)

        self._date_edit = QDateEdit()
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDisplayFormat("yyyy-MM-dd")
        date_row = QWidget()
        date_layout = QHBoxLayout(date_row)
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.addWidget(self._date_edit)
        attach_date_edit_quick_controls(self._date_edit)
        form.addRow("date", date_row)

        self._category_edit = self._editable_combo(self._defaults.categories)
        self._category_edit.editTextChanged.connect(self._on_category_changed)
        form.addRow("categories", self._category_edit)

        self._tags_edit = QPlainTextEdit()
        self._tags_edit.setPlaceholderText("One keyword per line")
        self._tags_edit.setMinimumHeight(100)
        form.addRow("tags", self._tags_edit)

        self._author_edit = self._editable_combo(self._defaults.authors)
        form.addRow("author", self._author_edit)
        self._author_email_edit = self._editable_combo(self._defaults.author_emails)
        form.addRow("author-email", self._author_email_edit)
        self._license_edit = self._editable_combo(self._defaults.licenses)
        form.addRow("license", self._license_edit)
        self._license_url_edit = self._editable_combo(self._defaults.license_urls)
        form.addRow("license-url", self._license_url_edit)

        permalink_row = QHBoxLayout()
        self._permalink_base = QLineEdit()
        self._permalink_suffix = QLineEdit()
        permalink_row.addWidget(self._permalink_base, 2)
        permalink_row.addWidget(self._permalink_suffix, 3)
        form.addRow("permalink", permalink_row)

        permalink_source_row = QHBoxLayout()
        self._permalink_source_base = QLineEdit()
        self._permalink_source_suffix = QLineEdit()
        permalink_source_row.addWidget(self._permalink_source_base, 2)
        permalink_source_row.addWidget(self._permalink_source_suffix, 3)
        form.addRow("permalink-source", permalink_source_row)

        self._lang_edit = QLineEdit("en")
        form.addRow("lang", self._lang_edit)

        content.addWidget(form_host, 1)
        layout.addLayout(content)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self._ai_button = make_emoji_push_button("Fill with AI", "🤖")
        self._ai_button.clicked.connect(self._on_fill_with_ai)
        buttons.addWidget(self._ai_button)
        cancel_button = make_emoji_push_button("Cancel", "❌")
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(cancel_button)
        ok_button = make_emoji_push_button("OK", "✅")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self.accept)
        buttons.addWidget(ok_button)
        layout.addLayout(buttons)
