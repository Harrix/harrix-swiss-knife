---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `engine.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `SpellEngine`](#%EF%B8%8F-class-spellengine)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `add_to_user_dictionary`](#%EF%B8%8F-method-add_to_user_dictionary)
  - [⚙️ Method `ensure_loaded`](#%EF%B8%8F-method-ensure_loaded)
  - [⚙️ Method `load_error (property)`](#%EF%B8%8F-method-load_error-property)
  - [⚙️ Method `lookup`](#%EF%B8%8F-method-lookup)
  - [⚙️ Method `reload_user_dictionary`](#%EF%B8%8F-method-reload_user_dictionary)
  - [⚙️ Method `suggest`](#%EF%B8%8F-method-suggest)
  - [⚙️ Method `user_words (property)`](#%EF%B8%8F-method-user_words-property)
- [🔧 Function `bundled_dictionaries_dir`](#-function-bundled_dictionaries_dir)
- [🔧 Function `get_spell_engine`](#-function-get_spell_engine)
- [🔧 Function `reset_spell_engine_for_tests`](#-function-reset_spell_engine_for_tests)

</details>

## 🏛️ Class `SpellEngine`

```python
class SpellEngine
```

Lookup words against English, Russian, and the user dictionary (OR).

<details>
<summary>Code:</summary>

```python
class SpellEngine:

    def __init__(self, dictionaries_dir: Path | None = None, user_dict_path: Path | None = None) -> None:
        """Create an unloaded engine; call `ensure_loaded` before lookup."""
        self._dictionaries_dir = dictionaries_dir if dictionaries_dir is not None else bundled_dictionaries_dir()
        self._user_dict_path = user_dict_path
        self._dicts: list[Dictionary] = []
        self._user_words: set[str] = set()
        self._user_words_folded: set[str] = set()
        self._loaded = False
        self._load_error: str | None = None

    def add_to_user_dictionary(self, word: str) -> bool:
        """Persist `word` in the personal dictionary and refresh in-memory set.

        Returns:

        - `bool`: `True` when the word was added (or already present).

        """
        cleaned = word.strip()
        if not cleaned:
            return False
        self._set_user_words(user_dict_mod.add_user_word(cleaned, self._user_dict_path))
        return True

    def ensure_loaded(self) -> bool:
        """Load Hunspell dictionaries and the user word list once.

        Returns:

        - `bool`: `True` when at least one language dictionary is ready.

        """
        if self._loaded:
            return bool(self._dicts)
        self._loaded = True
        self._set_user_words(user_dict_mod.load_user_words(self._user_dict_path))
        try:
            dictionary_cls = _import_dictionary_class()
        except ImportError as exc:
            self._load_error = str(exc)
            log.warning("%s", self._load_error)
            return False
        for name in ("en_US", "ru_RU"):
            stem = self._dictionaries_dir / name
            if not stem.with_suffix(".dic").is_file() or not stem.with_suffix(".aff").is_file():
                log.warning("Spellcheck dictionary missing: %s", stem)
                continue
            try:
                self._dicts.append(dictionary_cls.from_files(str(stem)))
            except Exception:
                log.exception("Failed to load spellcheck dictionary %s", stem)
        if not self._dicts:
            self._load_error = self._load_error or f"No spellcheck dictionaries in {self._dictionaries_dir}"
            log.error("%s", self._load_error)
            return False
        return True

    @property
    def load_error(self) -> str | None:
        """Return a load failure message, or `None` when dictionaries loaded."""
        return self._load_error

    def lookup(self, word: str) -> bool:
        """Return `True` when `word` is in en, ru, or the personal dictionary."""
        if not word:
            return True
        if not self.ensure_loaded():
            return True
        if word in self._user_words or word.casefold() in self._user_words_folded:
            return True
        for dictionary in self._dicts:
            try:
                if dictionary.lookup(word):
                    return True
            except Exception:
                log.exception("Spellcheck lookup failed for %r", word)
        return False

    def reload_user_dictionary(self) -> None:
        """Reload personal words from disk (keeps Hunspell dictionaries)."""
        self._set_user_words(user_dict_mod.load_user_words(self._user_dict_path))

    def suggest(self, word: str, *, limit: int = 7) -> list[str]:
        """Return up to `limit` unique suggestions from en and ru dictionaries."""
        cleaned = word.strip()
        if not cleaned or not self.ensure_loaded() or limit <= 0:
            return []
        seen: set[str] = {cleaned, cleaned.casefold()}
        suggestions: list[str] = []
        for dictionary in self._dicts:
            try:
                for candidate in dictionary.suggest(cleaned):
                    if not candidate or candidate.casefold() in seen:
                        continue
                    seen.add(candidate.casefold())
                    suggestions.append(candidate)
                    if len(suggestions) >= limit:
                        return suggestions
            except Exception:
                log.exception("Spellcheck suggest failed for %r", cleaned)
        return suggestions

    @property
    def user_words(self) -> set[str]:
        """Return a copy of the in-memory personal dictionary."""
        return set(self._user_words)

    def _set_user_words(self, words: set[str]) -> None:
        self._user_words = words
        self._user_words_folded = {w.casefold() for w in words}
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, dictionaries_dir: Path | None = None, user_dict_path: Path | None = None) -> None
```

Create an unloaded engine; call [`ensure_loaded`](#%EF%B8%8F-method-ensure_loaded) before lookup.

<details>
<summary>Code:</summary>

```python
def __init__(self, dictionaries_dir: Path | None = None, user_dict_path: Path | None = None) -> None:
        self._dictionaries_dir = dictionaries_dir if dictionaries_dir is not None else bundled_dictionaries_dir()
        self._user_dict_path = user_dict_path
        self._dicts: list[Dictionary] = []
        self._user_words: set[str] = set()
        self._user_words_folded: set[str] = set()
        self._loaded = False
        self._load_error: str | None = None
```

</details>

### ⚙️ Method `add_to_user_dictionary`

```python
def add_to_user_dictionary(self, word: str) -> bool
```

Persist `word` in the personal dictionary and refresh in-memory set.

Returns:

- `bool`: `True` when the word was added (or already present).

<details>
<summary>Code:</summary>

```python
def add_to_user_dictionary(self, word: str) -> bool:
        cleaned = word.strip()
        if not cleaned:
            return False
        self._set_user_words(user_dict_mod.add_user_word(cleaned, self._user_dict_path))
        return True
```

</details>

### ⚙️ Method `ensure_loaded`

```python
def ensure_loaded(self) -> bool
```

Load Hunspell dictionaries and the user word list once.

Returns:

- `bool`: `True` when at least one language dictionary is ready.

<details>
<summary>Code:</summary>

```python
def ensure_loaded(self) -> bool:
        if self._loaded:
            return bool(self._dicts)
        self._loaded = True
        self._set_user_words(user_dict_mod.load_user_words(self._user_dict_path))
        try:
            dictionary_cls = _import_dictionary_class()
        except ImportError as exc:
            self._load_error = str(exc)
            log.warning("%s", self._load_error)
            return False
        for name in ("en_US", "ru_RU"):
            stem = self._dictionaries_dir / name
            if not stem.with_suffix(".dic").is_file() or not stem.with_suffix(".aff").is_file():
                log.warning("Spellcheck dictionary missing: %s", stem)
                continue
            try:
                self._dicts.append(dictionary_cls.from_files(str(stem)))
            except Exception:
                log.exception("Failed to load spellcheck dictionary %s", stem)
        if not self._dicts:
            self._load_error = self._load_error or f"No spellcheck dictionaries in {self._dictionaries_dir}"
            log.error("%s", self._load_error)
            return False
        return True
```

</details>

### ⚙️ Method `load_error (property)`

```python
def load_error(self) -> str | None
```

Return a load failure message, or `None` when dictionaries loaded.

<details>
<summary>Code:</summary>

```python
def load_error(self) -> str | None:
        return self._load_error
```

</details>

### ⚙️ Method `lookup`

```python
def lookup(self, word: str) -> bool
```

Return `True` when `word` is in en, ru, or the personal dictionary.

<details>
<summary>Code:</summary>

```python
def lookup(self, word: str) -> bool:
        if not word:
            return True
        if not self.ensure_loaded():
            return True
        if word in self._user_words or word.casefold() in self._user_words_folded:
            return True
        for dictionary in self._dicts:
            try:
                if dictionary.lookup(word):
                    return True
            except Exception:
                log.exception("Spellcheck lookup failed for %r", word)
        return False
```

</details>

### ⚙️ Method `reload_user_dictionary`

```python
def reload_user_dictionary(self) -> None
```

Reload personal words from disk (keeps Hunspell dictionaries).

<details>
<summary>Code:</summary>

```python
def reload_user_dictionary(self) -> None:
        self._set_user_words(user_dict_mod.load_user_words(self._user_dict_path))
```

</details>

### ⚙️ Method `suggest`

```python
def suggest(self, word: str, *, limit: int = 7) -> list[str]
```

Return up to `limit` unique suggestions from en and ru dictionaries.

<details>
<summary>Code:</summary>

```python
def suggest(self, word: str, *, limit: int = 7) -> list[str]:
        cleaned = word.strip()
        if not cleaned or not self.ensure_loaded() or limit <= 0:
            return []
        seen: set[str] = {cleaned, cleaned.casefold()}
        suggestions: list[str] = []
        for dictionary in self._dicts:
            try:
                for candidate in dictionary.suggest(cleaned):
                    if not candidate or candidate.casefold() in seen:
                        continue
                    seen.add(candidate.casefold())
                    suggestions.append(candidate)
                    if len(suggestions) >= limit:
                        return suggestions
            except Exception:
                log.exception("Spellcheck suggest failed for %r", cleaned)
        return suggestions
```

</details>

### ⚙️ Method `user_words (property)`

```python
def user_words(self) -> set[str]
```

Return a copy of the in-memory personal dictionary.

<details>
<summary>Code:</summary>

```python
def user_words(self) -> set[str]:
        return set(self._user_words)
```

</details>

## 🔧 Function `bundled_dictionaries_dir`

```python
def bundled_dictionaries_dir() -> Path
```

Return the directory that holds bundled `.aff` / `.dic` files.

<details>
<summary>Code:</summary>

```python
def bundled_dictionaries_dir() -> Path:
    base = Path(__file__).resolve().parent.parent / "assets" / "dictionaries"
    nested = base / "files"
    if (nested / "en_US.dic").is_file() and (nested / "en_US.aff").is_file():
        return nested
    return base
```

</details>

## 🔧 Function `get_spell_engine`

```python
def get_spell_engine() -> SpellEngine
```

Return the process-wide spellcheck engine (lazy singleton).

<details>
<summary>Code:</summary>

```python
def get_spell_engine() -> SpellEngine:
    global _ENGINE  # noqa: PLW0603
    with _ENGINE_LOCK:
        if _ENGINE is None:
            _ENGINE = SpellEngine()
        return _ENGINE
```

</details>

## 🔧 Function `reset_spell_engine_for_tests`

```python
def reset_spell_engine_for_tests() -> None
```

Clear the singleton (tests only).

<details>
<summary>Code:</summary>

```python
def reset_spell_engine_for_tests() -> None:
    global _ENGINE  # noqa: PLW0603
    with _ENGINE_LOCK:
        _ENGINE = None
```

</details>
