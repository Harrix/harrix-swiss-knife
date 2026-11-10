---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `quick_launcher_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `QuickLauncherDialog`](#%EF%B8%8F-class-quicklauncherdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `allow_destroy`](#%EF%B8%8F-method-allow_destroy)
  - [⚙️ Method `closeEvent`](#%EF%B8%8F-method-closeevent)
  - [⚙️ Method `dispose_instance (classmethod)`](#%EF%B8%8F-method-dispose_instance-classmethod)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)
  - [⚙️ Method `mouseMoveEvent`](#%EF%B8%8F-method-mousemoveevent)
  - [⚙️ Method `mousePressEvent`](#%EF%B8%8F-method-mousepressevent)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `nativeEvent`](#%EF%B8%8F-method-nativeevent)
  - [⚙️ Method `present`](#%EF%B8%8F-method-present)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
  - [⚙️ Method `set_action_classes`](#%EF%B8%8F-method-set_action_classes)
  - [⚙️ Method `toggle (classmethod)`](#%EF%B8%8F-method-toggle-classmethod)
  - [⚙️ Method `update_session`](#%EF%B8%8F-method-update_session)

</details>

## 🏛️ Class `QuickLauncherDialog`

```python
class QuickLauncherDialog(QDialog)
```

Resizable always-on-top window listing quick-launcher actions.

<details>
<summary>Code:</summary>

```python
class QuickLauncherDialog(QDialog):

    _instance: ClassVar[QuickLauncherDialog | None] = None

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the quick launcher dialog."""
        super().__init__(parent)
        self._default_parent = parent
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowTitle("Quick launcher")
        apply_window_icon(self)
        self.setWindowFlags(_overlay_window_flags())
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=False)
        self.setMinimumSize(_OVERLAY_MIN_SIZE)
        self.resize(_OVERLAY_DEFAULT_SIZE)
        self._output_bus: ActionOutputBus | None = None
        self._action_classes: list[type[ActionBase]] = []
        self._dragging = False
        self._drag_position = QPoint()
        self._win11_caption = False
        self._close_button: QPushButton | None = None
        self._allow_destroy = False
        self._selected_card: FluentIconTileCard | None = None

        self.setObjectName("quickLauncherDialog")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setProperty(OVERLAY_CAPTION_PROPERTY, True)  # noqa: FBT003
        prepare_fluent_app_window(self)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        content = QWidget(self)
        content.setObjectName("quickLauncherContent")
        content.setAutoFillBackground(False)
        self._content_layout = QVBoxLayout(content)
        self._content_layout.setContentsMargins(SPACE_L, SPACE_M, SPACE_L, SPACE_L)
        self._content_layout.setSpacing(SPACE_M)

        menu_button = self._build_menu_button()
        self._win11_caption = install_win11_caption(self, trailing_widgets=[menu_button])
        if not self._win11_caption:
            self._build_fallback_header(menu_button)

        self._scroll = FluentScrollArea(content)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setWidgetResizable(True)
        self._scroll_body = QWidget()
        self._scroll_body.setObjectName("quickLauncherScrollBody")
        self._scroll_body.setAutoFillBackground(False)
        self._scroll_layout = QVBoxLayout(self._scroll_body)
        self._scroll_layout.setContentsMargins(0, 0, 0, 0)
        self._scroll_layout.setSpacing(SPACE_M)
        self._scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._actions_title = SubtitleLabel("Actions", self._scroll_body)
        self._actions_title.setCursor(Qt.CursorShape.OpenHandCursor)
        self._scroll_layout.addWidget(self._actions_title)

        self._actions_grid = FluentCardGrid(
            self._scroll_body,
            base_width=ICON_TILE_WIDTH,
            min_scale=COMMAND_CARD_MIN_SCALE,
        )
        self._scroll_layout.addWidget(self._actions_grid)

        self._actions_divider = QWidget(self._scroll_body)
        self._actions_divider.setObjectName("quickLauncherDivider")
        self._actions_divider.setFixedHeight(1)
        self._actions_divider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._scroll_layout.addWidget(self._actions_divider)

        self._markdown_title = SubtitleLabel("New Markdown", self._scroll_body)
        self._markdown_title.setCursor(Qt.CursorShape.OpenHandCursor)
        self._scroll_layout.addWidget(self._markdown_title)

        self._markdown_grid = FluentCardGrid(
            self._scroll_body,
            base_width=ICON_TILE_WIDTH,
            min_scale=COMMAND_CARD_MIN_SCALE,
        )
        self._scroll_layout.addWidget(self._markdown_grid)

        self._scroll.setWidget(self._scroll_body)
        self._content_layout.addWidget(self._scroll, stretch=1)

        self._hint = QLabel(self)
        self._hint.setCursor(Qt.CursorShape.OpenHandCursor)

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.addWidget(self._hint, stretch=1)
        self._size_grip = QSizeGrip(self)
        footer.addWidget(self._size_grip, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self._content_layout.addLayout(footer)

        self._layout.addWidget(content, stretch=1)

        for draggable_widget in (self._hint, self._actions_title, self._markdown_title):
            draggable_widget.installEventFilter(self)

        install_fluent_app_window(self)
        bind_theme(self, self._refresh_overlay_theme)
        self._update_hint()
        self._refresh_overlay_theme()
        self._apply_split_layout(enabled=False)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self._center_on_screen()
        install_documented_shortcut(
            self,
            QKeySequence.StandardKey.HelpContents,
            self._show_keyboard_shortcuts,
            description="Show keyboard shortcuts help",
            category="Help",
        )

    def allow_destroy(self) -> None:
        """Allow the next close to destroy this overlay instead of hiding it."""
        self._allow_destroy = True

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Hide the overlay instead of destroying it, unless disposing the singleton."""
        if self._allow_destroy:
            event.accept()
            super().closeEvent(event)
            return
        event.ignore()
        self.hide()

    @classmethod
    def dispose_instance(cls) -> None:
        """Destroy the singleton through Qt before application shutdown."""
        dialog = cls._instance
        cls._instance = None
        if dialog is None or not isValid(dialog):
            return
        dialog.allow_destroy()
        dialog.hide()
        dialog.close()
        dialog.deleteLater()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Start window drag from passive header and hint widgets; reposition AI buttons."""
        if isinstance(watched, FluentIconTileCard) and event.type() == QEvent.Type.Resize:
            button = watched.findChild(FluentIconButton, "quickLauncherAiButton")
            if button is not None:
                _position_ai_button(watched, button)
            return False

        if isinstance(watched, QWidget) and self._is_drag_excluded_widget(watched):
            return False

        if (
            event.type() == QEvent.Type.MouseButtonPress
            and isinstance(event, QMouseEvent)
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self._start_drag(event.globalPosition().toPoint())
            return True

        if (
            event.type() == QEvent.Type.MouseMove
            and isinstance(event, QMouseEvent)
            and event.buttons() & Qt.MouseButton.LeftButton
            and self._dragging
        ):
            self._move_drag(event.globalPosition().toPoint())
            return True

        if (
            event.type() == QEvent.Type.MouseButtonRelease
            and isinstance(event, QMouseEvent)
            and event.button() == Qt.MouseButton.LeftButton
            and self._dragging
        ):
            self._end_drag()
            return True

        return False

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Hide the overlay on Escape; move focus between cards with arrows."""
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            event.accept()
            return
        if event.key() in {
            Qt.Key.Key_Left,
            Qt.Key.Key_Right,
            Qt.Key.Key_Up,
            Qt.Key.Key_Down,
        } and self._move_card_focus(Qt.Key(event.key())):
            event.accept()
            return
        super().keyPressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Move the overlay while dragging from dialog margins."""
        if event.buttons() & Qt.MouseButton.LeftButton and self._dragging:
            self._move_drag(event.globalPosition().toPoint())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Start dragging from dialog margins and background."""
        if event.button() == Qt.MouseButton.LeftButton and self._can_start_drag_at(event.position().toPoint()):
            self._start_drag(event.globalPosition().toPoint())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Stop dragging the overlay."""
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._end_drag()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def nativeEvent(self, event_type, message) -> tuple[bool, int]:  # noqa: ANN001, N802
        """Allow caption drag and edge resize for this frameless window on Windows."""
        caption = try_handle_win11_caption_native_event(self, event_type, message)
        if caption is not None:
            return caption
        handled = try_handle_frameless_resize_native_event(self, event_type, message)
        if handled is not None:
            return handled
        return cast("tuple[bool, int]", super().nativeEvent(event_type, message))

    def present(self) -> None:
        """Show and focus the overlay without a visible size jump."""
        self._update_hint()
        self._retarget_to_active_modal_parent()
        width = max(self.width(), _OVERLAY_DEFAULT_SIZE.width())
        self.resize(width, max(self.height(), _OVERLAY_MIN_SIZE.height()))
        opening = not self.isVisible()
        if opening:
            self.move(-10_000, -10_000)
        self.show()
        self._fit_to_content()
        if opening:
            QApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
            self._fit_to_content()
        self._center_on_screen()
        self.raise_()
        self.activateWindow()
        self._focus_first_card()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Reflow card grids when the window width changes."""
        super().resizeEvent(event)
        QTimer.singleShot(0, self._refit_grids_for_width)

    def set_action_classes(self, action_classes: list[type[ActionBase]]) -> None:
        """Rebuild the action card grid."""
        self._action_classes = list(action_classes)
        self._actions_grid.clear()
        self._selected_card = None
        for action_cls in self._action_classes:
            card = self._make_action_card(action_cls)
            self._actions_grid.add_card(card)

    @classmethod
    def toggle(
        cls,
        *,
        parent: QWidget | None,
        output_bus: ActionOutputBus | None,
        action_classes: list[type[ActionBase]],
    ) -> None:
        """Show or hide the singleton quick launcher dialog."""
        if cls._instance is None or not isValid(cls._instance):
            cls._instance = cls(parent)
        dialog = cls._instance
        dialog.update_session(output_bus=output_bus, action_classes=action_classes)

        if dialog.isVisible():
            dialog.hide()
            return

        dialog.present()

    def update_session(
        self,
        *,
        output_bus: ActionOutputBus | None,
        action_classes: list[type[ActionBase]],
    ) -> None:
        """Refresh output bus and action list before showing."""
        self._output_bus = output_bus
        self.set_action_classes(action_classes)
        split_markdown = load_quick_launcher_markdown_in_panel()
        self._apply_split_layout(enabled=split_markdown)
        if split_markdown:
            choices, action_map = OnNewMarkdown(output_bus=output_bus).build_picker_choices()
            template_titles = {title for title, (kind, _) in action_map.items() if kind == "template"}
            self._set_markdown_choices(choices, ai_screenshot_titles=template_titles)
        else:
            self._markdown_grid.clear()
        if self.isVisible():
            self._fit_to_content()

    def _apply_split_layout(self, *, enabled: bool) -> None:
        """Show or hide the Markdown panel."""
        self._actions_divider.setVisible(enabled)
        self._markdown_title.setVisible(enabled)
        self._markdown_grid.setVisible(enabled)

    def _build_fallback_header(self, menu_button: FluentToolButton) -> None:
        """Build a simple title row when Win11 caption is unavailable."""
        title = QLabel("Quick launcher")
        title_font = QFont(title.font())
        grow_qfont(title_font)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setCursor(Qt.CursorShape.OpenHandCursor)

        close_button = QPushButton("")
        close_button.setFixedSize(CAPTION_BUTTON_HEIGHT, CAPTION_BUTTON_HEIGHT)
        close_button.setFlat(True)
        close_button.setToolTip("Close")
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_lucide_button_icon(close_button, CLOSE_BUTTON_ICON, icon_size=18)
        close_button.clicked.connect(self.hide)
        self._close_button = close_button

        header_spacer = QWidget(self)
        header_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header_spacer.setCursor(Qt.CursorShape.OpenHandCursor)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(menu_button)
        header.addWidget(title)
        header.addWidget(header_spacer, stretch=1)
        header.addWidget(close_button)
        self._content_layout.addLayout(header)

        for draggable_widget in (title, header_spacer):
            draggable_widget.installEventFilter(self)

    def _build_menu_button(self) -> FluentToolButton:
        header_menu = FluentMenu("", self)
        add_keyboard_shortcuts_help_action(header_menu, self, slot=self._show_keyboard_shortcuts)
        menu_button = FluentToolButton("", self, icon="menu", menu=header_menu)
        menu_button.setObjectName("quickLauncherMenuButton")
        menu_button.setFixedSize(CAPTION_BUTTON_HEIGHT, CAPTION_BUTTON_HEIGHT)
        menu_button.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        menu_button.setToolTip("Menu")
        menu_button.setAccessibleName("Menu")
        return menu_button

    def _can_start_drag_at(self, local_pos: QPoint) -> bool:
        child = self.childAt(local_pos)
        if child is None:
            return True
        return not self._is_drag_excluded_widget(child)

    def _center_on_screen(self) -> None:
        center_widget_on_available_screen(self)

    def _content_height_metrics(self) -> _ContentHeightMetrics:
        split = self._markdown_grid.isVisible()
        grid_width = self._grid_content_width()
        cards_natural = _grid_natural_height(self._actions_grid, grid_width)
        markdown_natural = _grid_natural_height(self._markdown_grid, grid_width) if split else 0
        actions_chrome = self._actions_title.sizeHint().height()
        markdown_chrome = self._markdown_title.sizeHint().height() if split else 0
        divider_height = self._actions_divider.height() if self._actions_divider.isVisible() else 0
        window_chrome = _layout_vertical_chrome(
            self._content_layout,
            has_fallback_header=not self._win11_caption,
        )
        if self._win11_caption:
            window_chrome += CAPTION_BUTTON_HEIGHT
        spacing_total = _layout_spacing_total(
            self._content_layout,
            self._scroll_layout,
            split=split,
            has_fallback_header=not self._win11_caption,
        )
        sections_chrome = actions_chrome + markdown_chrome + divider_height
        grids_natural = cards_natural + markdown_natural
        content_height = window_chrome + spacing_total + sections_chrome + grids_natural
        return _ContentHeightMetrics(
            split=split,
            cards_natural=cards_natural,
            markdown_natural=markdown_natural,
            sections_chrome=sections_chrome,
            window_chrome=window_chrome,
            spacing_total=spacing_total,
            grids_natural=grids_natural,
            content_height=content_height,
        )

    def _end_drag(self) -> None:
        if self._dragging:
            self.releaseMouse()
        self._dragging = False
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def _fit_to_content(self) -> None:
        """Resize the window to fit all cards when screen height allows."""
        metrics = self._content_height_metrics()
        screen = QApplication.primaryScreen()
        screen_max_height = screen.availableGeometry().height() if screen is not None else metrics.content_height
        target_height = min(max(metrics.content_height, _OVERLAY_MIN_SIZE.height()), screen_max_height)
        self.setMinimumHeight(min(metrics.content_height, screen_max_height, _OVERLAY_MIN_SIZE.height()))
        width = max(self.width(), _OVERLAY_MIN_SIZE.width())
        self.resize(width, target_height)

    def _focus_first_card(self) -> None:
        cards = [card for card in self._actions_grid.cards() if isinstance(card, FluentIconTileCard)]
        if not cards:
            cards = [card for card in self._markdown_grid.cards() if isinstance(card, FluentIconTileCard)]
        if not cards:
            return
        self._select_card(cards[0])
        cards[0].setFocus(Qt.FocusReason.OtherFocusReason)

    def _grid_content_width(self) -> int:
        margins = self._content_layout.contentsMargins()
        return max(1, self.width() - margins.left() - margins.right())

    def _is_drag_excluded_widget(self, widget: QWidget) -> bool:
        if self._close_button is not None and (widget is self._close_button or self._close_button.isAncestorOf(widget)):
            return True
        caption = self.findChild(QWidget, "captionBar")
        if caption is not None and (widget is caption or caption.isAncestorOf(widget)):
            return True
        if widget is self._actions_grid or self._actions_grid.isAncestorOf(widget):
            return True
        if widget is self._markdown_grid or self._markdown_grid.isAncestorOf(widget):
            return True
        return widget is self._size_grip or self._size_grip.isAncestorOf(widget)

    def _make_action_card(self, action_cls: type[ActionBase]) -> FluentIconTileCard:
        title = strip_md_inline_code_markers(action_cls.title)
        icon = create_action_icon(action_cls, ICON_TILE_ICON_SIZE)
        card = FluentIconTileCard(
            title,
            icon=icon if not icon.isNull() else None,
            user_data=action_cls,
        )
        card.clicked.connect(lambda listed=action_cls, host=card: self._on_action_card_clicked(listed, host))
        card.context_menu_requested.connect(
            lambda global_pos, listed=action_cls, host=card: show_action_class_context_menu(
                parent=self,
                global_pos=global_pos,
                action_cls=listed,
                host_widget=host,
            ),
        )
        return card

    def _make_markdown_card(
        self,
        icon_emoji: str,
        title: str,
        *,
        show_ai: bool,
    ) -> FluentIconTileCard:
        icon = create_emoji_icon(icon_emoji or "📝", ICON_TILE_ICON_SIZE)
        card = FluentIconTileCard(title, icon=icon if not icon.isNull() else None, user_data=title)
        card.clicked.connect(lambda choice=title, host=card: self._on_markdown_card_clicked(choice, host))
        if show_ai:
            button = FluentIconButton("camera", card, tooltip=AI_SCREENSHOT_TOOLTIP)
            button.setObjectName("quickLauncherAiButton")
            button.setFixedSize(_AI_BUTTON_SIZE, _AI_BUTTON_SIZE)
            button.clicked.connect(lambda choice=title: self._on_markdown_ai_screenshot(choice))
            card.installEventFilter(self)
            _position_ai_button(card, button)
        return card

    def _move_card_focus(self, key: Qt.Key) -> bool:
        cards = [card for card in self._actions_grid.cards() if isinstance(card, FluentIconTileCard)]
        if self._markdown_grid.isVisible():
            cards.extend(card for card in self._markdown_grid.cards() if isinstance(card, FluentIconTileCard))
        if not cards:
            return False
        current = self.focusWidget()
        index = next((i for i, card in enumerate(cards) if card is current or card.isAncestorOf(current)), -1)
        if index < 0 and self._selected_card is not None:
            index = next((i for i, card in enumerate(cards) if card is self._selected_card), -1)
        index = max(index, 0)
        columns = max(1, self._grid_content_width() // max(1, cards[0].width() or 1))
        if key == Qt.Key.Key_Left:
            index = max(0, index - 1)
        elif key == Qt.Key.Key_Right:
            index = min(len(cards) - 1, index + 1)
        elif key == Qt.Key.Key_Up:
            index = max(0, index - columns)
        elif key == Qt.Key.Key_Down:
            index = min(len(cards) - 1, index + columns)
        else:
            return False
        self._select_card(cards[index])
        cards[index].setFocus(Qt.FocusReason.OtherFocusReason)
        return True

    def _move_drag(self, global_pos: QPoint) -> None:
        self.move(global_pos - self._drag_position)

    def _on_action_card_clicked(self, action_cls: type[ActionBase], card: FluentIconTileCard) -> None:
        self._select_card(card)
        self._run_action(action_cls)

    def _on_markdown_ai_screenshot(self, title: str) -> None:
        self._run_markdown_choice(title, ai_screenshot=True)

    def _on_markdown_card_clicked(self, title: str, card: FluentIconTileCard) -> None:
        self._select_card(card)
        self._run_markdown_choice(title, ai_screenshot=False)

    def _refit_grids_for_width(self) -> None:
        """Update minimum height when the window width changes."""
        if not self.isVisible():
            return
        metrics = self._content_height_metrics()
        screen = QApplication.primaryScreen()
        screen_max_height = screen.availableGeometry().height() if screen is not None else metrics.content_height
        min_height = min(max(metrics.content_height, _OVERLAY_MIN_SIZE.height()), screen_max_height)
        self.setMinimumHeight(min(_OVERLAY_MIN_SIZE.height(), min_height))
        if metrics.content_height <= screen_max_height and self.height() < metrics.content_height:
            self.resize(self.width(), metrics.content_height)

    def _refresh_overlay_caption(self) -> None:
        """Re-apply caption fill after dialog stylesheet polish."""
        if not isValid(self):
            return
        refresh_win11_caption(self)

    def _refresh_overlay_theme(self) -> None:
        """Apply Fluent overlay border and divider for the current theme."""
        palette = palette_for(self)
        border = css(mix(palette.window_bg, palette.popup_stroke))
        window = css(palette.window_bg)
        muted = css(mix(palette.window_bg, palette.text_secondary))
        divider = css(palette.divider)
        self.setStyleSheet(
            f"#quickLauncherDialog {{ background-color: {window}; border: 1px solid {border}; }}"
            f"#captionBar, #captionButtonRow {{ background-color: {window}; }}"
            "#quickLauncherContent, #quickLauncherScrollBody { background: transparent; }"
            f"#quickLauncherDivider {{ background-color: {divider}; }}",
        )
        hint = getattr(self, "_hint", None)
        if hint is not None:
            hint.setStyleSheet(f"color: {muted};")
        divider_widget = getattr(self, "_actions_divider", None)
        if divider_widget is not None:
            divider_palette = divider_widget.palette()
            divider_palette.setColor(divider_widget.backgroundRole(), QColor(palette.divider))
            divider_widget.setAutoFillBackground(True)
            divider_widget.setPalette(divider_palette)
        # Caption must follow solid window_bg (see OVERLAY_CAPTION_PROPERTY), not wallpaper top.
        refresh_win11_caption(self)
        # setStyleSheet polish can reset caption palettes after the call above.
        QTimer.singleShot(0, self._refresh_overlay_caption)

    def _retarget_to_active_modal_parent(self) -> None:
        """Parent launcher to active modal dialog so it stays interactive."""
        modal_parent = QApplication.activeModalWidget()
        if modal_parent is self:
            modal_parent = None
        target_parent = modal_parent if modal_parent is not None else self._default_parent

        flags = _overlay_window_flags()
        if self.parentWidget() is not target_parent:
            self.setParent(target_parent, flags)
        elif self.windowFlags() != flags:
            self.setWindowFlags(flags)
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)

    def _run_action(self, action_cls: type[ActionBase]) -> None:
        self.hide()
        action = action_cls(output_bus=self._output_bus)
        action()

    def _run_markdown_choice(self, title: str, *, ai_screenshot: bool) -> None:
        self.hide()
        OnNewMarkdown(output_bus=self._output_bus).execute_picker_choice(
            title,
            ai_screenshot=ai_screenshot,
        )

    def _select_card(self, card: FluentIconTileCard) -> None:
        previous = self._selected_card
        if previous is not None and previous is not card:
            previous.set_selected(selected=False)
        card.set_selected(selected=True)
        self._selected_card = card

    def _set_markdown_choices(
        self,
        choices: list[tuple[str, str]],
        *,
        ai_screenshot_titles: set[str] | None = None,
    ) -> None:
        self._markdown_grid.clear()
        ai_titles = ai_screenshot_titles or set()
        for icon_emoji, title in choices:
            card = self._make_markdown_card(icon_emoji, title, show_ai=title in ai_titles)
            self._markdown_grid.add_card(card)

    def _show_keyboard_shortcuts(self) -> None:
        show_keyboard_shortcuts_help(
            self,
            "Quick launcher — Keyboard shortcuts",
            [
                ShortcutHelpEntry("Esc", "Hide Quick launcher", "Window"),
                ShortcutHelpEntry("Enter / Space", "Run the focused action card", "Actions"),
                ShortcutHelpEntry("Tab", "Move focus between cards", "Actions"),
                ShortcutHelpEntry("Arrow keys", "Move focus between cards", "Actions"),
                ShortcutHelpEntry("F1", "Show this keyboard shortcuts help", "Help"),
            ],
        )

    def _start_drag(self, global_pos: QPoint) -> None:
        self._dragging = True
        self._drag_position = global_pos - self.frameGeometry().topLeft()
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        self.grabMouse()

    def _update_hint(self) -> None:
        # Local import avoids circular dependency: action -> context -> dialog.
        from harrix_swiss_knife.actions.quick_launcher.action import OnQuickLauncher  # noqa: PLC0415

        hint_parts = ["Click a card to run", "Drag to move", "Esc or X to close"]
        hotkeys = load_hotkeys_for_action(OnQuickLauncher.__name__)
        if hotkeys:
            hint_parts.append(f"{' / '.join(hotkeys)} to toggle")
        self._hint.setText(" · ".join(hint_parts))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Build the quick launcher dialog.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._default_parent = parent
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowTitle("Quick launcher")
        apply_window_icon(self)
        self.setWindowFlags(_overlay_window_flags())
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=False)
        self.setMinimumSize(_OVERLAY_MIN_SIZE)
        self.resize(_OVERLAY_DEFAULT_SIZE)
        self._output_bus: ActionOutputBus | None = None
        self._action_classes: list[type[ActionBase]] = []
        self._dragging = False
        self._drag_position = QPoint()
        self._win11_caption = False
        self._close_button: QPushButton | None = None
        self._allow_destroy = False
        self._selected_card: FluentIconTileCard | None = None

        self.setObjectName("quickLauncherDialog")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setProperty(OVERLAY_CAPTION_PROPERTY, True)  # noqa: FBT003
        prepare_fluent_app_window(self)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        content = QWidget(self)
        content.setObjectName("quickLauncherContent")
        content.setAutoFillBackground(False)
        self._content_layout = QVBoxLayout(content)
        self._content_layout.setContentsMargins(SPACE_L, SPACE_M, SPACE_L, SPACE_L)
        self._content_layout.setSpacing(SPACE_M)

        menu_button = self._build_menu_button()
        self._win11_caption = install_win11_caption(self, trailing_widgets=[menu_button])
        if not self._win11_caption:
            self._build_fallback_header(menu_button)

        self._scroll = FluentScrollArea(content)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setWidgetResizable(True)
        self._scroll_body = QWidget()
        self._scroll_body.setObjectName("quickLauncherScrollBody")
        self._scroll_body.setAutoFillBackground(False)
        self._scroll_layout = QVBoxLayout(self._scroll_body)
        self._scroll_layout.setContentsMargins(0, 0, 0, 0)
        self._scroll_layout.setSpacing(SPACE_M)
        self._scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._actions_title = SubtitleLabel("Actions", self._scroll_body)
        self._actions_title.setCursor(Qt.CursorShape.OpenHandCursor)
        self._scroll_layout.addWidget(self._actions_title)

        self._actions_grid = FluentCardGrid(
            self._scroll_body,
            base_width=ICON_TILE_WIDTH,
            min_scale=COMMAND_CARD_MIN_SCALE,
        )
        self._scroll_layout.addWidget(self._actions_grid)

        self._actions_divider = QWidget(self._scroll_body)
        self._actions_divider.setObjectName("quickLauncherDivider")
        self._actions_divider.setFixedHeight(1)
        self._actions_divider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._scroll_layout.addWidget(self._actions_divider)

        self._markdown_title = SubtitleLabel("New Markdown", self._scroll_body)
        self._markdown_title.setCursor(Qt.CursorShape.OpenHandCursor)
        self._scroll_layout.addWidget(self._markdown_title)

        self._markdown_grid = FluentCardGrid(
            self._scroll_body,
            base_width=ICON_TILE_WIDTH,
            min_scale=COMMAND_CARD_MIN_SCALE,
        )
        self._scroll_layout.addWidget(self._markdown_grid)

        self._scroll.setWidget(self._scroll_body)
        self._content_layout.addWidget(self._scroll, stretch=1)

        self._hint = QLabel(self)
        self._hint.setCursor(Qt.CursorShape.OpenHandCursor)

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.addWidget(self._hint, stretch=1)
        self._size_grip = QSizeGrip(self)
        footer.addWidget(self._size_grip, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self._content_layout.addLayout(footer)

        self._layout.addWidget(content, stretch=1)

        for draggable_widget in (self._hint, self._actions_title, self._markdown_title):
            draggable_widget.installEventFilter(self)

        install_fluent_app_window(self)
        bind_theme(self, self._refresh_overlay_theme)
        self._update_hint()
        self._refresh_overlay_theme()
        self._apply_split_layout(enabled=False)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self._center_on_screen()
        install_documented_shortcut(
            self,
            QKeySequence.StandardKey.HelpContents,
            self._show_keyboard_shortcuts,
            description="Show keyboard shortcuts help",
            category="Help",
        )
```

</details>

### ⚙️ Method `allow_destroy`

```python
def allow_destroy(self) -> None
```

Allow the next close to destroy this overlay instead of hiding it.

<details>
<summary>Code:</summary>

```python
def allow_destroy(self) -> None:
        self._allow_destroy = True
```

</details>

### ⚙️ Method `closeEvent`

```python
def closeEvent(self, event: QCloseEvent) -> None
```

Hide the overlay instead of destroying it, unless disposing the singleton.

<details>
<summary>Code:</summary>

```python
def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        if self._allow_destroy:
            event.accept()
            super().closeEvent(event)
            return
        event.ignore()
        self.hide()
```

</details>

### ⚙️ Method `dispose_instance (classmethod)`

```python
def dispose_instance(cls) -> None
```

Destroy the singleton through Qt before application shutdown.

<details>
<summary>Code:</summary>

```python
def dispose_instance(cls) -> None:
        dialog = cls._instance
        cls._instance = None
        if dialog is None or not isValid(dialog):
            return
        dialog.allow_destroy()
        dialog.hide()
        dialog.close()
        dialog.deleteLater()
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Start window drag from passive header and hint widgets; reposition AI buttons.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if isinstance(watched, FluentIconTileCard) and event.type() == QEvent.Type.Resize:
            button = watched.findChild(FluentIconButton, "quickLauncherAiButton")
            if button is not None:
                _position_ai_button(watched, button)
            return False

        if isinstance(watched, QWidget) and self._is_drag_excluded_widget(watched):
            return False

        if (
            event.type() == QEvent.Type.MouseButtonPress
            and isinstance(event, QMouseEvent)
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self._start_drag(event.globalPosition().toPoint())
            return True

        if (
            event.type() == QEvent.Type.MouseMove
            and isinstance(event, QMouseEvent)
            and event.buttons() & Qt.MouseButton.LeftButton
            and self._dragging
        ):
            self._move_drag(event.globalPosition().toPoint())
            return True

        if (
            event.type() == QEvent.Type.MouseButtonRelease
            and isinstance(event, QMouseEvent)
            and event.button() == Qt.MouseButton.LeftButton
            and self._dragging
        ):
            self._end_drag()
            return True

        return False
```

</details>

### ⚙️ Method `keyPressEvent`

```python
def keyPressEvent(self, event: QKeyEvent) -> None
```

Hide the overlay on Escape; move focus between cards with arrows.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            event.accept()
            return
        if event.key() in {
            Qt.Key.Key_Left,
            Qt.Key.Key_Right,
            Qt.Key.Key_Up,
            Qt.Key.Key_Down,
        } and self._move_card_focus(Qt.Key(event.key())):
            event.accept()
            return
        super().keyPressEvent(event)
```

</details>

### ⚙️ Method `mouseMoveEvent`

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None
```

Move the overlay while dragging from dialog margins.

<details>
<summary>Code:</summary>

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.buttons() & Qt.MouseButton.LeftButton and self._dragging:
            self._move_drag(event.globalPosition().toPoint())
            event.accept()
            return
        super().mouseMoveEvent(event)
```

</details>

### ⚙️ Method `mousePressEvent`

```python
def mousePressEvent(self, event: QMouseEvent) -> None
```

Start dragging from dialog margins and background.

<details>
<summary>Code:</summary>

```python
def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self._can_start_drag_at(event.position().toPoint()):
            self._start_drag(event.globalPosition().toPoint())
            event.accept()
            return
        super().mousePressEvent(event)
```

</details>

### ⚙️ Method `mouseReleaseEvent`

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

Stop dragging the overlay.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._end_drag()
            event.accept()
            return
        super().mouseReleaseEvent(event)
```

</details>

### ⚙️ Method `nativeEvent`

```python
def nativeEvent(self, event_type, message) -> tuple[bool, int]
```

Allow caption drag and edge resize for this frameless window on Windows.

<details>
<summary>Code:</summary>

```python
def nativeEvent(self, event_type, message) -> tuple[bool, int]:  # noqa: ANN001, N802
        caption = try_handle_win11_caption_native_event(self, event_type, message)
        if caption is not None:
            return caption
        handled = try_handle_frameless_resize_native_event(self, event_type, message)
        if handled is not None:
            return handled
        return cast("tuple[bool, int]", super().nativeEvent(event_type, message))
```

</details>

### ⚙️ Method `present`

```python
def present(self) -> None
```

Show and focus the overlay without a visible size jump.

<details>
<summary>Code:</summary>

```python
def present(self) -> None:
        self._update_hint()
        self._retarget_to_active_modal_parent()
        width = max(self.width(), _OVERLAY_DEFAULT_SIZE.width())
        self.resize(width, max(self.height(), _OVERLAY_MIN_SIZE.height()))
        opening = not self.isVisible()
        if opening:
            self.move(-10_000, -10_000)
        self.show()
        self._fit_to_content()
        if opening:
            QApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
            self._fit_to_content()
        self._center_on_screen()
        self.raise_()
        self.activateWindow()
        self._focus_first_card()
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Reflow card grids when the window width changes.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        QTimer.singleShot(0, self._refit_grids_for_width)
```

</details>

### ⚙️ Method `set_action_classes`

```python
def set_action_classes(self, action_classes: list[type[ActionBase]]) -> None
```

Rebuild the action card grid.

<details>
<summary>Code:</summary>

```python
def set_action_classes(self, action_classes: list[type[ActionBase]]) -> None:
        self._action_classes = list(action_classes)
        self._actions_grid.clear()
        self._selected_card = None
        for action_cls in self._action_classes:
            card = self._make_action_card(action_cls)
            self._actions_grid.add_card(card)
```

</details>

### ⚙️ Method `toggle (classmethod)`

```python
def toggle(cls, *, parent: QWidget | None, output_bus: ActionOutputBus | None, action_classes: list[type[ActionBase]]) -> None
```

Show or hide the singleton quick launcher dialog.

<details>
<summary>Code:</summary>

```python
def toggle(
        cls,
        *,
        parent: QWidget | None,
        output_bus: ActionOutputBus | None,
        action_classes: list[type[ActionBase]],
    ) -> None:
        if cls._instance is None or not isValid(cls._instance):
            cls._instance = cls(parent)
        dialog = cls._instance
        dialog.update_session(output_bus=output_bus, action_classes=action_classes)

        if dialog.isVisible():
            dialog.hide()
            return

        dialog.present()
```

</details>

### ⚙️ Method `update_session`

```python
def update_session(self, *, output_bus: ActionOutputBus | None, action_classes: list[type[ActionBase]]) -> None
```

Refresh output bus and action list before showing.

<details>
<summary>Code:</summary>

```python
def update_session(
        self,
        *,
        output_bus: ActionOutputBus | None,
        action_classes: list[type[ActionBase]],
    ) -> None:
        self._output_bus = output_bus
        self.set_action_classes(action_classes)
        split_markdown = load_quick_launcher_markdown_in_panel()
        self._apply_split_layout(enabled=split_markdown)
        if split_markdown:
            choices, action_map = OnNewMarkdown(output_bus=output_bus).build_picker_choices()
            template_titles = {title for title, (kind, _) in action_map.items() if kind == "template"}
            self._set_markdown_choices(choices, ai_screenshot_titles=template_titles)
        else:
            self._markdown_grid.clear()
        if self.isVisible():
            self._fit_to_content()
```

</details>
