---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `new_markdown_commands.py`

## 🏛️ Class `BuiltinMarkdownCommandsMixin`

```python
class BuiltinMarkdownCommandsMixin
```

Mixin with built-in New Markdown command implementations.

<details>
<summary>Code:</summary>

```python
class BuiltinMarkdownCommandsMixin:

    @ActionBase.handle_exceptions("creating new article")
    def _execute_new_article(self) -> None:
        """Create new article with predefined template."""
        article_name = self.dialogs.get_text_input(
            "Article title", "Enter the name of the article (English, without spaces):", "name-of-article"
        )
        if not article_name:
            return

        article_name = article_name.replace(" ", "-")

        now_local = datetime.now(UTC).astimezone()
        text = self.config["beginning_of_article"].replace(
            "[YEAR]",
            now_local.strftime("%Y"),
        )
        text = text.replace("[NAME]", article_name)
        text = text.replace(
            "[DATE]",
            now_local.strftime("%Y-%m-%d"),
        )
        text += f"\n# {article_name.capitalize().replace('-', ' ')}\n\n\n"

        result, filename = h.md.add_note(Path(self.config["path_articles"]), article_name, text, is_with_images=True)
        self._open_notes_editor(filename, workspace_key="vscode_workspace_articles")
        self.add_line(result)

    @ActionBase.handle_exceptions("creating new diary entry")
    def _execute_new_diary(self, *, diary_root: Path | str | None = None) -> None:
        """Create new diary entry for current date."""
        base = Path(diary_root) if diary_root is not None else Path(self.config["path_diary"])
        result, filename = h.md.add_diary_new_dairy_in_year(base, self.config["beginning_of_md"])
        self._open_notes_editor(filename)
        self.add_line(result)

    @ActionBase.handle_exceptions("creating new cases entry")
    def _execute_new_diary_cases(self, *, cases_root: Path | str | None = None) -> None:
        """Create new cases entry for current month."""
        if cases_root is not None:
            base = Path(cases_root)
            result, filename = h.md.add_diary_new_cases_in_year(base, self.config["beginning_of_md"])
            self._open_notes_editor(filename)
            self.add_line(result)
            return
        path_cases = self.config.get("path_cases")
        if not path_cases:
            self.add_line("❌ path_cases is not configured in config.json.")
            self.show_result()
            return
        result, filename = h.md.add_diary_new_cases_in_year(path_cases, self.config["beginning_of_md"])
        self._open_notes_editor(filename)
        self.add_line(result)

    @ActionBase.handle_exceptions("creating new dream entry")
    def _execute_new_diary_dream(self, *, dream_root: Path | str | None = None) -> None:
        """Create new dream journal entry for current date."""
        base = Path(dream_root) if dream_root is not None else Path(self.config["path_dream"])
        result, filename = h.md.add_diary_new_dream_in_year(base, self.config["beginning_of_md"])
        self._open_notes_editor(filename)
        self.add_line(result)

    @ActionBase.handle_exceptions("creating new memory entry")
    def _execute_new_memory(self) -> None:
        """Create new memory entry for current date."""
        path_memories = self.config.get("path_memories")
        if not path_memories:
            self.add_line("❌ Config key 'path_memories' is not set.")
            return
        result, filename = h.md.add_diary_new_dairy_in_year(path_memories, self.config["beginning_of_md"])
        self._open_notes_editor(filename)
        self.add_line(result)

    @ActionBase.handle_exceptions("creating new note")
    def _execute_new_note(
        self,
        *,
        is_with_images: bool = False,
        folder_path: Path | None = None,
        note_stem: str | None = None,
    ) -> None:
        """Create new general note with user-specified filename."""
        noninteractive = folder_path is not None

        if folder_path is not None:
            if note_stem is None or not str(note_stem).strip():
                self.add_line("❌ Note name is empty.")
                return
            stem_raw = str(note_stem).strip()
            if stem_raw.lower().endswith(".md"):
                stem_raw = stem_raw[:-3]
            heading_stem = stem_raw
            parent: Path = folder_path
        else:
            try:
                temp_config = h.dev.config_load(self.config_path, is_temp=True)
                default_path = temp_config.get(
                    "path_last_note_folder", self.config.get("path_last_note_folder", self.config["path_notes"])
                )
            except (FileNotFoundError, OSError):
                default_path = self.config.get("path_last_note_folder", self.config["path_notes"])

            filename_dialog = self.dialogs.get_save_filename(
                "Save Note", default_path, "Markdown (*.md);;All Files (*)"
            )
            if not filename_dialog:
                return

            heading_stem = filename_dialog.stem
            parent = filename_dialog.parent

        # Temp config should never prevent note creation.
        try:
            temp_config_path = Path(self.temp_config_path)
            temp_config_path.parent.mkdir(parents=True, exist_ok=True)
            if not temp_config_path.exists() or temp_config_path.stat().st_size == 0:
                temp_config_path.write_text("{}", encoding="utf-8")
            h.dev.config_update_value("path_last_note_folder", str(parent), self.config_path, is_temp=True)
        except (FileNotFoundError, OSError) as e:
            self.add_line(f"⚠️ Could not update temp config ({self.temp_config_path}): {e}")

        self.add_line(f"Folder path: {parent}")
        self.add_line(f"File name without extension: {heading_stem}")

        config_folder = h.dev.get_project_root() / "config"
        template_files = self.config.get("note_beginning_templates", [])

        if not template_files:
            self.add_line("❌ No note_beginning_templates configured in config.json.")
            return

        file_contents: dict[str, str] = {}
        file_choices: list[tuple[str, str]] = []
        display_to_template: dict[str, str] = {}
        for template_file in template_files:
            if template_file.startswith("snippet:"):
                file_path_str = template_file[8:]
                file_path = h.dev.get_project_root() / file_path_str
                display_name = Path(file_path_str).name
            else:
                file_path = config_folder / template_file
                display_name = template_file

            if not file_path.exists():
                self.add_line(f"⚠️ Template file not found: {template_file}")
                continue

            try:
                with Path.open(file_path, "r", encoding="utf8") as f:
                    content = f.read()
                file_contents[template_file] = content
                lines = content.split("\n")
                max_count_lines = 10
                preview = "\n".join(lines[:max_count_lines]) + "\n..." if len(lines) > max_count_lines else content
                display_to_template[display_name] = template_file
                file_choices.append((display_name, preview))
            except Exception as e:
                self.add_line(f"❌ Error reading file {template_file}: {e}")
                continue

        if not file_choices:
            self.add_line("❌ No valid beginning template files could be read.")
            return

        if noninteractive:
            selected_template_file = next(iter(file_contents))
            beginning_text = file_contents[selected_template_file]
            self.add_line(f"🔵 Using first beginning template: {selected_template_file}")
        else:
            selected_display_name = self.dialogs.get_choice_from_list_with_descriptions(
                "Select Beginning Template", "Choose a beginning template:", file_choices
            )

            if not selected_display_name:
                return

            selected_template_file = display_to_template[selected_display_name]
            beginning_text = file_contents[selected_template_file]

        text = beginning_text + f"\n# {heading_stem}\n\n\n"
        filename_final = heading_stem.replace("-", "--").replace(" ", "-")

        result, filename = h.md.add_note(parent, filename_final, text, is_with_images=is_with_images)
        self._open_notes_editor(filename)
        self.add_line(result)

    def _execute_new_note_with_images(self) -> None:
        """Create new note with images directory."""
        self._execute_new_note(is_with_images=True)

    @ActionBase.handle_exceptions("processing quotes")
    def _execute_new_quotes(self) -> None:
        """Add new quotes with author and book title."""
        self._execute_new_quotes_format_with_author_and_book()

    def _execute_new_quotes_format_with_author_and_book(self) -> None:
        """Format quotes with specified author and book title via dialog."""
        quotes_folder = self.config.get("path_quotes", "")
        author_books_dict = self._extract_authors_and_books_from_quotes_folder(quotes_folder)
        authors_list = sorted(author_books_dict.keys())

        fields = [
            TemplateField("Author", "combobox", "{{Author:combobox}}", "", options=authors_list),
            TemplateField("Book Title", "combobox", "{{Book Title:combobox}}", "", options=[]),
            TemplateField(
                "Quotes",
                "multiline",
                "{{Quotes:multiline}}",
                (
                    "They can get a big bang out of buying a blanket.\n\n\n"
                    "I just mean that I used to think about old Spencer quite a lot"
                ),
            ),
        ]

        dialog = TemplateDialog(
            fields=fields,
            title="Enter Book, Author and Quotes",
            app_config=self.config,
        )

        author_widget = dialog.widgets.get("Author")
        book_widget = dialog.widgets.get("Book Title")
        if isinstance(author_widget, QComboBox) and isinstance(book_widget, QComboBox):

            def update_book_list(author_text: str) -> None:
                current_book = book_widget.currentText()
                book_widget.clear()

                if hasattr(book_widget, "smart_filter_model"):
                    delattr(book_widget, "smart_filter_model")
                if hasattr(book_widget, "smart_filter_proxy"):
                    delattr(book_widget, "smart_filter_proxy")
                if hasattr(book_widget, "smart_filter_completer"):
                    delattr(book_widget, "smart_filter_completer")
                if hasattr(book_widget, "smart_filter_items"):
                    delattr(book_widget, "smart_filter_items")

                if author_text and author_text in author_books_dict:
                    books = author_books_dict[author_text]
                    book_widget.addItems(books)
                    apply_smart_filtering(book_widget)

                    if current_book:
                        index = book_widget.findText(current_book)
                        if index >= 0:
                            book_widget.setCurrentIndex(index)
                        else:
                            book_widget.setCurrentText(current_book)
                else:
                    book_widget.setCurrentText(current_book or "")

            author_widget.currentTextChanged.connect(update_book_list)

            if author_widget.currentText():
                update_book_list(author_widget.currentText())

        if dialog.exec() != dialog.DialogCode.Accepted:
            self.add_line("❌ Dialog was canceled.")
            self.show_result()
            return

        field_values = dialog.get_field_values()
        if not field_values:
            self.add_line("❌ No field values collected.")
            self.show_result()
            return

        book_title = field_values.get("Book Title", "")
        author = field_values.get("Author", "")
        quotes_content = field_values.get("Quotes", "")

        if not book_title or not author or not quotes_content:
            self.add_line("❌ Book title, author and quotes are required.")
            self.show_result()
            return

        quotes = [q.strip() for q in quotes_content.split("\n\n") if q.strip()]

        formatted_content = ""
        for quote in quotes:
            formatted_content += f"{quote}\n\n{book_title}\n{author}\n\n\n"

        formatted_content = formatted_content.rstrip()

        result = h.md.format_quotes_as_markdown_content(formatted_content)

        quotes_without_header = result
        if quotes_without_header.startswith(f"# {book_title}"):
            lines = quotes_without_header.split("\n")
            for i_original, line in enumerate(lines):
                i = i_original
                if line.strip() == f"# {book_title}":
                    while i + 1 < len(lines) and not lines[i + 1].strip():
                        i += 1
                    quotes_without_header = "\n".join(lines[i + 1 :]).lstrip()
                    break

        success = self._save_quotes_to_file(quotes_without_header, author, book_title)
        if success:
            self.add_line("✅ Quotes saved to file successfully!")
        else:
            self.add_line("❌ Failed to save quotes to file.")

        self.show_result()

    def _extract_authors_and_books_from_quotes_folder(self, quotes_folder: str) -> dict[str, list[str]]:
        """Extract authors and their books from Markdown quote files.

        If folder contains aggregated file `_<FolderName>.g.md` (e.g. `Fiction` -> `_Fiction.g.md`),
        only that file is scanned; otherwise all `*.md` in folder (and subfolders) are scanned.

        """
        author_books: dict[str, set[str]] = {}

        quotes_path = Path(quotes_folder)
        if not quotes_path.exists():
            return {}

        folder_name = quotes_path.name
        aggregated_file = quotes_path / f"_{folder_name}.g.md"
        md_files = [aggregated_file] if aggregated_file.exists() else list(quotes_path.rglob("*.md"))

        pattern = re.compile(r">\s*--\s*_([^_]+?),\s*([^_]+?)_", re.MULTILINE)

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception as e:
                print(f"Warning: Failed to read {md_file}: {e}")
                continue

            matches = pattern.findall(content)
            for author, book in matches:
                author_clean = author.strip()
                book_clean = book.strip()
                if author_clean and not author_clean.startswith("["):
                    if author_clean not in author_books:
                        author_books[author_clean] = set()
                    if book_clean:
                        author_books[author_clean].add(book_clean)

        return {author: sorted(books) for author, books in sorted(author_books.items())}

    def _save_quotes_to_file(self, quotes_content: str, author: str, book_title: str) -> bool:
        """Save quotes to a Markdown file."""
        selected_folder = self.dialogs.get_folder_with_choice_option(
            self.config.get("paths_quotes", []),
            self.config.get("path_quotes", ""),
        )

        if not selected_folder:
            return False

        author_folder_name = "-".join(part.strip() for part in author.split() if part.strip())
        author_folder = selected_folder / author_folder_name
        author_folder.mkdir(exist_ok=True)

        clean_title = book_title.replace("«", "").replace("»", "").replace('"', "").replace("'", "")
        book_filename = "-".join(part.strip() for part in clean_title.split() if part.strip())
        file_path = h.md.note_md_path(author_folder, book_filename)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        header = f"# {book_title}"
        separator = "---"

        if file_path.exists():
            existing_content = file_path.read_text(encoding="utf-8")
            lines = existing_content.split("\n")
            new_lines = []
            header_found = False

            for i, line in enumerate(lines):
                new_lines.append(line)
                if line.strip() == header.strip():
                    header_found = True
                    new_lines.append("")
                    new_lines.append(quotes_content)
                    new_lines.append("")
                    new_lines.append(separator)
                    new_lines.extend(lines[i + 1 :])
                    break

            if not header_found:
                if not existing_content.rstrip().endswith("---"):
                    new_lines.extend(["", separator, "", quotes_content])
                else:
                    new_lines.extend(["", quotes_content])

            content = "\n".join(new_lines)
        else:
            beginning_template = self.config["beginning_of_md"]
            content = f"{beginning_template}\n{header}\n\n{quotes_content}"

        content = content.rstrip() + "\n"
        file_path.write_text(content, encoding="utf-8")
        return True
```

</details>
