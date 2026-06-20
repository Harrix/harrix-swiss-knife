---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `fix_md_with_quotes.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnFixMDWithQuotes`](#️-class-onfixmdwithquotes)
  - [⚙️ Method `execute`](#️-method-execute)
  - [⚙️ Method `in_thread`](#️-method-in_thread)
  - [⚙️ Method `thread_after`](#️-method-thread_after)

</details>

## 🏛️ Class `OnFixMDWithQuotes`

```python
class OnFixMDWithQuotes(ActionBase)
```

Add author and title information to quote files in a folder.

This action processes quote files in a folder to add author and book information
based on the folder structure. Given a file structure like:

`C:/quotes/Name-Surname/Title-of-book.md`

The action will:

1. Extract author name from the parent folder
2. Extract book title from the filename
3. Format quotes with proper author attribution

Example transformation:

- Before: Plain text quotes separated by `---`
- After: Block quotes with attribution `-- _Name Surname, Title of book_`

<details>
<summary>Code:</summary>

```python
class OnFixMDWithQuotes(ActionBase):

    icon = "❞"
    title = "Fix MD with quotes in …"

    @ActionBase.handle_exceptions("fixing markdown with quotes")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Add author and title information to quote files in a folder."""
        self.dialogs.show_instructions("""Given a file like `C:/test/Name-Surname/Title-of-book.md` with content:

```markdown

# Title of book

Line 1.

Line 2.

---

Line 3.

Line 4.

-- Modified title of book

```

After processing:

```markdown

# Title of book

> Line 1.
> Line 2.
> -- _Name Surname, Title of book_

---

> Line 3.
> Line 4.
> -- _Name Surname, Modified title of book_

```
""")
        self.folder_path = self.dialogs.get_existing_directory("Select folder with quotes", self.config["path_quotes"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("fixing markdown with quotes thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        result = h.file.apply_func(self.folder_path, ".md", h.md.generate_author_book)
        self.add_line(result)

    @ActionBase.handle_exceptions("fixing markdown with quotes thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Add author and title information to quote files in a folder.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.dialogs.show_instructions("""Given a file like `C:/test/Name-Surname/Title-of-book.md` with content:

```markdown

# Title of book

Line 1.

Line 2.

---

Line 3.

Line 4.

-- Modified title of book

```

After processing:

```markdown

# Title of book

> Line 1.
> Line 2.
> -- _Name Surname, Title of book_

---

> Line 3.
> Line 4.
> -- _Name Surname, Modified title of book_

```
""")
        self.folder_path = self.dialogs.get_existing_directory("Select folder with quotes", self.config["path_quotes"])
        if not self.folder_path:
            return

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
        if self.folder_path is None:
            return
        result = h.file.apply_func(self.folder_path, ".md", h.md.generate_author_book)
        self.add_line(result)
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
