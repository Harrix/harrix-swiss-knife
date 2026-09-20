---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `recognize_table_with_ai.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnRecognizeTableWithAI`](#%EF%B8%8F-class-onrecognizetablewithai)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnRecognizeTableWithAI`

```python
class OnRecognizeTableWithAI(ActionBase)
```

Recognize a table from selected images via AI and copy it for Excel.

<details>
<summary>Code:</summary>

```python
class OnRecognizeTableWithAI(ActionBase):

    icon = "📊"
    title = "Recognize table (AI)…"
    bold_title = False

    _PREVIEW_MAX_LEN = 120

    @ActionBase.handle_exceptions("recognizing table with AI")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Select images (or use `image_paths`), extract tables with AI, and show them."""
        image_paths = kwargs.get("image_paths")
        if image_paths:
            selected = [Path(path) for path in image_paths]
        else:
            selected = self.dialogs.get_images_from_picker("Select table images")
        if not selected:
            return

        self._image_paths = [Path(path) for path in selected]
        self.result_folder = self._image_paths[0].parent
        self._tables: list[ExtractedTable] = []
        self._bothub_state = BothubRequestState()
        self._model = get_image_table_model(self.config)
        self.add_line(f"🤖 Model: {self._model}")
        self._process_image(0)

    def _finish_tables(self) -> None:
        if not self._tables:
            self.add_line("❌ No table recognized")
            self.show_result()
            return

        copy_tables_to_clipboard(self._tables)
        self.add_line("📋 Table copied to clipboard (paste into Excel)")
        title = "Table"
        elapsed = self.elapsed_mm_ss()
        if elapsed is not None:
            title = f"Table — {elapsed}"
        folder = self._image_paths[0].parent
        default_name = suggest_xlsx_filename(self._image_paths, self._tables)
        self.dialogs.show_extracted_tables(
            self._tables,
            title,
            save_default_path=str(folder / default_name),
            open_folder_path=folder,
        )
        self.show_toast(f"✅ Recognized table in {len(self._image_paths)} image(s)")

    def _process_image(self, index: int) -> None:
        total = len(self._image_paths)
        if index >= total:
            self._finish_tables()
            return

        path = self._image_paths[index]
        self.add_line(f"🔵 [{index + 1}/{total}] {path.name}")

        max_image_side = get_max_image_side(self.config)

        try:
            image_data = image_bytes_and_mime(path, max_image_side=max_image_side)
            prompt_text = build_image_table_prompt(self.config)
        except ValueError as exc:
            show_bothub_prompt_build_error(None, exc)
            return

        def on_error(message: str) -> None:
            message_box.critical(None, "BotHub Error", message)

        def on_success(response_text: str) -> None:
            tables = parse_tables_response(response_text)
            if not tables:
                preview = response_text.strip().replace("\n", " ")
                if len(preview) > self._PREVIEW_MAX_LEN:
                    preview = preview[: self._PREVIEW_MAX_LEN - 3] + "..."
                self.add_line(f"⚠️ No table in response: {preview or '(empty)'}")
            else:
                self._tables.extend(tables)
                first = tables[0]
                preview = first.title or (first.rows[0][0].text if first.rows and first.rows[0] else "")
                self.add_line(f"📊 {preview or 'table'} ({len(tables)} table(s))")
            self._process_image(index + 1)

        run_bothub_request(
            None,
            self.config,
            prompt_text,
            on_success,
            image=image_data,
            model=self._model,
            toast_message=f"Table [{index + 1}/{total}]: {path.name}…",
            is_busy=lambda: self._bothub_state.worker is not None,
            state=self._bothub_state,
            on_error=on_error,
        )
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Select images (or use `image_paths`), extract tables with AI, and show them.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        image_paths = kwargs.get("image_paths")
        if image_paths:
            selected = [Path(path) for path in image_paths]
        else:
            selected = self.dialogs.get_images_from_picker("Select table images")
        if not selected:
            return

        self._image_paths = [Path(path) for path in selected]
        self.result_folder = self._image_paths[0].parent
        self._tables: list[ExtractedTable] = []
        self._bothub_state = BothubRequestState()
        self._model = get_image_table_model(self.config)
        self.add_line(f"🤖 Model: {self._model}")
        self._process_image(0)
```

</details>
