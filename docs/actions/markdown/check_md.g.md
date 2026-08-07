---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `check_md.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnCheckMd`](#%EF%B8%8F-class-oncheckmd)
  - [⚙️ Method `check_md_common`](#%EF%B8%8F-method-check_md_common)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnCheckMd`

```python
class OnCheckMd(ActionBase)
```

Check all Markdown files in a folder for errors with Harrix rules.

<details>
<summary>Code:</summary>

```python
class OnCheckMd(ActionBase):

    icon = "🚧"
    title = "Check MD in …"
    cli_available = True
    cli_hint = "md check"

    include_g_md: bool = False

    _RULE_ID_RE = re.compile(r"^H\d+")
    # Location may be `path`, `path:line`, or `path:line:col` (Windows drive-safe via non-greedy path).
    _FORMATTED_ERROR_RE = re.compile(
        r"^(?P<location>.*?): (?P<code>[A-Z]+\d+)(?P<rest>\n  .*| .*|)$",
        re.DOTALL,
    )
    _INCLUDE_G_MD_CHOICE = "Include .g.md files"

    def check_md_common(self) -> None:
        """Check Markdown files in `folder_path` with `selected_rule_ids` and log results."""
        checker = h.md_check.MdChecker()
        if self.folder_path is None:
            return

        md_files = [
            md_file
            for md_file in checker.find_markdown_files(self.folder_path)
            if self.include_g_md or not md_file.name.endswith(".g.md")
        ]

        errors_dict: dict[str, list[str]] = {}
        for md_file in h.file.iter_with_progress(md_files):
            errors = checker.check(md_file, select=self.selected_rule_ids)
            if errors:
                errors_dict[str(md_file)] = errors

        # MdChecker formats errors with a path relative to the git root.
        # Replace that relative prefix with the full absolute path (the dict key).
        all_errors = [
            self._absolutize_checker_error(error, file_path)
            for file_path, file_errors in errors_dict.items()
            for error in file_errors
        ]

        self.last_error_count = len(all_errors)
        if all_errors:
            for index, error in enumerate(all_errors):
                if index:
                    self.add_line("")
                self.add_line(error)
            self.add_line("")
            self.add_line(f"🔢 Count errors = {len(all_errors)}")

            desc_counts = Counter()
            for err in all_errors:
                description = self._error_type_description(err)
                if description:
                    desc_counts[description] += 1

            sorted_stats = sorted(desc_counts.items(), key=lambda x: (-x[1], x[0]))
            stats_lines = [f"  {count}: {desc}" for desc, count in sorted_stats]
            self.add_line("📊 Stats by error type:\n" + "\n".join(stats_lines))

            first_rule_id: str | None = None
            for desc, _count in sorted_stats:
                rule_id_match = self._RULE_ID_RE.match(desc.strip())
                if rule_id_match is not None:
                    first_rule_id = rule_id_match.group(0)
                    break

            if first_rule_id is not None:
                folder_quoted = shlex.quote(str(self.folder_path))
                self.add_line(
                    "💡 Check a single rule — put the rule id in place of <>:\n"
                    f"  {CLI_EXECUTABLE} md check {folder_quoted} --rule <>\n"
                    f"  Example: {CLI_EXECUTABLE} md check {folder_quoted} --rule {first_rule_id}"
                )
        else:
            self.add_line(f"✅ There are no errors in {self.folder_path}.")

    @ActionBase.handle_exceptions("checking markdown folder")
    def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        rule_ids: set[str] | None = None,
        include_g_md: bool = False,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Check all Markdown files in a folder for errors with Harrix rules."""
        if noninteractive and folder_path is None:
            self.handle_error(
                ValueError("folder_path is required when noninteractive is True"),
                self.title,
            )
            return

        if folder_path is not None:
            self.folder_path = Path(folder_path).resolve()
        else:
            self.folder_path = self.dialogs.get_folder_with_choice_option(
                self.config["paths_notes"], self.config["path_notes"]
            )
        if not self.folder_path:
            return

        checker = h.md_check.MdChecker()
        all_rule_ids = checker.all_rules

        if noninteractive:
            self.include_g_md = include_g_md
            if rule_ids is None:
                self.selected_rule_ids = all_rule_ids
            else:
                unknown = rule_ids - set(checker.RULES)
                if unknown:
                    self.handle_error(
                        ValueError(f"Unknown rule id(s): {', '.join(sorted(unknown))}"),
                        self.title,
                    )
                    return
                self.selected_rule_ids = rule_ids
            self.add_line(f"🔵 Starting Markdown check for path: {self.folder_path}")
            self.check_md_common()
            return

        # Convert rules dict to list of rule descriptions for display
        rule_choices = [f"{rule_id}: {description}" for rule_id, description in checker.RULES.items()]
        choices = [self._INCLUDE_G_MD_CHOICE, *rule_choices]

        # Show dialog to select rules (all selected by default; .g.md opt-in)
        selected_rules = self.dialogs.get_checkbox_selection(
            "Select Rules for Markdown Check",
            "Choose which rules to check:",
            choices,
            default_selected=rule_choices,
        )

        if not selected_rules:
            return

        self.include_g_md = self._INCLUDE_G_MD_CHOICE in selected_rules

        # Extract rule IDs from selected descriptions
        self.selected_rule_ids = set()
        for selected_rule in selected_rules:
            if selected_rule == self._INCLUDE_G_MD_CHOICE:
                continue
            # Extract rule ID (e.g., "H001" from "H001: Description")
            rule_id = selected_rule.split(":")[0].strip()
            self.selected_rule_ids.add(rule_id)

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("markdown folder checking thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        self.check_md_common()

    @ActionBase.handle_exceptions("markdown folder checking thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()

    @staticmethod
    def _absolutize_checker_error(error: str, file_path: str) -> str:
        """Replace the relative path prefix with an absolute path; keep multi-line body."""
        match = OnCheckMd._FORMATTED_ERROR_RE.match(error)
        if match is None:
            return error
        location = f"{file_path}{OnCheckMd._line_col_suffix(match.group('location'))}"
        return f"{location}: {match.group('code')}{match.group('rest')}"

    @staticmethod
    def _error_type_description(error: str) -> str | None:
        """Build a short stats key like `H060 Asset file not referenced in Markdown`."""
        match = OnCheckMd._FORMATTED_ERROR_RE.match(error)
        if match is None:
            return None
        code = match.group("code")
        rest = match.group("rest").strip()
        if not rest:
            return code
        summary = rest.split(": ", 1)[0].strip()
        return f"{code} {summary}" if summary else code

    @staticmethod
    def _line_col_suffix(location: str) -> str:
        """Return `:line` / `:line:col` suffix from a checker location, if present."""
        parts = location.split(":")
        if not parts:
            return ""
        if parts[-1].isdigit():
            if len(parts) >= 2 and parts[-2].isdigit():  # noqa: PLR2004
                return f":{parts[-2]}:{parts[-1]}"
            return f":{parts[-1]}"
        return ""
```

</details>

### ⚙️ Method `check_md_common`

```python
def check_md_common(self) -> None
```

Check Markdown files in `folder_path` with `selected_rule_ids` and log results.

<details>
<summary>Code:</summary>

```python
def check_md_common(self) -> None:
        checker = h.md_check.MdChecker()
        if self.folder_path is None:
            return

        md_files = [
            md_file
            for md_file in checker.find_markdown_files(self.folder_path)
            if self.include_g_md or not md_file.name.endswith(".g.md")
        ]

        errors_dict: dict[str, list[str]] = {}
        for md_file in h.file.iter_with_progress(md_files):
            errors = checker.check(md_file, select=self.selected_rule_ids)
            if errors:
                errors_dict[str(md_file)] = errors

        # MdChecker formats errors with a path relative to the git root.
        # Replace that relative prefix with the full absolute path (the dict key).
        all_errors = [
            self._absolutize_checker_error(error, file_path)
            for file_path, file_errors in errors_dict.items()
            for error in file_errors
        ]

        self.last_error_count = len(all_errors)
        if all_errors:
            for index, error in enumerate(all_errors):
                if index:
                    self.add_line("")
                self.add_line(error)
            self.add_line("")
            self.add_line(f"🔢 Count errors = {len(all_errors)}")

            desc_counts = Counter()
            for err in all_errors:
                description = self._error_type_description(err)
                if description:
                    desc_counts[description] += 1

            sorted_stats = sorted(desc_counts.items(), key=lambda x: (-x[1], x[0]))
            stats_lines = [f"  {count}: {desc}" for desc, count in sorted_stats]
            self.add_line("📊 Stats by error type:\n" + "\n".join(stats_lines))

            first_rule_id: str | None = None
            for desc, _count in sorted_stats:
                rule_id_match = self._RULE_ID_RE.match(desc.strip())
                if rule_id_match is not None:
                    first_rule_id = rule_id_match.group(0)
                    break

            if first_rule_id is not None:
                folder_quoted = shlex.quote(str(self.folder_path))
                self.add_line(
                    "💡 Check a single rule — put the rule id in place of <>:\n"
                    f"  {CLI_EXECUTABLE} md check {folder_quoted} --rule <>\n"
                    f"  Example: {CLI_EXECUTABLE} md check {folder_quoted} --rule {first_rule_id}"
                )
        else:
            self.add_line(f"✅ There are no errors in {self.folder_path}.")
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *_args: Any, folder_path: Path | None = None, rule_ids: set[str] | None = None, include_g_md: bool = False, noninteractive: bool = False, **_kwargs: Any) -> None
```

Check all Markdown files in a folder for errors with Harrix rules.

<details>
<summary>Code:</summary>

```python
def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        rule_ids: set[str] | None = None,
        include_g_md: bool = False,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        if noninteractive and folder_path is None:
            self.handle_error(
                ValueError("folder_path is required when noninteractive is True"),
                self.title,
            )
            return

        if folder_path is not None:
            self.folder_path = Path(folder_path).resolve()
        else:
            self.folder_path = self.dialogs.get_folder_with_choice_option(
                self.config["paths_notes"], self.config["path_notes"]
            )
        if not self.folder_path:
            return

        checker = h.md_check.MdChecker()
        all_rule_ids = checker.all_rules

        if noninteractive:
            self.include_g_md = include_g_md
            if rule_ids is None:
                self.selected_rule_ids = all_rule_ids
            else:
                unknown = rule_ids - set(checker.RULES)
                if unknown:
                    self.handle_error(
                        ValueError(f"Unknown rule id(s): {', '.join(sorted(unknown))}"),
                        self.title,
                    )
                    return
                self.selected_rule_ids = rule_ids
            self.add_line(f"🔵 Starting Markdown check for path: {self.folder_path}")
            self.check_md_common()
            return

        # Convert rules dict to list of rule descriptions for display
        rule_choices = [f"{rule_id}: {description}" for rule_id, description in checker.RULES.items()]
        choices = [self._INCLUDE_G_MD_CHOICE, *rule_choices]

        # Show dialog to select rules (all selected by default; .g.md opt-in)
        selected_rules = self.dialogs.get_checkbox_selection(
            "Select Rules for Markdown Check",
            "Choose which rules to check:",
            choices,
            default_selected=rule_choices,
        )

        if not selected_rules:
            return

        self.include_g_md = self._INCLUDE_G_MD_CHOICE in selected_rules

        # Extract rule IDs from selected descriptions
        self.selected_rule_ids = set()
        for selected_rule in selected_rules:
            if selected_rule == self._INCLUDE_G_MD_CHOICE:
                continue
            # Extract rule ID (e.g., "H001" from "H001: Description")
            rule_id = selected_rule.split(":")[0].strip()
            self.selected_rule_ids.add(rule_id)

        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        self.check_md_common()
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Execute code in the main thread after in_thread(). For handling the results of thread execution.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()
```

</details>
