---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `window.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DirtyReposCommitWindow`](#%EF%B8%8F-class-dirtyreposcommitwindow)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `closeEvent`](#%EF%B8%8F-method-closeevent)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
  - [⚙️ Method `nativeEvent`](#%EF%B8%8F-method-nativeevent)
  - [⚙️ Method `replace_repos`](#%EF%B8%8F-method-replace_repos)
  - [⚙️ Method `stop_background_workers`](#%EF%B8%8F-method-stop_background_workers)
- [🔧 Function `show_dirty_repos_commit_window`](#-function-show_dirty_repos_commit_window)
- [🔧 Function `stop_active_git_commit_window`](#-function-stop_active_git_commit_window)

</details>

## 🏛️ Class `DirtyReposCommitWindow`

```python
class DirtyReposCommitWindow(QDialog)
```

Repos | files+commit | diff — commit dirty repos and push public ones.

<details>
<summary>Code:</summary>

```python
class DirtyReposCommitWindow(QDialog):

    def __init__(
        self,
        repos: Sequence[Path],
        parent: QWidget | None = None,
        *,
        initial_statuses: Sequence[DirtyRepoStatus] | None = None,
        quick_paste_db: str | Path | None = None,
        on_line: Callable[[str], None] | None = None,
    ) -> None:
        """Build the window with an initial dirty-repo path list.

        Pass `initial_statuses` from the action scan to skip a second full
        Git pass on the UI thread before the first paint.

        """
        super().__init__(parent)
        self.setObjectName("dirtyReposCommitWindow")
        self.setWindowTitle("Git commit")
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)  # noqa: FBT003
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setProperty(OVERLAY_CAPTION_PROPERTY, True)  # noqa: FBT003
        self.setMinimumSize(960, 640)
        apply_window_icon(self)
        prepare_fluent_app_window(self)

        self._on_line = on_line
        self._quick_paste_db = quick_paste_db
        self._quick_paste: list[str] = []
        self._statuses: list[DirtyRepoStatus] = []
        self._history_by_repo: dict[Path, list[CommitHistoryEntry]] = {}
        self._suggestion_subjects: list[str] = []
        self._suggestion_filter = ""
        self._applying_suggestion = False
        self._busy = False
        self._workers: list[_FnWorker] = []
        self._win11_caption = False
        self._suppress_file_signals = False
        self._visibility_generation = 0
        self._commit_summary = CommitDaySummary(today=DayCommitCounts(), yesterday=DayCommitCounts())
        self._commit_summary_running = False
        self._commit_summary_pending = False
        self._push_emphasized = False
        self._commit_emphasized = False

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.tabWidget = QTabWidget(self)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setDocumentMode(True)

        body = QWidget(self.tabWidget)
        body.setObjectName("dirtyReposCommitBody")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(SPACE_XL, SPACE_M, SPACE_XL, SPACE_XL)
        body_layout.setSpacing(SPACE_M)

        header = QHBoxLayout()
        header.setSpacing(SPACE_S)
        self._status_label = FluentText("", body, role=TextRole.SECONDARY)
        header.addWidget(self._status_label, 1)
        self._add_button = FluentPushButton("Add repositories", body, icon="folder-plus")
        self._add_button.setToolTip("Add a repository or a folder to config.json")
        self._add_button.clicked.connect(self._on_add_repositories)
        header.addWidget(self._add_button)
        self._check_button = FluentPushButton("Check", body, icon="refresh-cw")
        self._check_button.setToolTip("Re-check the selected repository")
        self._check_button.clicked.connect(self._check_current_repo)
        header.addWidget(self._check_button)
        self._rescan_button = FluentPushButton("Check all repositories", body, icon="refresh-cw")
        self._rescan_button.setToolTip("Scan every repository under paths_git_roots")
        self._rescan_button.clicked.connect(self._rescan_all_repos)
        header.addWidget(self._rescan_button)
        body_layout.addLayout(header)

        self._splitter = FluentSplitter(Qt.Orientation.Horizontal, body)
        polish_fluent_splitter(self._splitter)

        left = QWidget(self._splitter)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, SPACE_S, 0)
        left_layout.setSpacing(SPACE_S)
        left_layout.addWidget(FluentText("Repositories", left, role=TextRole.SECONDARY))
        self._repo_list = FluentListWidget(left, compact=True)
        self._repo_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._repo_list.currentItemChanged.connect(self._on_repo_changed)
        left_layout.addWidget(self._repo_list, 1)
        left_layout.addWidget(self._build_commit_summary(left))
        self._splitter.addWidget(left)

        middle = QWidget(self._splitter)
        middle_layout = QVBoxLayout(middle)
        middle_layout.setContentsMargins(SPACE_S, 0, SPACE_S, 0)
        middle_layout.setSpacing(SPACE_S)
        middle_layout.addWidget(FluentText("Changed files", middle, role=TextRole.SECONDARY))
        self._file_list = _CheckableFileList(middle)
        self._file_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._file_list.itemChanged.connect(self._on_file_item_changed)
        self._file_list.currentItemChanged.connect(self._on_file_focus_changed)
        self._file_list.copy_path_clicked.connect(self._on_copy_file_path_clicked)
        self._file_list.customContextMenuRequested.connect(self._on_file_context_menu)
        self._files_stack, self._files_empty = _empty_stack(
            self._file_list,
            "No changed files.\nWorking tree is clean.",
            middle,
        )
        middle_layout.addWidget(self._files_stack, 1)

        middle_layout.addWidget(FluentText("Commit title", middle, role=TextRole.SECONDARY))
        self._subject = FluentLineEdit(middle, placeholder="Commit message")
        self._subject.textChanged.connect(self._on_subject_edited)
        self._subject.installEventFilter(self)
        middle_layout.addWidget(self._subject)

        middle_layout.addWidget(FluentText("Suggestions", middle, role=TextRole.SECONDARY))
        self._suggestions = FluentListWidget(middle, compact=True)
        self._suggestions.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._suggestions.setItemDelegate(_SuggestionFilterDelegate(self._suggestions))
        self._suggestions.itemClicked.connect(self._on_suggestion_clicked)
        self._suggestions_stack, self._suggestions_empty = _empty_stack(
            self._suggestions,
            "No suggestions — working tree is clean.",
            middle,
        )
        middle_layout.addWidget(self._suggestions_stack, 1)

        buttons = QHBoxLayout()
        buttons.setSpacing(SPACE_S)
        # Qt treats a single "&" as a mnemonic; "&&" shows a literal ampersand.
        self._commit_push_button = FluentPrimaryButton("Commit && push", middle, icon="arrow-up-from-line")
        self._commit_push_button.setDefault(True)
        self._commit_push_button.clicked.connect(self._on_commit_and_push)
        self._commit_button = FluentPushButton("Commit", middle)
        self._commit_button.clicked.connect(self._on_commit)
        bind_theme(self._commit_button, self._style_commit_button)
        self._push_button = FluentPushButton("Push", middle, icon="arrow-up-from-line")
        self._push_button.clicked.connect(self._on_push)
        bind_theme(self._push_button, self._style_push_button)
        self._desktop_button = FluentPushButton("Open in GitHub Desktop", middle)
        self._desktop_button.clicked.connect(self._on_open_desktop)
        buttons.addWidget(self._commit_push_button)
        buttons.addWidget(self._commit_button)
        buttons.addWidget(self._push_button)
        buttons.addWidget(self._desktop_button)
        buttons.addStretch(1)
        middle_layout.addLayout(buttons)
        self._splitter.addWidget(middle)

        right = QWidget(self._splitter)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(SPACE_S, 0, 0, 0)
        right_layout.setSpacing(SPACE_S)
        right_layout.addWidget(FluentText("Diff", right, role=TextRole.SECONDARY))
        self._right_stack = QStackedWidget(right)
        self._diff = GitDiffEdit(self._right_stack)
        self._diff.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._diff_empty = _empty_hint(
            self._right_stack,
            "No diff to show.\nSelect a changed file to view its diff.",
        )
        self._unpushed_note = QWidget(self._right_stack)
        note_layout = QVBoxLayout(self._unpushed_note)
        note_layout.setContentsMargins(SPACE_M, SPACE_M, SPACE_M, SPACE_M)
        note_layout.setSpacing(SPACE_M)
        self._unpushed_label = FluentText("", self._unpushed_note, word_wrap=True)
        self._unpushed_hint = FluentText(
            "Nothing to commit in this repository.",
            self._unpushed_note,
            role=TextRole.SECONDARY,
            word_wrap=True,
        )
        # Accent primary: this note only appears when the tree is clean and push remains.
        self._unpushed_push = FluentPrimaryButton("Push these commits", self._unpushed_note, icon="arrow-up-from-line")
        self._unpushed_push.clicked.connect(self._on_push)
        note_layout.addWidget(self._unpushed_label)
        note_layout.addWidget(self._unpushed_hint)
        note_row = QHBoxLayout()
        note_row.setSpacing(SPACE_S)
        note_row.addWidget(self._unpushed_push)
        note_row.addStretch(1)
        note_layout.addLayout(note_row)
        note_layout.addStretch(1)
        self._right_stack.addWidget(self._diff)
        self._right_stack.addWidget(self._diff_empty)
        self._right_stack.addWidget(self._unpushed_note)
        self._right_stack.setCurrentWidget(self._diff_empty)
        right_layout.addWidget(self._right_stack, 1)
        self._splitter.addWidget(right)

        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 0)
        self._splitter.setStretchFactor(2, 1)
        self._splitter.setCollapsible(0, False)  # noqa: FBT003
        self._splitter.setCollapsible(1, False)  # noqa: FBT003
        self._splitter.setCollapsible(2, False)  # noqa: FBT003
        show_splitter_hairlines((self._splitter,))
        sizes = load_splitter_sizes(_SPLITTER_KEY, _SPLITTER_DEFAULT)
        self._splitter.setSizes(sizes)
        self._splitter.splitterMoved.connect(self._schedule_splitter_save)
        body_layout.addWidget(self._splitter, 1)

        self._charts_page = GitCommitChartsPage(self.tabWidget)
        self.tabWidget.addTab(body, "Commit")
        self.tabWidget.addTab(self._charts_page, "Charts")
        root.addWidget(self.tabWidget, 1)
        install_fluent_app_window(self)
        self._win11_caption = install_win11_caption(self)

        self._splitter_save_timer = QTimer(self)
        self._splitter_save_timer.setSingleShot(True)
        self._splitter_save_timer.setInterval(_SPLITTER_SAVE_DELAY_MS)
        self._splitter_save_timer.timeout.connect(self._save_splitter_sizes)

        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(_REFRESH_MS)
        self._refresh_timer.timeout.connect(self._refresh_known_dirty)

        if initial_statuses is not None:
            self._set_statuses(list(initial_statuses))
        else:
            initial = [Path(path).resolve() for path in repos]
            self._set_statuses(refresh_repo_statuses(initial))
        self._load_quick_paste_async()
        # Defer the today/yesterday strip so the window can paint first.
        QTimer.singleShot(0, self._refresh_commit_summary)
        self._refresh_timer.start()
        apply_app_window_size_and_position(self)
        self._update_commit_enabled()

    def closeEvent(self, event: Any) -> None:  # noqa: N802
        """Stop timers, join workers, and clear the singleton when closing."""
        self.stop_background_workers()
        self._save_splitter_sizes()
        global _active_window  # noqa: PLW0603
        if _active_window is self:
            _active_window = None
        super().closeEvent(event)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Arrow keys in the commit title walk matching suggestions, like Quick paste."""
        if watched is self._subject and event.type() == QEvent.Type.KeyPress and isinstance(event, QKeyEvent):
            if event.key() == Qt.Key.Key_Down:
                self._move_suggestion(1)
                return True
            if event.key() == Qt.Key.Key_Up:
                self._move_suggestion(-1)
                return True
        return super().eventFilter(watched, event)

    def nativeEvent(self, event_type: Any, message: Any) -> tuple[bool, int]:  # noqa: N802
        """Keep caption drag and edge resize on Windows."""
        handled = try_handle_win11_caption_native_event(self, event_type, message)
        if handled is not None:
            return handled
        return cast("tuple[bool, int]", super().nativeEvent(event_type, message))

    def replace_repos(
        self,
        repos: Sequence[Path],
        *,
        initial_statuses: Sequence[DirtyRepoStatus] | None = None,
        on_line: Callable[[str], None] | None = None,
    ) -> None:
        """Replace the dirty-repo list (used when the action rescans while open)."""
        if on_line is not None:
            self._on_line = on_line
        if initial_statuses is not None:
            self._set_statuses(list(initial_statuses))
            return
        initial = [Path(path).resolve() for path in repos]
        self._set_statuses(refresh_repo_statuses(initial))

    def stop_background_workers(self) -> None:
        """Join Git/commit and Charts QThreads before this window is destroyed."""
        self._refresh_timer.stop()
        self._splitter_save_timer.stop()
        self._charts_page.stop_background_work()
        for worker in list(self._workers):
            if worker.isRunning() and not worker.wait(3000):
                worker.terminate()
                worker.wait(1000)
        self._workers.clear()

    def _accept_suggestion(self, text: str) -> None:
        self._applying_suggestion = True
        try:
            self._subject.setText(text)
            self._subject.selectAll()
        finally:
            self._applying_suggestion = False
        self._update_commit_enabled()

    def _add_repo_section_header(self, title: str, *, count: int) -> None:
        """Add a non-selectable group heading to the repositories list."""
        item = QListWidgetItem(f"{title} ({count})")
        font = item.font()
        font.setBold(True)
        item.setFont(font)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        item.setData(_REPO_ROLE, title)
        item.setForeground(palette_for(self).text_secondary)
        self._repo_list.addItem(item)

    def _apply_repo_access(self, item: QListWidgetItem, access: RepoAccess) -> None:
        path = item.data(_REPO_ROLE)
        if not isinstance(path, Path):
            return
        item.setData(_REPO_KIND_ROLE, access.kind)
        item.setData(_REPO_SLUG_ROLE, access.github_slug)
        item.setData(_REPO_REMOTE_ROLE, access.remote_url)
        item.setIcon(self._repo_icon(access.kind))
        item.setToolTip(access.summary(path))

    def _apply_suggestion_filter(self) -> None:
        ordered = order_suggestions_for_filter(self._suggestion_subjects, self._suggestion_filter)
        self._suggestions.clear()
        for subject, matched in ordered:
            item = QListWidgetItem(subject)
            item.setData(_SUGGESTION_MATCH_ROLE, matched)
            self._suggestions.addItem(item)
        self._sync_suggestions_empty()

    def _apply_visibility_statuses(self, found: dict[Path, tuple[str, int]]) -> None:
        """Store public unpushed counts discovered while resolving visibility."""
        updated: list[DirtyRepoStatus] = []
        changed = False
        for status in self._statuses:
            payload = found.get(status.path)
            if payload is None:
                updated.append(status)
                continue
            visibility, ahead = payload
            if visibility == "public" and (status.unpushed != ahead or status.access_kind != "public"):
                updated.append(replace(status, unpushed=ahead, access_kind="public"))
                changed = True
            elif visibility == "private" and (status.unpushed > 0 or status.access_kind != "private"):
                updated.append(replace(status, unpushed=0, access_kind="private"))
                changed = True
            else:
                updated.append(status)
        ordered = order_repo_statuses(updated, prefer_first=self._current_repo())
        if not changed and [row.path for row in ordered] == [row.path for row in self._statuses]:
            by_path = {status.path: status for status in ordered}
            for row in range(self._repo_list.count()):
                item = self._repo_list.item(row)
                if item is None:
                    continue
                path = item.data(_REPO_ROLE)
                if not isinstance(path, Path):
                    continue
                status = by_path.get(path)
                if status is None:
                    continue
                item.setText(status.list_label())
                self._style_repo_item(item, status)
            self._statuses = ordered
            current = self._current_status()
            if current is not None and current.unpushed and not self._file_list.count():
                self._show_unpushed_note(current)
            self._set_status_text()
            self._update_commit_enabled()
            return
        self._set_statuses(ordered)

    def _build_commit_summary(self, parent: QWidget) -> QGroupBox:
        """Build the Today / Yesterday commit totals for the repository column."""
        group = QGroupBox(parent)
        group.setObjectName("groupBox_commits")
        group.setTitle("Commits")
        group.setToolTip(
            "Commits created today and yesterday on local branches. Public and private are GitHub repositories.",
        )
        grid = QGridLayout(group)
        grid.setContentsMargins(0, SPACE_XS, 0, 0)
        grid.setHorizontalSpacing(SPACE_M)
        grid.setVerticalSpacing(SPACE_S)
        grid.setColumnStretch(1, 1)

        self.label_commit_today_caption = QLabel("Today", group)
        self.label_commit_today_caption.setObjectName("label_commit_today_caption")
        self.label_today_commits = QLabel(group)
        self.label_today_commits.setObjectName("label_today_commits")
        self.label_commit_yesterday_caption = QLabel("Yesterday", group)
        self.label_commit_yesterday_caption.setObjectName("label_commit_yesterday_caption")
        self.label_yesterday_commits = QLabel(group)
        self.label_yesterday_commits.setObjectName("label_yesterday_commits")

        top = Qt.AlignmentFlag.AlignTop
        grid.addWidget(self.label_commit_today_caption, 0, 0, alignment=top)
        grid.addWidget(self.label_today_commits, 0, 1, alignment=top)
        grid.addWidget(self.label_commit_yesterday_caption, 1, 0, alignment=top)
        grid.addWidget(self.label_yesterday_commits, 1, 1, alignment=top)
        self.groupBox_commits = group
        bind_theme(group, self._polish_commit_summary)
        return group

    def _check_current_repo(self) -> None:
        """Re-check only the repository selected in the list."""
        if self._busy:
            return
        repo = self._current_repo()
        if repo is None:
            self._toast("Select a repository")
            return
        label = repo.name or str(repo)
        self._status_label.setText(f"Checking {label}…")
        self._emit_line(f"🔵 Checking {repo}")

        def work() -> DirtyRepoStatus:
            invalidate_unpushed_cache(repo)
            return build_repo_status(repo, resolve_visibility=True, fresh_unpushed=True)

        def done(status: DirtyRepoStatus) -> None:
            self._history_by_repo.pop(repo, None)
            statuses = [item for item in self._statuses if item.path != repo]
            statuses.append(status)
            ordered = order_repo_statuses(statuses, prefer_first=repo)
            self._set_statuses(ordered)
            save_git_repos_all_clean(all_clean=not any(row.needs_attention for row in ordered))
            if status.needs_attention:
                self._emit_line(f"✅ {label}: {status.list_label()}")
            else:
                self._toast(f"{label} is clean")
                self._emit_line(f"✅ {label}: clean (no commit or push needed)")
            self._set_status_text()

        def failed(_message: str) -> None:
            self._set_status_text()

        self._run_worker(work, done, busy=True, on_fail=failed)

    def _checked_paths(self) -> list[str]:
        paths: list[str] = []
        for index in range(self._file_list.count()):
            item = self._file_list.item(index)
            if item is None:
                continue
            if item.checkState() == Qt.CheckState.Checked:
                path = item.data(_FILE_PATH_ROLE)
                if isinstance(path, str) and path:
                    paths.append(path)
        return paths

    def _clear_suggestions(self) -> None:
        self._suggestion_subjects = []
        self._suggestions.clear()
        self._sync_suggestions_empty()

    def _commit_push_tooltip(self, status: DirtyRepoStatus | None, *, can_commit: bool) -> str:
        """Explain why Commit & push is enabled or inactive."""
        if not can_commit:
            if self._busy:
                return "Busy"
            if self._current_repo() is None:
                return "Select a repository"
            if not self._checked_paths():
                return "Select files to commit"
            if not self._subject.text().strip():
                return "Enter a commit message"
            return "Cannot commit"
        if status is None:
            return "Select a repository"
        if status.access_kind == "local":
            return "Local repositories are not pushed"
        if status.access_kind != "public":
            return "Commit & push is available for public repositories"
        return "Commit selected files, then push all unpushed commits"

    def _copy_file_texts(self, paths: list[str], *, basename: bool) -> None:
        """Put relative paths or basenames on the clipboard."""
        if not paths:
            return
        texts = [Path(path).name if basename else path for path in paths]
        clipboard = QApplication.clipboard()
        if clipboard is None:
            return
        clipboard.setText("\n".join(texts))
        if basename:
            self._toast("Copied file name" if len(paths) == 1 else "Copied file names")
        else:
            self._toast("Copied path" if len(paths) == 1 else "Copied paths")

    def _current_repo(self) -> Path | None:
        item = self._repo_list.currentItem()
        if item is None:
            return None
        path = item.data(_REPO_ROLE)
        return path if isinstance(path, Path) else None

    def _current_status(self) -> DirtyRepoStatus | None:
        repo = self._current_repo()
        if repo is None:
            return None
        for status in self._statuses:
            if status.path == repo:
                return status
        return None

    def _emit_line(self, line: str) -> None:
        if self._on_line is not None:
            self._on_line(line)

    def _focused_file(self) -> tuple[str, str] | None:
        item = self._file_list.currentItem()
        if item is None:
            return None
        path = item.data(_FILE_PATH_ROLE)
        status = item.data(_FILE_STATUS_ROLE)
        if not isinstance(path, str) or not path:
            return None
        return path, str(status or " M")

    def _load_diff_async(self) -> None:
        repo = self._current_repo()
        focused = self._focused_file()
        if repo is None or focused is None:
            self._show_diff_text("")
            return
        path, status = focused

        def work() -> str:
            return git_diff_text_for_path(repo, path, status=status)

        self._right_stack.setCurrentWidget(self._diff)
        self._run_worker(work, self._show_diff_text, busy=False)

    def _load_quick_paste_async(self) -> None:
        db = self._quick_paste_db

        def work() -> list[str]:
            return load_quick_paste_phrases(db)

        def done(phrases: list[str]) -> None:
            self._quick_paste = phrases
            self._rebuild_suggestions()

        self._run_worker(work, done, busy=False)

    def _load_repo_details_async(self, repo: Path) -> None:
        def work() -> tuple[list[ChangedFile], list[CommitHistoryEntry]]:
            files = list_changed_files(repo)
            history = self._history_by_repo.get(repo)
            if history is None:
                history = load_commit_history(repo)
            return files, history

        def done(payload: tuple[list[ChangedFile], list[CommitHistoryEntry]]) -> None:
            files, history = payload
            self._history_by_repo[repo] = history
            if self._current_repo() != repo:
                return
            if not files:
                status = self._current_status()
                if status is not None and status.access_kind == "public" and status.unpushed > 0:
                    self._populate_files([])
                    self._clear_suggestions()
                    self._show_unpushed_note(status)
                    return
                if status is not None and status.needs_attention:
                    self._refresh_known_dirty(prefer=repo)
                    return
                self._populate_files([])
                self._clear_suggestions()
                self._show_diff_text("")
                self._update_commit_enabled()
                return
            self._populate_files(files)
            self._rebuild_suggestions()
            self._load_diff_async()

        self._run_worker(work, done)

    def _matching_suggestion_rows(self) -> list[int]:
        rows: list[int] = []
        for row in range(self._suggestions.count()):
            item = self._suggestions.item(row)
            if item is None or item.data(_SUGGESTION_MATCH_ROLE) is False:
                continue
            rows.append(row)
        return rows

    def _merge_found_repos(self, repos: list[FoundGitRepo]) -> None:
        """Merge discovered repos into the list (attention first, then clean A — Z)."""
        scanned = {repo.path.resolve() for repo in repos}
        kept = [status for status in self._statuses if status.path.resolve() not in scanned]
        for repo in repos:
            if repo.status is not None:
                kept.append(repo.status)
            else:
                kept.append(DirtyRepoStatus(path=repo.path.resolve(), files=()))
        ordered = order_repo_statuses(kept)
        self._set_statuses(ordered)
        save_git_repos_all_clean(all_clean=not any(status.needs_attention for status in ordered))

    def _move_suggestion(self, delta: int) -> bool:
        rows = self._matching_suggestion_rows()
        if not rows:
            return False
        current = self._suggestions.currentRow()
        if current not in rows:
            row = rows[0] if delta > 0 else rows[-1]
        else:
            index = rows.index(current) + delta
            row = rows[max(0, min(index, len(rows) - 1))]
        item = self._suggestions.item(row)
        if item is None:
            return False
        self._suggestions.setCurrentItem(item)
        self._suggestions.scrollToItem(item)
        self._accept_suggestion(item.text())
        return True

    def _on_add_repositories(self) -> None:
        """Add a repository or folder to `config.json` and show what was found."""
        if self._busy:
            return
        roots = configured_git_roots()
        start = str(roots[-1]) if roots else str(Path.home())
        chosen = QFileDialog.getExistingDirectory(self, "Add repository or folder", start)
        if not chosen:
            return
        folder = Path(chosen)
        self._status_label.setText("Looking for repositories…")

        def work() -> tuple[GitRootAdd, list[FoundGitRepo]]:
            result = add_git_root(folder)
            if not folder.is_dir():
                return result, []
            return result, discover_git_repos(folder)

        def done(payload: tuple[GitRootAdd, list[FoundGitRepo]]) -> None:
            result, repos = payload
            self._set_status_text()
            if not folder.is_dir():
                self._toast(result.message)
                self._emit_line(f"❌ {result.message}")
                return
            attention = [repo for repo in repos if repo.status is not None]
            if result.added:
                self._emit_line(f"Added `{result.message}` to `paths_git_roots`")
                self._toast("Added to config.json")
            else:
                self._emit_line(f"⚪ {result.path} is already in `paths_git_roots`")
            self._emit_line(f"🔵 Found {len(repos)} repository(ies), {len(attention)} need a commit or push")
            self._merge_found_repos(repos)
            self._refresh_commit_summary()
            _FoundReposDialog(result, repos, self).exec()

        def failed(_message: str) -> None:
            self._set_status_text()

        self._run_worker(work, done, busy=True, on_fail=failed)

    def _on_commit(self) -> None:
        repo = self._current_repo()
        if repo is None or self._busy:
            return
        paths = self._checked_paths()
        subject = self._subject.text().strip()
        if not paths or not subject:
            return

        def work() -> tuple[bool, str]:
            return commit_selected_paths(repo, paths, subject)

        def done(result: tuple[bool, str]) -> None:
            ok, detail = result
            if ok:
                self._toast(f"Committed {repo.name}")
                self._emit_line(f"✅ {repo.name}: committed — {detail}")
                self._subject.clear()
                self._refresh_known_dirty(prefer=repo)
                self._refresh_commit_summary()
            else:
                self._toast(detail)
                self._emit_line(f"❌ {repo.name}: {detail}")

        self._run_worker(work, done)

    def _on_commit_and_push(self) -> None:
        """Commit selected paths, then push all unpushed commits on public repos."""
        repo = self._current_repo()
        status = self._current_status()
        if repo is None or status is None or self._busy or status.access_kind != "public":
            return
        paths = self._checked_paths()
        subject = self._subject.text().strip()
        if not paths or not subject:
            return

        def work() -> tuple[bool, str, bool | None]:
            ok, detail = commit_selected_paths(repo, paths, subject)
            if not ok:
                return False, detail, None
            push_ok, push_detail = push_current_branch(repo)
            return True, push_detail, push_ok

        def done(result: tuple[bool, str, bool | None]) -> None:
            ok, detail, pushed = result
            if not ok:
                self._toast(detail)
                self._emit_line(f"❌ {repo.name}: {detail}")
                return
            self._subject.clear()
            if pushed:
                self._toast(f"Committed and pushed {repo.name}")
                self._emit_line(f"✅ {repo.name}: committed and pushed — {detail}")
            else:
                self._toast(f"Committed {repo.name}; push failed")
                self._emit_line(f"✅ {repo.name}: committed")
                self._emit_line(f"❌ {repo.name}: push failed — {detail}")
            self._refresh_known_dirty(prefer=repo)
            self._refresh_commit_summary()

        self._run_worker(work, done)

    def _on_copy_file_path_clicked(self, path: str) -> None:
        """Copy one relative path from the row copy icon."""
        self._copy_file_texts([path], basename=False)

    def _on_discard_selected_files(self, paths: list[str]) -> None:
        """Confirm and discard working-tree changes for the selected paths."""
        repo = self._current_repo()
        if repo is None or self._busy or not paths:
            return
        preview = "\n".join(f"  • {path}" for path in paths[:_DISCARD_PREVIEW_LIMIT])
        extra = "" if len(paths) <= _DISCARD_PREVIEW_LIMIT else f"\n  … and {len(paths) - _DISCARD_PREVIEW_LIMIT} more"
        noun = "file" if len(paths) == 1 else "files"
        if not FluentMessageDialog.ask(
            self,
            "Discard changes",
            f"Discard changes in {len(paths)} {noun}?\n\n{preview}{extra}",
            yes="Discard",
            no="Cancel",
        ):
            return

        def work() -> tuple[bool, str]:
            return discard_changed_paths(repo, paths)

        def done(result: tuple[bool, str]) -> None:
            ok, detail = result
            if ok:
                self._toast(f"Discarded {len(paths)} {noun}")
                self._emit_line(f"↩️ {repo.name}: discarded — {detail}")
                self._refresh_known_dirty(prefer=repo)
            else:
                self._toast(detail)
                self._emit_line(f"❌ {repo.name}: {detail}")

        self._run_worker(work, done)

    def _on_file_context_menu(self, pos: QPoint) -> None:
        """Copy paths or discard changes for the list selection."""
        item = self._file_list.itemAt(pos)
        if item is not None and not item.isSelected():
            self._file_list.clearSelection()
            item.setSelected(True)
            self._file_list.setCurrentItem(item)
        paths = self._selected_file_paths()
        if not paths:
            return
        menu = FluentMenu("", self)
        add_lucide_action(menu, "Copy relative path", COPY_BUTTON_ICON).triggered.connect(
            lambda: self._copy_file_texts(paths, basename=False),
        )
        add_lucide_action(menu, "Copy file name", "file").triggered.connect(
            lambda: self._copy_file_texts(paths, basename=True),
        )
        menu.addSeparator()
        add_lucide_action(menu, "Discard changes", "undo-2").triggered.connect(
            lambda: self._on_discard_selected_files(paths),
        )
        menu.exec(self._file_list.viewport().mapToGlobal(pos))

    def _on_file_focus_changed(
        self,
        _current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        if self._suppress_file_signals:
            return
        self._load_diff_async()

    def _on_file_item_changed(self, _item: QListWidgetItem) -> None:
        if self._suppress_file_signals:
            return
        self._rebuild_suggestions()
        self._update_commit_enabled()

    def _on_open_desktop(self) -> None:
        repo = self._current_repo()
        if repo is None:
            return
        ok, detail = open_github_desktop_nonblocking(repo)
        if ok:
            self._toast(f"Opened {repo.name}")
            self._emit_line(f"📂 {repo.name}: opened in GitHub Desktop")
        else:
            self._toast(detail)
            self._emit_line(f"❌ {repo.name}: {detail}")

    def _on_push(self) -> None:
        status = self._current_status()
        if status is None or self._busy or status.access_kind != "public" or status.unpushed <= 0:
            return
        repo = status.path

        def work() -> tuple[bool, str]:
            return push_current_branch(repo)

        def done(result: tuple[bool, str]) -> None:
            ok, detail = result
            if ok:
                self._toast(f"Pushed {repo.name}")
                self._emit_line(f"✅ {repo.name}: pushed — {detail}")
                self._refresh_known_dirty(prefer=repo)
            else:
                self._toast(detail)
                self._emit_line(f"❌ {repo.name}: {detail}")

        self._run_worker(work, done)

    def _on_repo_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        if current is None:
            self._populate_files([])
            self._clear_suggestions()
            self._show_diff_text("")
            self._update_commit_enabled()
            return
        path = current.data(_REPO_ROLE)
        if isinstance(path, Path):
            self._load_repo_details_async(path)

    def _on_subject_edited(self, text: str) -> None:
        self._update_commit_enabled()
        if self._applying_suggestion or text == self._suggestion_filter:
            return
        self._suggestion_filter = text
        self._apply_suggestion_filter()

    def _on_suggestion_clicked(self, item: QListWidgetItem) -> None:
        self._accept_suggestion(item.text())

    def _paint_commit_summary(self) -> None:
        """Fill the Today and Yesterday labels from the latest counts."""
        summary = self._commit_summary
        apply_commit_day_summary_label(
            self.label_today_commits,
            summary.today.total,
            summary.today.public,
            summary.today.private,
            today=True,
            local=summary.today.local,
            other=summary.today.other,
        )
        apply_commit_day_summary_label(
            self.label_yesterday_commits,
            summary.yesterday.total,
            summary.yesterday.public,
            summary.yesterday.private,
            today=False,
            local=summary.yesterday.local,
            other=summary.yesterday.other,
        )

    def _polish_commit_summary(self) -> None:
        """Restyle the commit summary when the theme changes."""
        quiet_group_box(self.groupBox_commits)
        for name in ("label_commit_today_caption", "label_commit_yesterday_caption"):
            label = getattr(self, name)
            if isinstance(label, QLabel):
                apply_day_summary_caption(label)
                label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
                label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        self._paint_commit_summary()

    def _populate_files(self, files: list[ChangedFile] | tuple[ChangedFile, ...]) -> None:
        self._suppress_file_signals = True
        self._file_list.clear()
        for changed in files:
            item = QListWidgetItem(changed.path)
            caption = _file_status_glyph(changed.status)[2]
            item.setToolTip(f"{caption}: {changed.path}")
            item.setFlags(
                Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable,
            )
            item.setCheckState(Qt.CheckState.Checked)
            item.setData(_FILE_PATH_ROLE, changed.path)
            item.setData(_FILE_STATUS_ROLE, changed.status)
            self._file_list.addItem(item)
        self._suppress_file_signals = False
        if self._file_list.count():
            self._files_stack.setCurrentWidget(self._file_list)
            self._file_list.setCurrentRow(0)
        else:
            self._files_stack.setCurrentWidget(self._files_empty)
        self._update_commit_enabled()

    def _populate_repos(self) -> None:
        current = self._current_repo()
        self._repo_list.blockSignals(True)  # noqa: FBT003
        self._repo_list.clear()
        attention = [status for status in self._statuses if status.needs_attention]
        other = [status for status in self._statuses if not status.needs_attention]
        select_row = -1

        def add_status_row(status: DirtyRepoStatus) -> None:
            nonlocal select_row
            item = QListWidgetItem(status.list_label())
            item.setData(_REPO_ROLE, status.path)
            self._apply_repo_access(item, read_repo_access(status.path))
            self._style_repo_item(item, status)
            self._repo_list.addItem(item)
            if current is not None and status.path == current:
                select_row = self._repo_list.count() - 1

        if attention:
            self._add_repo_section_header(_REPO_SECTION_ATTENTION, count=len(attention))
            for status in attention:
                add_status_row(status)
        if other:
            self._add_repo_section_header(_REPO_SECTION_OTHER, count=len(other))
            for status in other:
                add_status_row(status)

        self._repo_list.blockSignals(False)  # noqa: FBT003
        if self._repo_list.count():
            if select_row < 0:
                select_row = next(
                    (
                        row
                        for row in range(self._repo_list.count())
                        if ((item := self._repo_list.item(row)) is not None and isinstance(item.data(_REPO_ROLE), Path))
                    ),
                    0,
                )
            self._repo_list.setCurrentRow(min(select_row, self._repo_list.count() - 1))
        else:
            self._populate_files([])
            self._clear_suggestions()
            self._show_diff_text("")
            self._update_commit_enabled()
        self._resolve_repo_visibility()

    def _push_tooltip(self, status: DirtyRepoStatus | None) -> str:
        """Explain why Push is enabled or inactive for the selected repository."""
        if status is None:
            return "Select a repository"
        if status.access_kind == "local":
            return "Local repositories are not pushed"
        if status.access_kind != "public":
            return "Push is available for public repositories"
        if status.unpushed <= 0:
            return "Nothing to push"
        noun = "commit" if status.unpushed == 1 else "commits"
        return f"Push {status.unpushed} {noun}"

    def _rebuild_suggestions(self) -> None:
        repo = self._current_repo()
        history = self._history_by_repo.get(repo, []) if repo is not None else []
        self._suggestion_subjects = rank_commit_subjects(
            set(self._checked_paths()),
            history,
            self._quick_paste,
        )
        self._apply_suggestion_filter()

    def _refresh_commit_summary(self) -> None:
        """Recount today's and yesterday's commits across configured repositories."""
        if self._commit_summary_running:
            self._commit_summary_pending = True
            return
        self._commit_summary_running = True

        def work() -> CommitDaySummary:
            return count_recent_commits(configured_git_roots())

        def done(summary: CommitDaySummary) -> None:
            self._commit_summary_running = False
            self._commit_summary = summary
            self._paint_commit_summary()
            if self._commit_summary_pending:
                self._commit_summary_pending = False
                self._refresh_commit_summary()

        def failed(_message: str) -> None:
            self._commit_summary_running = False
            if self._commit_summary_pending:
                self._commit_summary_pending = False
                self._refresh_commit_summary()

        self._run_worker(work, done, busy=False, on_fail=failed)

    def _refresh_known_dirty(self, prefer: Path | None = None) -> None:
        if self._busy:
            return
        known = [status.path for status in self._statuses]
        prefer_path = prefer or self._current_repo()
        had_attention = any(status.needs_attention for status in self._statuses)

        def work() -> list[DirtyRepoStatus]:
            return refresh_repo_statuses(known, prefer_first=prefer_path)

        def done(statuses: list[DirtyRepoStatus]) -> None:
            self._set_statuses(statuses)
            attention_left = any(status.needs_attention for status in statuses)
            save_git_repos_all_clean(all_clean=not attention_left)
            if had_attention and not attention_left:
                self._toast("Nothing left to commit or push")
                self._emit_line("✅ Nothing left to commit or push")

        self._run_worker(work, done, busy=False)

    def _repo_icon(self, kind: str) -> QIcon:
        palette = palette_for(self)
        if kind == "local":
            color = palette.text_secondary
        elif kind == "private":
            color = palette.caution
        else:
            color = palette.accent
        return create_lucide_icon(_ACCESS_ICONS.get(kind, "folder-git"), ICON_SIZE, color=color)

    def _rescan_all_repos(self) -> None:
        if self._busy:
            return
        self._status_label.setText("Checking all repositories…")
        self._emit_line("🔵 Checking all repositories from `paths_git_roots`")

        def work() -> tuple[list[Path], list[DirtyRepoStatus]]:
            roots = configured_git_roots()
            return roots, scan_all_repo_statuses(roots)

        def done(payload: tuple[list[Path], list[DirtyRepoStatus]]) -> None:
            roots, statuses = payload
            if not roots:
                self._toast("`paths_git_roots` is empty")
                self._emit_line("❌ `paths_git_roots` is missing or empty in config.json.")
                self._set_status_text()
                return
            self._set_statuses(statuses)
            attention = [status for status in statuses if status.needs_attention]
            save_git_repos_all_clean(all_clean=not attention)
            self._emit_line(f"🔵 Scanned {len(roots)} root(s) from `paths_git_roots`")
            for root in roots:
                self._emit_line(f"  • {root}")
            if attention:
                self._toast(f"{len(attention)} repo(s) need a commit or push")
                self._emit_line(f"🔶 {len(attention)} repository(ies) need a commit or push")
            else:
                self._toast("All Git repos are committed and pushed")
                self._emit_line("✅ No repositories need a commit or push")
            self._refresh_commit_summary()

        def failed(_message: str) -> None:
            self._set_status_text()

        self._run_worker(work, done, busy=True, on_fail=failed)

    def _resolve_repo_visibility(self) -> None:
        pending: list[tuple[Path, str, str]] = []
        for row in range(self._repo_list.count()):
            item = self._repo_list.item(row)
            if item is None or item.data(_REPO_KIND_ROLE) != "remote":
                continue
            slug = item.data(_REPO_SLUG_ROLE)
            path = item.data(_REPO_ROLE)
            if not isinstance(slug, str) or "/" not in slug or not isinstance(path, Path):
                continue
            owner, _, name = slug.partition("/")
            if owner and name:
                pending.append((path, owner, name))
        self._visibility_generation += 1
        generation = self._visibility_generation
        if not pending:
            return

        def work() -> dict[Path, tuple[str, int]]:
            found: dict[Path, tuple[str, int]] = {}
            for path, owner, name in pending:
                visibility = github_repo_visibility(owner, name)
                ahead = unpushed_commit_count(path) if visibility == "public" else 0
                found[path] = (visibility, ahead)
            return found

        def done(found: object) -> None:
            if generation != self._visibility_generation:
                return
            if not isinstance(found, dict):
                return
            for row in range(self._repo_list.count()):
                item = self._repo_list.item(row)
                if item is None:
                    continue
                path = item.data(_REPO_ROLE)
                if not isinstance(path, Path):
                    continue
                visibility, _ahead = found.get(path, ("", 0))
                if visibility not in {"public", "private"}:
                    continue
                remote = item.data(_REPO_REMOTE_ROLE)
                self._apply_repo_access(
                    item,
                    repo_access_from_remote(str(remote or ""), visibility=visibility),
                )
            self._apply_visibility_statuses(found)

        self._run_worker(work, done, busy=False)

    def _run_worker(
        self,
        fn: Callable[[], Any],
        on_done: Callable[[Any], None],
        *,
        busy: bool = True,
        on_fail: Callable[[str], None] | None = None,
    ) -> None:
        # No QObject parent: parenting a running QThread to the window makes Qt
        # destroy it on quit before closeEvent can wait, which aborts the process.
        worker = _FnWorker(fn)
        self._workers.append(worker)

        def finished(result: Any) -> None:
            if busy:
                self._busy = False
                self._update_commit_enabled()
            on_done(result)

        def failed(message: str) -> None:
            if busy:
                self._busy = False
                self._update_commit_enabled()
            self._toast(message)
            self._emit_line(f"❌ {message}")
            if on_fail is not None:
                on_fail(message)

        def cleanup() -> None:
            # Only after QThread.finished — never deleteLater from inside run().
            if worker in self._workers:
                self._workers.remove(worker)
            worker.deleteLater()

        worker.finished_ok.connect(finished)
        worker.failed.connect(failed)
        worker.finished.connect(cleanup)
        if busy:
            self._busy = True
            self._update_commit_enabled()
        worker.start()

    def _save_splitter_sizes(self) -> None:
        save_splitter_sizes(_SPLITTER_KEY, self._splitter.sizes(), _SPLITTER_DEFAULT)

    def _schedule_splitter_save(self, *_args: object) -> None:
        self._splitter_save_timer.start()

    def _selected_file_paths(self) -> list[str]:
        """Return selected changed-file paths in list order (not checkbox state)."""
        paths: list[str] = []
        for index in range(self._file_list.count()):
            item = self._file_list.item(index)
            if item is None or not item.isSelected():
                continue
            path = item.data(_FILE_PATH_ROLE)
            if isinstance(path, str) and path:
                paths.append(path)
        return paths

    def _set_status_text(self) -> None:
        count = len(self._statuses)
        dirty_count = sum(1 for status in self._statuses if status.is_dirty)
        push_count = sum(1 for status in self._statuses if status.unpushed)
        attention_count = sum(1 for status in self._statuses if status.needs_attention)
        if count == 0:
            self._status_label.setText("No repositories found under paths_git_roots.")
            return
        if attention_count == 0:
            noun = "repository" if count == 1 else "repositories"
            self._status_label.setText(f"No commit or push needed · {count} {noun} listed.")
            return
        parts: list[str] = []
        if dirty_count:
            parts.append(f"{dirty_count} with uncommitted changes")
        if push_count:
            parts.append(f"{push_count} public with unpushed commits")
        self._status_label.setText(", ".join(parts) + f" · {count} listed.")

    def _set_statuses(self, statuses: list[DirtyRepoStatus]) -> None:
        self._statuses = order_repo_statuses(statuses)
        self._populate_repos()
        self._set_status_text()

    def _show_diff_text(self, text: str) -> None:
        """Show a textual diff, or an empty hint when there is nothing to display."""
        if text.strip():
            self._diff.setPlainText(text)
            self._right_stack.setCurrentWidget(self._diff)
            return
        if self._current_repo() is None:
            self._diff_empty.setText("Select a repository to review changes.")
        elif self._file_list.count() == 0:
            self._diff_empty.setText("No diff to show.\nWorking tree is clean.")
        else:
            self._diff_empty.setText("No diff to show.\nSelect a changed file to view its diff.")
        self._right_stack.setCurrentWidget(self._diff_empty)

    def _show_unpushed_note(self, status: DirtyRepoStatus) -> None:
        """Explain a clean public repository and offer to push its commits."""
        noun = "commit" if status.unpushed == 1 else "commits"
        self._unpushed_label.setText(
            f"{status.unpushed} {noun} on this public repository are not on the remote. The working tree is clean.",
        )
        self._unpushed_push.setText(f"Push {status.unpushed} {noun}")
        self._right_stack.setCurrentWidget(self._unpushed_note)
        self._update_commit_enabled()

    def _style_commit_button(self) -> None:
        """Use accent chrome for Commit on local repositories."""
        button = self._commit_button
        palette = palette_for(button)
        if self._commit_emphasized:
            button.setStyleSheet(accent_button_qss(palette))
        else:
            button.setStyleSheet(push_button_qss(palette))

    def _style_push_button(self) -> None:
        """Use accent chrome when Push is the only remaining action."""
        button = self._push_button
        palette = palette_for(button)
        if self._push_emphasized:
            button.setStyleSheet(accent_button_qss(palette))
            button.setIcon(create_lucide_icon("arrow-up-from-line", ICON_SIZE, color=palette.text_on_accent))
        else:
            button.setStyleSheet(push_button_qss(palette))
            button.setIcon(themed_icon("arrow-up-from-line", palette))
        button.setIconSize(QSize(ICON_SIZE, ICON_SIZE))

    def _style_repo_item(self, item: QListWidgetItem, status: DirtyRepoStatus) -> None:
        """Mute clean repositories so attention rows stand out at the top."""
        palette = palette_for(self)
        if status.needs_attention:
            item.setForeground(palette.text_primary)
            return
        item.setForeground(palette.text_secondary)

    def _sync_suggestions_empty(self) -> None:
        """Show a hint when the suggestions list has no rows."""
        if self._suggestions.count():
            self._suggestions_stack.setCurrentWidget(self._suggestions)
            return
        if self._file_list.count() == 0:
            self._suggestions_empty.setText("No suggestions — working tree is clean.")
        elif self._suggestion_filter.strip():
            self._suggestions_empty.setText("No suggestions match the commit title.")
        else:
            self._suggestions_empty.setText("No suggestions for the selected files.")
        self._suggestions_stack.setCurrentWidget(self._suggestions_empty)

    def _toast(self, message: str) -> None:
        ToastNotification(message, duration=2000, parent=self)

    def _update_commit_enabled(self) -> None:
        enabled = (
            not self._busy
            and self._current_repo() is not None
            and bool(self._checked_paths())
            and bool(self._subject.text().strip())
        )
        self._commit_button.setEnabled(enabled)
        status = self._current_status()
        is_local = status is not None and status.access_kind == "local"
        # Local repos have no remote: hide push actions and make Commit the primary.
        self._commit_push_button.setVisible(not is_local)
        self._push_button.setVisible(not is_local)
        self._commit_emphasized = is_local
        self._style_commit_button()
        self._commit_button.setDefault(is_local)
        self._commit_push_button.setDefault(not is_local)
        can_commit_push = enabled and status is not None and status.access_kind == "public"
        self._commit_push_button.setEnabled(can_commit_push)
        self._commit_push_button.setToolTip(self._commit_push_tooltip(status, can_commit=enabled))
        can_push = not self._busy and status is not None and status.access_kind == "public" and status.unpushed > 0
        self._push_button.setEnabled(can_push)
        self._push_button.setToolTip(self._push_tooltip(status))
        # Accent Push when the tree is clean and only a public push remains.
        self._push_emphasized = can_push and self._file_list.count() == 0
        self._style_push_button()
        self._unpushed_push.setEnabled(can_push)
        self._desktop_button.setEnabled(self._current_repo() is not None and not self._busy)
        self._check_button.setEnabled(self._current_repo() is not None and not self._busy)
        self._rescan_button.setEnabled(not self._busy)
        self._add_button.setEnabled(not self._busy)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, repos: Sequence[Path], parent: QWidget | None = None, *, initial_statuses: Sequence[DirtyRepoStatus] | None = None, quick_paste_db: str | Path | None = None, on_line: Callable[[str], None] | None = None) -> None
```

Build the window with an initial dirty-repo path list.

Pass `initial_statuses` from the action scan to skip a second full
Git pass on the UI thread before the first paint.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        repos: Sequence[Path],
        parent: QWidget | None = None,
        *,
        initial_statuses: Sequence[DirtyRepoStatus] | None = None,
        quick_paste_db: str | Path | None = None,
        on_line: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("dirtyReposCommitWindow")
        self.setWindowTitle("Git commit")
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)  # noqa: FBT003
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setProperty(OVERLAY_CAPTION_PROPERTY, True)  # noqa: FBT003
        self.setMinimumSize(960, 640)
        apply_window_icon(self)
        prepare_fluent_app_window(self)

        self._on_line = on_line
        self._quick_paste_db = quick_paste_db
        self._quick_paste: list[str] = []
        self._statuses: list[DirtyRepoStatus] = []
        self._history_by_repo: dict[Path, list[CommitHistoryEntry]] = {}
        self._suggestion_subjects: list[str] = []
        self._suggestion_filter = ""
        self._applying_suggestion = False
        self._busy = False
        self._workers: list[_FnWorker] = []
        self._win11_caption = False
        self._suppress_file_signals = False
        self._visibility_generation = 0
        self._commit_summary = CommitDaySummary(today=DayCommitCounts(), yesterday=DayCommitCounts())
        self._commit_summary_running = False
        self._commit_summary_pending = False
        self._push_emphasized = False
        self._commit_emphasized = False

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.tabWidget = QTabWidget(self)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setDocumentMode(True)

        body = QWidget(self.tabWidget)
        body.setObjectName("dirtyReposCommitBody")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(SPACE_XL, SPACE_M, SPACE_XL, SPACE_XL)
        body_layout.setSpacing(SPACE_M)

        header = QHBoxLayout()
        header.setSpacing(SPACE_S)
        self._status_label = FluentText("", body, role=TextRole.SECONDARY)
        header.addWidget(self._status_label, 1)
        self._add_button = FluentPushButton("Add repositories", body, icon="folder-plus")
        self._add_button.setToolTip("Add a repository or a folder to config.json")
        self._add_button.clicked.connect(self._on_add_repositories)
        header.addWidget(self._add_button)
        self._check_button = FluentPushButton("Check", body, icon="refresh-cw")
        self._check_button.setToolTip("Re-check the selected repository")
        self._check_button.clicked.connect(self._check_current_repo)
        header.addWidget(self._check_button)
        self._rescan_button = FluentPushButton("Check all repositories", body, icon="refresh-cw")
        self._rescan_button.setToolTip("Scan every repository under paths_git_roots")
        self._rescan_button.clicked.connect(self._rescan_all_repos)
        header.addWidget(self._rescan_button)
        body_layout.addLayout(header)

        self._splitter = FluentSplitter(Qt.Orientation.Horizontal, body)
        polish_fluent_splitter(self._splitter)

        left = QWidget(self._splitter)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, SPACE_S, 0)
        left_layout.setSpacing(SPACE_S)
        left_layout.addWidget(FluentText("Repositories", left, role=TextRole.SECONDARY))
        self._repo_list = FluentListWidget(left, compact=True)
        self._repo_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._repo_list.currentItemChanged.connect(self._on_repo_changed)
        left_layout.addWidget(self._repo_list, 1)
        left_layout.addWidget(self._build_commit_summary(left))
        self._splitter.addWidget(left)

        middle = QWidget(self._splitter)
        middle_layout = QVBoxLayout(middle)
        middle_layout.setContentsMargins(SPACE_S, 0, SPACE_S, 0)
        middle_layout.setSpacing(SPACE_S)
        middle_layout.addWidget(FluentText("Changed files", middle, role=TextRole.SECONDARY))
        self._file_list = _CheckableFileList(middle)
        self._file_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._file_list.itemChanged.connect(self._on_file_item_changed)
        self._file_list.currentItemChanged.connect(self._on_file_focus_changed)
        self._file_list.copy_path_clicked.connect(self._on_copy_file_path_clicked)
        self._file_list.customContextMenuRequested.connect(self._on_file_context_menu)
        self._files_stack, self._files_empty = _empty_stack(
            self._file_list,
            "No changed files.\nWorking tree is clean.",
            middle,
        )
        middle_layout.addWidget(self._files_stack, 1)

        middle_layout.addWidget(FluentText("Commit title", middle, role=TextRole.SECONDARY))
        self._subject = FluentLineEdit(middle, placeholder="Commit message")
        self._subject.textChanged.connect(self._on_subject_edited)
        self._subject.installEventFilter(self)
        middle_layout.addWidget(self._subject)

        middle_layout.addWidget(FluentText("Suggestions", middle, role=TextRole.SECONDARY))
        self._suggestions = FluentListWidget(middle, compact=True)
        self._suggestions.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._suggestions.setItemDelegate(_SuggestionFilterDelegate(self._suggestions))
        self._suggestions.itemClicked.connect(self._on_suggestion_clicked)
        self._suggestions_stack, self._suggestions_empty = _empty_stack(
            self._suggestions,
            "No suggestions — working tree is clean.",
            middle,
        )
        middle_layout.addWidget(self._suggestions_stack, 1)

        buttons = QHBoxLayout()
        buttons.setSpacing(SPACE_S)
        # Qt treats a single "&" as a mnemonic; "&&" shows a literal ampersand.
        self._commit_push_button = FluentPrimaryButton("Commit && push", middle, icon="arrow-up-from-line")
        self._commit_push_button.setDefault(True)
        self._commit_push_button.clicked.connect(self._on_commit_and_push)
        self._commit_button = FluentPushButton("Commit", middle)
        self._commit_button.clicked.connect(self._on_commit)
        bind_theme(self._commit_button, self._style_commit_button)
        self._push_button = FluentPushButton("Push", middle, icon="arrow-up-from-line")
        self._push_button.clicked.connect(self._on_push)
        bind_theme(self._push_button, self._style_push_button)
        self._desktop_button = FluentPushButton("Open in GitHub Desktop", middle)
        self._desktop_button.clicked.connect(self._on_open_desktop)
        buttons.addWidget(self._commit_push_button)
        buttons.addWidget(self._commit_button)
        buttons.addWidget(self._push_button)
        buttons.addWidget(self._desktop_button)
        buttons.addStretch(1)
        middle_layout.addLayout(buttons)
        self._splitter.addWidget(middle)

        right = QWidget(self._splitter)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(SPACE_S, 0, 0, 0)
        right_layout.setSpacing(SPACE_S)
        right_layout.addWidget(FluentText("Diff", right, role=TextRole.SECONDARY))
        self._right_stack = QStackedWidget(right)
        self._diff = GitDiffEdit(self._right_stack)
        self._diff.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._diff_empty = _empty_hint(
            self._right_stack,
            "No diff to show.\nSelect a changed file to view its diff.",
        )
        self._unpushed_note = QWidget(self._right_stack)
        note_layout = QVBoxLayout(self._unpushed_note)
        note_layout.setContentsMargins(SPACE_M, SPACE_M, SPACE_M, SPACE_M)
        note_layout.setSpacing(SPACE_M)
        self._unpushed_label = FluentText("", self._unpushed_note, word_wrap=True)
        self._unpushed_hint = FluentText(
            "Nothing to commit in this repository.",
            self._unpushed_note,
            role=TextRole.SECONDARY,
            word_wrap=True,
        )
        # Accent primary: this note only appears when the tree is clean and push remains.
        self._unpushed_push = FluentPrimaryButton("Push these commits", self._unpushed_note, icon="arrow-up-from-line")
        self._unpushed_push.clicked.connect(self._on_push)
        note_layout.addWidget(self._unpushed_label)
        note_layout.addWidget(self._unpushed_hint)
        note_row = QHBoxLayout()
        note_row.setSpacing(SPACE_S)
        note_row.addWidget(self._unpushed_push)
        note_row.addStretch(1)
        note_layout.addLayout(note_row)
        note_layout.addStretch(1)
        self._right_stack.addWidget(self._diff)
        self._right_stack.addWidget(self._diff_empty)
        self._right_stack.addWidget(self._unpushed_note)
        self._right_stack.setCurrentWidget(self._diff_empty)
        right_layout.addWidget(self._right_stack, 1)
        self._splitter.addWidget(right)

        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 0)
        self._splitter.setStretchFactor(2, 1)
        self._splitter.setCollapsible(0, False)  # noqa: FBT003
        self._splitter.setCollapsible(1, False)  # noqa: FBT003
        self._splitter.setCollapsible(2, False)  # noqa: FBT003
        show_splitter_hairlines((self._splitter,))
        sizes = load_splitter_sizes(_SPLITTER_KEY, _SPLITTER_DEFAULT)
        self._splitter.setSizes(sizes)
        self._splitter.splitterMoved.connect(self._schedule_splitter_save)
        body_layout.addWidget(self._splitter, 1)

        self._charts_page = GitCommitChartsPage(self.tabWidget)
        self.tabWidget.addTab(body, "Commit")
        self.tabWidget.addTab(self._charts_page, "Charts")
        root.addWidget(self.tabWidget, 1)
        install_fluent_app_window(self)
        self._win11_caption = install_win11_caption(self)

        self._splitter_save_timer = QTimer(self)
        self._splitter_save_timer.setSingleShot(True)
        self._splitter_save_timer.setInterval(_SPLITTER_SAVE_DELAY_MS)
        self._splitter_save_timer.timeout.connect(self._save_splitter_sizes)

        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(_REFRESH_MS)
        self._refresh_timer.timeout.connect(self._refresh_known_dirty)

        if initial_statuses is not None:
            self._set_statuses(list(initial_statuses))
        else:
            initial = [Path(path).resolve() for path in repos]
            self._set_statuses(refresh_repo_statuses(initial))
        self._load_quick_paste_async()
        # Defer the today/yesterday strip so the window can paint first.
        QTimer.singleShot(0, self._refresh_commit_summary)
        self._refresh_timer.start()
        apply_app_window_size_and_position(self)
        self._update_commit_enabled()
```

</details>

### ⚙️ Method `closeEvent`

```python
def closeEvent(self, event: Any) -> None
```

Stop timers, join workers, and clear the singleton when closing.

<details>
<summary>Code:</summary>

```python
def closeEvent(self, event: Any) -> None:  # noqa: N802
        self.stop_background_workers()
        self._save_splitter_sizes()
        global _active_window  # noqa: PLW0603
        if _active_window is self:
            _active_window = None
        super().closeEvent(event)
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Arrow keys in the commit title walk matching suggestions, like Quick paste.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self._subject and event.type() == QEvent.Type.KeyPress and isinstance(event, QKeyEvent):
            if event.key() == Qt.Key.Key_Down:
                self._move_suggestion(1)
                return True
            if event.key() == Qt.Key.Key_Up:
                self._move_suggestion(-1)
                return True
        return super().eventFilter(watched, event)
```

</details>

### ⚙️ Method `nativeEvent`

```python
def nativeEvent(self, event_type: Any, message: Any) -> tuple[bool, int]
```

Keep caption drag and edge resize on Windows.

<details>
<summary>Code:</summary>

```python
def nativeEvent(self, event_type: Any, message: Any) -> tuple[bool, int]:  # noqa: N802
        handled = try_handle_win11_caption_native_event(self, event_type, message)
        if handled is not None:
            return handled
        return cast("tuple[bool, int]", super().nativeEvent(event_type, message))
```

</details>

### ⚙️ Method `replace_repos`

```python
def replace_repos(self, repos: Sequence[Path], *, initial_statuses: Sequence[DirtyRepoStatus] | None = None, on_line: Callable[[str], None] | None = None) -> None
```

Replace the dirty-repo list (used when the action rescans while open).

<details>
<summary>Code:</summary>

```python
def replace_repos(
        self,
        repos: Sequence[Path],
        *,
        initial_statuses: Sequence[DirtyRepoStatus] | None = None,
        on_line: Callable[[str], None] | None = None,
    ) -> None:
        if on_line is not None:
            self._on_line = on_line
        if initial_statuses is not None:
            self._set_statuses(list(initial_statuses))
            return
        initial = [Path(path).resolve() for path in repos]
        self._set_statuses(refresh_repo_statuses(initial))
```

</details>

### ⚙️ Method `stop_background_workers`

```python
def stop_background_workers(self) -> None
```

Join Git/commit and Charts QThreads before this window is destroyed.

<details>
<summary>Code:</summary>

```python
def stop_background_workers(self) -> None:
        self._refresh_timer.stop()
        self._splitter_save_timer.stop()
        self._charts_page.stop_background_work()
        for worker in list(self._workers):
            if worker.isRunning() and not worker.wait(3000):
                worker.terminate()
                worker.wait(1000)
        self._workers.clear()
```

</details>

## 🔧 Function `show_dirty_repos_commit_window`

```python
def show_dirty_repos_commit_window(repos: Sequence[Path], parent: QWidget | None = None, *, initial_statuses: Sequence[DirtyRepoStatus] | None = None, quick_paste_db: str | Path | None = None, on_line: Callable[[str], None] | None = None) -> DirtyReposCommitWindow
```

Show or raise the singleton dirty-repos commit window.

When `initial_statuses` comes from the same scan that produced `repos`,
the window skips a duplicate Git refresh before the first paint.

<details>
<summary>Code:</summary>

```python
def show_dirty_repos_commit_window(
    repos: Sequence[Path],
    parent: QWidget | None = None,
    *,
    initial_statuses: Sequence[DirtyRepoStatus] | None = None,
    quick_paste_db: str | Path | None = None,
    on_line: Callable[[str], None] | None = None,
) -> DirtyReposCommitWindow:
    global _active_window  # noqa: PLW0603
    if _active_window is not None:
        try:
            if _active_window.isVisible():
                _active_window.replace_repos(
                    repos,
                    initial_statuses=initial_statuses,
                    on_line=on_line,
                )
                _active_window.raise_()
                _active_window.activateWindow()
                return _active_window
        except RuntimeError:
            _active_window = None
    window = DirtyReposCommitWindow(
        repos,
        parent,
        initial_statuses=initial_statuses,
        quick_paste_db=quick_paste_db,
        on_line=on_line,
    )
    _active_window = window
    window.show()
    window.raise_()
    window.activateWindow()
    return window
```

</details>

## 🔧 Function `stop_active_git_commit_window`

```python
def stop_active_git_commit_window() -> None
```

Join Git commit window workers and close the singleton (tray Exit / quit).

<details>
<summary>Code:</summary>

```python
def stop_active_git_commit_window() -> None:
    window = _active_window
    if window is None:
        return
    window.stop_background_workers()
    window.close()
```

</details>
