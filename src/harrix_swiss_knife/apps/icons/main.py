"""Vector Icons browser GUI."""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

import harrix_pylib as h
from PySide6.QtCore import QMimeData, QSize, Qt, QTimer, QUrl
from PySide6.QtGui import QCloseEvent, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import resources_rc  # noqa: F401
from harrix_swiss_knife.actions.common.open_in_editor import open_in_editor
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.common.app_entry import run_app_main
from harrix_swiss_knife.apps.common.qt_main_window import AppWindowMixin
from harrix_swiss_knife.apps.common.ui_helpers import reveal_in_file_explorer
from harrix_swiss_knife.apps.icons.catalog import IconCatalog, IconFamily, load_catalog, rebuild_catalog
from harrix_swiss_knife.apps.icons.settings import (
    ICON_SIZE_MAX,
    ICON_SIZE_MIN,
    load_category_icons,
    load_icon_size,
    save_icon_size,
    set_category_icon,
)
from harrix_swiss_knife.apps.icons.source_resolve import (
    candidate_source_stems,
    find_icon_source_file,
    resolve_external_ai_root,
    source_search_directories,
)
from harrix_swiss_knife.apps.icons.thumb_cache import (
    DEFAULT_THUMB_SIZE,
    ThumbnailCache,
    default_cache_dir,
    placeholder_pixmap,
    start_thumbnail_refresh,
)
from harrix_swiss_knife.apps.icons.widgets import DraggableIconList, VariantsPanel
from harrix_swiss_knife.paths import get_config_path_str
from harrix_swiss_knife.win11_backdrop import SystemBackdrop, try_apply_system_backdrop

logger = logging.getLogger(__name__)

ALL_CATEGORIES = "(All)"
CATEGORY_LIST_ICON_SIZE = 28


class MainWindow(QMainWindow, AppWindowMixin):
    """Browse Harrix Vector Icons with search, categories, cache, and drag-out."""

    about_app_name = "Vector Icons"
    about_description = "Browse and drag SVG icon families from Harrix-Vector-Icons."

    def __init__(self, *, hide_on_close: bool = False) -> None:
        """Build the browser UI and load catalog from config path."""
        super().__init__()
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)
        self.setWindowTitle("Vector Icons")
        self.setWindowIcon(QIcon(":/assets/logo.svg"))
        self._init_hide_on_close(hide_on_close=hide_on_close)

        self._icon_size = load_icon_size()
        self._catalog: IconCatalog | None = None
        self._repo_root: Path | None = None
        self._thumb_cache = ThumbnailCache(size=DEFAULT_THUMB_SIZE)
        self._pixmaps: dict[str, QPixmap] = {}
        self._placeholder = placeholder_pixmap(self._icon_size)
        self._thumb_thread = None
        self._thumb_worker = None
        self._current_category: str | None = None
        self._selected_family_id: str | None = None
        self._category_icons = load_category_icons()
        self._default_category_family_ids: dict[str, str] = {}
        self._icon_size_save_timer = QTimer(self)
        self._icon_size_save_timer.setSingleShot(True)
        self._icon_size_save_timer.setInterval(300)
        self._icon_size_save_timer.timeout.connect(self._persist_icon_size)

        self._build_ui()
        self._load_from_config()
        self._setup_window_size_and_position()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Stop background work and optionally hide instead of closing."""
        self._persist_icon_size()
        if self._hide_instead_of_close(event):
            return
        self._stop_thumb_refresh()
        super().closeEvent(event)

    def _apply_filters(self) -> None:
        if self._catalog is None or self._repo_root is None:
            self.icon_list.clear()
            self.variants_panel.clear_variants()
            self.count_label.setText("0 icons")
            return
        query = self.search_edit.text()
        families = self._catalog.filter_icons(category=self._current_category, query=query)
        self.icon_list.set_family_items(families, pixmaps=self._pixmaps, placeholder=self._placeholder)
        for index in range(self.icon_list.count()):
            item = self.icon_list.item(index)
            if item is None:
                continue
            family = item.data(Qt.ItemDataRole.UserRole)
            if not isinstance(family, IconFamily):
                continue
            featured = family.featured_path(self._repo_root)
            if featured is None and family.variants:
                featured = family.variants[0].absolute_path(self._repo_root, family.folder)
            if featured is not None:
                item.setData(Qt.ItemDataRole.UserRole + 1, str(featured))
        self.count_label.setText(f"{len(families)} icons")
        self.statusBar().showMessage(f"Showing {len(families)} / {len(self._catalog.icons)}")
        self._restore_or_clear_selection(families)

    def _apply_icon_size(self, size: int) -> None:
        """Apply display size to grids without writing config."""
        self._icon_size = size
        self._placeholder = placeholder_pixmap(size)
        self.icon_list.set_display_icon_size(size)
        self.variants_panel.set_thumb_size(self._variant_thumb_size(size))
        self.size_value_label.setText(str(size))
        selected_id = self._selected_family_id
        self._apply_filters()
        if selected_id is not None and self._catalog is not None and self._repo_root is not None:
            family = next((item for item in self._catalog.icons if item.id == selected_id), None)
            if family is not None:
                self._selected_family_id = selected_id
                self.variants_panel.show_family(family, self._repo_root)

    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Icon size"))
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(ICON_SIZE_MIN, ICON_SIZE_MAX)
        self.size_slider.setValue(self._icon_size)
        self.size_slider.setMaximumWidth(280)
        self.size_slider.setFixedHeight(24)
        self.size_slider.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.size_slider.valueChanged.connect(self._on_icon_size_changed)
        toolbar.addWidget(self.size_slider)
        self.size_value_label = QLabel(str(self._icon_size))
        self.size_value_label.setMinimumWidth(28)
        toolbar.addWidget(self.size_value_label)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search icons (title, tags, id)…")
        self.search_edit.textChanged.connect(self._apply_filters)
        toolbar.addWidget(self.search_edit, stretch=1)

        self.refresh_btn = QPushButton("🔄 Refresh catalog")
        self.refresh_btn.clicked.connect(self._on_refresh_catalog)
        toolbar.addWidget(self.refresh_btn)
        root.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.category_list = QListWidget()
        self.category_list.setMinimumWidth(160)
        self.category_list.setMaximumWidth(260)
        self.category_list.setIconSize(QSize(CATEGORY_LIST_ICON_SIZE, CATEGORY_LIST_ICON_SIZE))
        self.category_list.currentTextChanged.connect(self._on_category_changed)
        splitter.addWidget(self.category_list)

        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        self.count_label = QLabel("")
        center_layout.addWidget(self.count_label)
        self.icon_list = DraggableIconList(icon_size=self._icon_size)
        self.icon_list.family_selected.connect(self._on_family_selected)
        self._wire_icon_list_actions(self.icon_list)
        center_layout.addWidget(self.icon_list)
        splitter.addWidget(center)

        self.variants_panel = VariantsPanel(thumb_size=self._variant_thumb_size(self._icon_size))
        self.variants_panel.setMinimumWidth(220)
        self._wire_icon_list_actions(self.variants_panel.list)
        splitter.addWidget(self.variants_panel)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([200, 900, 320])
        root.addWidget(splitter)

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")

        file_menu = self.menuBar().addMenu("&File")
        refresh_action = file_menu.addAction("🔄 Refresh catalog")
        refresh_action.triggered.connect(self._on_refresh_catalog)
        open_cache_action = file_menu.addAction("📂 Open thumbs cache")
        open_cache_action.triggered.connect(self._on_open_thumbs_cache)
        cache_stats_action = file_menu.addAction("📊 Cache statistics")
        cache_stats_action.triggered.connect(self._on_cache_statistics)
        file_menu.addSeparator()
        self.actionExit = file_menu.addAction("E&xit")
        help_menu = self.menuBar().addMenu("&Help")
        self.actionAbout = help_menu.addAction("&About")
        self._connect_exit_about_actions()
        self._apply_exit_about_menu_emojis()

    def _category_family_id(self, category: str) -> str | None:
        if self._catalog is None:
            return None
        assigned = self._category_icons.get(category)
        if assigned:
            for family in self._catalog.icons:
                if family.id == assigned and category in family.categories:
                    return assigned
        return self._default_category_family_ids.get(category)

    def _category_pixmap_icon(self, category: str) -> QIcon:
        family_id = self._category_family_id(category)
        if family_id is None:
            return QIcon()
        pixmap = self._pixmaps.get(family_id)
        if pixmap is None or pixmap.isNull():
            return QIcon(self._placeholder)
        return QIcon(
            pixmap.scaled(
                CATEGORY_LIST_ICON_SIZE,
                CATEGORY_LIST_ICON_SIZE,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ),
        )

    @staticmethod
    def _format_byte_size(total_bytes: int) -> str:
        kib = 1024
        mib = kib * kib
        if total_bytes >= mib:
            return f"{total_bytes / mib:.2f} MB"
        if total_bytes >= kib:
            return f"{total_bytes / kib:.1f} KB"
        return f"{total_bytes} B"

    def _load_from_config(self) -> None:
        config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        raw = str(config.get("path_vector_icons") or "").strip()
        if not raw or raw.startswith("<"):
            QMessageBox.warning(
                self,
                "Vector Icons",
                "Set `path_vector_icons` in config.json to the Harrix-Vector-Icons repository root.",
            )
            self.statusBar().showMessage("path_vector_icons is not configured")
            return
        repo = Path(raw)
        if not repo.is_dir():
            QMessageBox.warning(self, "Vector Icons", f"Folder not found:\n{repo}")
            return
        self._repo_root = repo
        try:
            if not (repo / "catalog.json").is_file() and (repo / "icons").is_dir():
                self._catalog = rebuild_catalog(repo)
            else:
                self._catalog = load_catalog(repo)
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            QMessageBox.critical(self, "Vector Icons", f"Failed to load catalog:\n{exc}")
            return
        self._prime_pixmaps_from_cache()
        self._populate_categories()
        self._apply_filters()
        self._start_thumb_refresh()

    def _on_cache_statistics(self) -> None:
        stats = self._thumb_cache.stats(self._catalog)
        total_bytes = int(stats["total_bytes"])
        size_text = self._format_byte_size(total_bytes)
        lines = [
            f"Cache folder: {stats['cache_dir']}",
            f"PNG files: {stats['png_files']}",
            f"Total size: {size_text} ({total_bytes} bytes)",
            f"Meta entries: {stats['meta_entries']}",
            f"Thumb size: {stats['thumb_size']} px",
            f"Format version: {stats['format_version']}",
        ]
        if int(stats["catalog_icons"]) > 0:
            lines.extend(
                [
                    f"Catalog icons: {stats['catalog_icons']}",
                    f"Fresh: {stats['fresh']}",
                    f"Stale: {stats['stale']}",
                    f"Missing: {stats['missing']}",
                ],
            )
        message_box.information(self, "Cache statistics", "\n".join(lines))

    def _on_category_changed(self, text: str) -> None:
        self._current_category = None if text == ALL_CATEGORIES or not text else text
        self._apply_filters()

    def _on_copy_path(self, svg_path: str) -> None:
        path = str(Path(svg_path).resolve())
        clipboard = QApplication.clipboard()
        if clipboard is None:
            QMessageBox.warning(self, "Vector Icons", "Clipboard is not available.")
            return
        clipboard.setText(path)
        self.statusBar().showMessage(f"Copied path `{path}`")

    def _on_copy_svg(self, svg_path: str) -> None:
        path = Path(svg_path)
        if not path.is_file():
            QMessageBox.warning(self, "Vector Icons", f"File not found:\n{path}")
            return
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(str(path.resolve()))])
        try:
            mime.setText(path.read_text(encoding="utf-8"))
        except OSError:
            mime.setText(str(path.resolve()))
        clipboard = QApplication.clipboard()
        if clipboard is None:
            QMessageBox.warning(self, "Vector Icons", "Clipboard is not available.")
            return
        clipboard.setMimeData(mime)
        self.statusBar().showMessage(f"Copied `{path.name}`")

    def _on_family_selected(self, family: object) -> None:
        if family is None:
            self._selected_family_id = None
            self.variants_panel.clear_variants()
            return
        if not isinstance(family, IconFamily) or self._repo_root is None:
            return
        self._selected_family_id = family.id
        self.variants_panel.show_family(family, self._repo_root)
        self.statusBar().showMessage(f"{family.id}: {len(family.variants)} variants")

    def _on_icon_details(self, family: object, svg_path: str) -> None:
        if not isinstance(family, IconFamily):
            return
        note = family.note_path(self._repo_root) if self._repo_root is not None else None
        source = self._resolve_source_file(family, svg_path)
        variants = "\n".join(f"  - {variant.name} ({variant.file})" for variant in family.variants) or "  —"
        text = "\n".join(
            [
                f"ID: {family.id}",
                f"Title: {family.title}",
                f"Categories: {', '.join(family.categories) or '—'}",
                f"Tags: {', '.join(family.tags) or '—'}",
                f"Folder: {family.folder}",
                f"Note: {note if note is not None else '—'}",
                f"Source: {source if source is not None else '—'}",
                f"Featured: {family.featured or '—'}",
                f"Featured hash: {family.featured_hash or '—'}",
                f"Selected SVG: {svg_path}",
                f"Variants ({len(family.variants)}):",
                variants,
            ],
        )
        message_box.information(self, "Icon details", text)

    def _on_icon_size_changed(self, value: int) -> None:
        self._apply_icon_size(value)
        self._icon_size_save_timer.start()

    def _on_open_note_in_editor(self, family: object) -> None:
        if not isinstance(family, IconFamily):
            return
        if self._repo_root is None:
            QMessageBox.warning(self, "Vector Icons", "Icons repository is not loaded.")
            return
        note_path = family.note_path(self._repo_root)
        if note_path is None:
            QMessageBox.warning(self, "Vector Icons", f"Markdown note not found for `{family.id}`.")
            return
        config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        editor = str(config.get("editor-notes") or "").strip()
        if not editor or editor.startswith("<"):
            QMessageBox.warning(
                self,
                "Vector Icons",
                "Set `editor-notes` in config.json (for example `code-insiders`).",
            )
            return
        workspace = str(config.get("path_vector_icons") or self._repo_root).strip() or str(self._repo_root)
        try:
            open_in_editor(editor, workspace, note_path)
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, "Vector Icons", f"Failed to open note in editor:\n{exc}")
            return
        self.statusBar().showMessage(f"Opened `{note_path.name}` in {editor}")

    def _on_open_source(self, family: object, svg_path: str) -> None:
        source = self._resolve_source_file(family, svg_path)
        if source is None:
            self._warn_source_not_found(family, svg_path)
            return
        config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        raw_app = str(config.get("path_vector_icons_source_app") or "").strip()
        if not raw_app or raw_app.startswith("<"):
            QMessageBox.warning(
                self,
                "Vector Icons",
                "Set `path_vector_icons_source_app` in config.json "
                "to Adobe Illustrator (or another vector app) executable.",
            )
            return
        app_path = Path(raw_app)
        if not app_path.is_file():
            QMessageBox.warning(self, "Vector Icons", f"Source app not found:\n{app_path}")
            return
        try:
            subprocess.Popen([str(app_path), str(source)], shell=False)
        except OSError as exc:
            QMessageBox.critical(self, "Vector Icons", f"Failed to open source:\n{exc}")
            return
        self.statusBar().showMessage(f"Opened `{source.name}` in {app_path.name}")

    def _on_open_thumbs_cache(self) -> None:
        path = default_cache_dir()
        path.mkdir(parents=True, exist_ok=True)
        h.file.open_file_or_folder(path)
        self.statusBar().showMessage(f"Opened `{path}`")

    def _on_refresh_catalog(self) -> None:
        if self._repo_root is None:
            self._load_from_config()
            return
        try:
            self._catalog = rebuild_catalog(self._repo_root)
        except OSError as exc:
            QMessageBox.critical(self, "Vector Icons", f"Failed to rebuild catalog:\n{exc}")
            return
        self._prime_pixmaps_from_cache()
        self._populate_categories()
        self._apply_filters()
        self._start_thumb_refresh()

    def _on_reveal_in_explorer(self, svg_path: str) -> None:
        path = Path(svg_path)
        try:
            reveal_in_file_explorer(path)
        except (OSError, FileNotFoundError) as exc:
            QMessageBox.warning(self, "Vector Icons", str(exc))
            return
        self.statusBar().showMessage(f"Revealed `{path.name}`")

    def _on_reveal_source(self, family: object, svg_path: str) -> None:
        source = self._resolve_source_file(family, svg_path)
        if source is None:
            self._warn_source_not_found(family, svg_path)
            return
        try:
            reveal_in_file_explorer(source)
        except (OSError, FileNotFoundError) as exc:
            QMessageBox.warning(self, "Vector Icons", str(exc))
            return
        self.statusBar().showMessage(f"Revealed source `{source.name}`")

    def _on_set_as_category_icon(self, family: object) -> None:
        if not isinstance(family, IconFamily):
            return
        category = self._target_category_for_icon(family)
        if category is None:
            QMessageBox.warning(self, "Vector Icons", "Icon has no category to assign.")
            return
        self._category_icons = set_category_icon(category, family.id)
        self._refresh_category_icons()
        self.statusBar().showMessage(f"Category `{category}` icon set to `{family.id}`")

    def _on_thumb_finished(self, updated: int) -> None:
        total = len(self._catalog.icons) if self._catalog else 0
        self.statusBar().showMessage(f"Thumbnails ready ({updated} updated, {total} total)")
        self._refresh_category_icons()

    def _on_thumb_progress(self, family_id: str, thumb_path: str) -> None:
        pixmap = QPixmap(thumb_path)
        if pixmap.isNull():
            return
        self._pixmaps[family_id] = pixmap
        self.icon_list.update_family_pixmap(family_id, pixmap)
        if family_id in self._category_icons.values() or family_id in self._default_category_family_ids.values():
            self._refresh_category_icons()

    def _persist_icon_size(self) -> None:
        self._icon_size_save_timer.stop()
        save_icon_size(self.size_slider.value())

    def _populate_categories(self) -> None:
        self.category_list.blockSignals(True)  # noqa: FBT003
        self.category_list.clear()
        self._default_category_family_ids.clear()
        all_item = QListWidgetItem(QIcon(":/assets/logo.svg"), ALL_CATEGORIES)
        self.category_list.addItem(all_item)
        if self._catalog is not None:
            for name in self._catalog.categories():
                families = self._catalog.filter_icons(category=name)
                if families:
                    self._default_category_family_ids[name] = families[0].id
                item = QListWidgetItem(name)
                item.setIcon(self._category_pixmap_icon(name))
                self.category_list.addItem(item)
        self.category_list.setCurrentRow(0)
        self.category_list.blockSignals(False)  # noqa: FBT003
        self._current_category = None

    def _prime_pixmaps_from_cache(self) -> None:
        if self._catalog is None:
            return
        self._pixmaps.clear()
        for family in self._catalog.icons:
            pixmap = self._thumb_cache.load_pixmap(family.id)
            if pixmap is not None:
                self._pixmaps[family.id] = pixmap

    def _refresh_category_icons(self) -> None:
        for index in range(self.category_list.count()):
            item = self.category_list.item(index)
            if item is None:
                continue
            name = item.text()
            if name == ALL_CATEGORIES:
                item.setIcon(QIcon(":/assets/logo.svg"))
                continue
            item.setIcon(self._category_pixmap_icon(name))

    def _resolve_source_file(self, family: object, svg_path: str) -> Path | None:
        if not isinstance(family, IconFamily) or self._repo_root is None:
            return None
        config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        ai_root = resolve_external_ai_root(config.get("path_vector_icons_ai"))
        note_dir = self._repo_root / family.folder
        return find_icon_source_file(
            family_id=family.id,
            note_dir=note_dir,
            svg_path=Path(svg_path),
            external_ai_root=ai_root,
        )

    def _restore_or_clear_selection(self, families: list[IconFamily]) -> None:
        """Keep selection if the family is still visible; otherwise clear variants."""
        if self._selected_family_id is None:
            self.variants_panel.clear_variants()
            return
        for index, family in enumerate(families):
            if family.id != self._selected_family_id:
                continue
            item = self.icon_list.item(index)
            if item is not None:
                self.icon_list.setCurrentItem(item)
            return
        self._selected_family_id = None
        self.variants_panel.clear_variants()

    def _start_thumb_refresh(self) -> None:
        if self._catalog is None:
            return
        self._stop_thumb_refresh()
        self.statusBar().showMessage("Refreshing thumbnails in background…")
        self._thumb_thread, self._thumb_worker = start_thumbnail_refresh(
            self._catalog,
            self._thumb_cache,
            on_progress=self._on_thumb_progress,
            on_finished=self._on_thumb_finished,
        )

    def _stop_thumb_refresh(self) -> None:
        if self._thumb_worker is not None:
            self._thumb_worker.cancel()
        if self._thumb_thread is not None and self._thumb_thread.isRunning():
            self._thumb_thread.quit()
            self._thumb_thread.wait(3000)
        self._thumb_thread = None
        self._thumb_worker = None

    def _target_category_for_icon(self, family: IconFamily) -> str | None:
        if self._current_category and self._current_category in family.categories:
            return self._current_category
        return family.categories[0] if family.categories else None

    @staticmethod
    def _variant_thumb_size(icon_size: int) -> int:
        return max(ICON_SIZE_MIN, min(icon_size, (icon_size * 3) // 4 or icon_size))

    def _warn_source_not_found(self, family: object, svg_path: str) -> None:
        if not isinstance(family, IconFamily) or self._repo_root is None:
            QMessageBox.warning(self, "Vector Icons", "Source file not found.")
            return
        config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        ai_root = resolve_external_ai_root(config.get("path_vector_icons_ai"))
        note_dir = self._repo_root / family.folder
        stems = ", ".join(candidate_source_stems(family.id, Path(svg_path)))
        dirs = "\n".join(f"  - {path}" for path in source_search_directories(note_dir, ai_root)) or "  —"
        hint = ""
        if ai_root is None:
            hint = (
                "\n\nSet `path_vector_icons_ai` in config.json (for example Harrix-Vector-Icons-ai or its src folder)."
            )
        QMessageBox.warning(
            self,
            "Vector Icons",
            f"Source file not found for `{family.id}`.\n\nTried stems: {stems}\nSearch folders:\n{dirs}{hint}",
        )

    def _wire_icon_list_actions(self, icon_list: DraggableIconList) -> None:
        icon_list.reveal_requested.connect(self._on_reveal_in_explorer)
        icon_list.details_requested.connect(self._on_icon_details)
        icon_list.copy_requested.connect(self._on_copy_svg)
        icon_list.copy_path_requested.connect(self._on_copy_path)
        icon_list.open_note_requested.connect(self._on_open_note_in_editor)
        icon_list.set_category_icon_requested.connect(self._on_set_as_category_icon)
        icon_list.reveal_source_requested.connect(self._on_reveal_source)
        icon_list.open_source_requested.connect(self._on_open_source)


def main() -> None:
    """Run the Vector Icons app standalone."""
    run_app_main(MainWindow, set_tab_index_zero=False)


if __name__ == "__main__":
    main()
