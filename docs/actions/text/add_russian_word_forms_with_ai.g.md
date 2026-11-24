---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `add_russian_word_forms_with_ai.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnAddRussianWordFormsWithAI`](#%EF%B8%8F-class-onaddrussianwordformswithai)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnAddRussianWordFormsWithAI`

```python
class OnAddRussianWordFormsWithAI(ActionBase)
```

Expand a Russian lemma into forms and add them to the user dictionary.

<details>
<summary>Code:</summary>

```python
class OnAddRussianWordFormsWithAI(ActionBase):

    icon = "📖"
    title = "Add Russian word forms with AI…"
    bold_title = False
    cli_available = False
    quick_launcher = True

    @ActionBase.handle_exceptions("adding Russian word forms with AI")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Ask for a word, generate forms with AI, then merge into spellcheck."""
        self._run(initial_word=kwargs.get("initial_word"))

    def _run(self, *, initial_word: str | None = None) -> None:
        word = (initial_word or "").strip()
        if not word:
            entered = self.dialogs.get_text_input(
                "Russian word forms",
                "Enter a Russian word (lemma):",
            )
            if entered is None:
                return
            word = entered.strip()
        if not word:
            self.show_toast("❌ Word is empty.", duration=4000)
            return

        try:
            prompt_text = build_russian_word_forms_prompt(word, self.config)
        except ValueError as exc:
            show_bothub_prompt_build_error(None, exc)
            return

        def on_success(response_text: str) -> None:
            forms = parse_russian_word_forms(response_text, lemma=word)
            if not forms:
                message_box.critical(None, "AI Error", "No word forms in the AI response.")
                return
            forms_text = "\n".join(forms)
            self.text_to_clipboard(forms_text)
            edited = self.dialogs.get_text_textarea(
                "Word forms",
                "Review the forms (one per line), then click OK to add them to the spellcheck dictionary.",
                default_text=forms_text,
                copy_button=True,
            )
            if edited is None:
                return
            final_forms = parse_russian_word_forms(edited, lemma=word)
            if not final_forms:
                self.show_toast("❌ No word forms to add.", duration=4000)
                return
            before = load_user_words()
            add_user_words(final_forms)
            get_spell_engine().reload_user_dictionary()
            added = [form for form in final_forms if form not in before]
            already = len(final_forms) - len(added)
            self.add_line(
                f"📖 `{word}`: added {len(added)} form(s) to the spellcheck dictionary ({already} already present).",
            )
            self.show_toast(
                f"✅ Added {len(added)} form(s) for `{word}` ({already} already present).",
                duration=5000,
            )

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

Ask for a word, generate forms with AI, then merge into spellcheck.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self._run(initial_word=kwargs.get("initial_word"))
```

</details>
