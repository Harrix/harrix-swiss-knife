---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `name_git_commit_with_ai.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnNameGitCommitWithAI`](#%EF%B8%8F-class-onnamegitcommitwithai)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnNameGitCommitWithAI`

```python
class OnNameGitCommitWithAI(ActionBase)
```

Turn a free-form change description into a styled commit subject.

<details>
<summary>Code:</summary>

```python
class OnNameGitCommitWithAI(ActionBase):

    icon = "🏷️"
    title = "Name Git commit with AI…"
    bold_title = False
    cli_available = False
    quick_launcher = True

    @ActionBase.handle_exceptions("naming a Git commit with AI")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Ask for a description, then copy the AI subject to the clipboard."""
        description = self.dialogs.get_text_textarea(
            "Name Git commit",
            "Describe what this commit does. Any language is fine.",
        )
        if description is None:
            return

        try:
            prompt_text = build_git_commit_subject_prompt(description, self.config)
        except ValueError as exc:
            show_bothub_prompt_build_error(None, exc)
            return

        def on_success(response_text: str) -> None:
            subject = normalize_commit_subject(response_text)
            if not subject:
                message_box.critical(None, "AI Error", "Empty commit title from AI.")
                return
            self.text_to_clipboard(subject)
            self.show_text_multiline(subject, title="Commit title (copied to clipboard)")

        def on_error(message: str) -> None:
            message_box.critical(None, "AI Error", message)

        run_bothub_request(
            None,
            self.config,
            prompt_text,
            on_success,
            on_error=on_error,
        )
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Ask for a description, then copy the AI subject to the clipboard.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        description = self.dialogs.get_text_textarea(
            "Name Git commit",
            "Describe what this commit does. Any language is fine.",
        )
        if description is None:
            return

        try:
            prompt_text = build_git_commit_subject_prompt(description, self.config)
        except ValueError as exc:
            show_bothub_prompt_build_error(None, exc)
            return

        def on_success(response_text: str) -> None:
            subject = normalize_commit_subject(response_text)
            if not subject:
                message_box.critical(None, "AI Error", "Empty commit title from AI.")
                return
            self.text_to_clipboard(subject)
            self.show_text_multiline(subject, title="Commit title (copied to clipboard)")

        def on_error(message: str) -> None:
            message_box.critical(None, "AI Error", message)

        run_bothub_request(
            None,
            self.config,
            prompt_text,
            on_success,
            on_error=on_error,
        )
```

</details>
