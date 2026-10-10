---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `speech_answer.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `answer_speech_question_sync`](#-function-answer_speech_question_sync)
- [🔧 Function `build_speech_answer_prompt`](#-function-build_speech_answer_prompt)
- [🔧 Function `get_speech_answer_prompt_template`](#-function-get_speech_answer_prompt_template)

</details>

## 🔧 Function `answer_speech_question_sync`

```python
def answer_speech_question_sync(input_text: str, config: dict[str, Any]) -> str
```

Send a spoken question to BotHub synchronously and return the answer.

Raises:

- `ValueError`: Configuration errors (prompt or API key).
- [`BotHubApiError`](../bothub_client.g.md#-constant-bothubapierror): API or network failure.

<details>
<summary>Code:</summary>

```python
def answer_speech_question_sync(input_text: str, config: dict[str, Any]) -> str:
    return chat_completion_with_bothub_failover(config, build_speech_answer_prompt(input_text, config))
```

</details>

## 🔧 Function `build_speech_answer_prompt`

```python
def build_speech_answer_prompt(input_text: str, config: dict[str, Any]) -> str
```

Build BotHub prompt that answers a spoken question.

Raises:

- `ValueError`: If prompt template or API key is not configured.

<details>
<summary>Code:</summary>

```python
def build_speech_answer_prompt(input_text: str, config: dict[str, Any]) -> str:
    return build_prompt(
        config,
        "speech_answer",
        {"TEXT": input_text},
        prompt_display_name="speech_answer",
    )
```

</details>

## 🔧 Function `get_speech_answer_prompt_template`

```python
def get_speech_answer_prompt_template(config: dict[str, Any]) -> str | None
```

Return stripped `prompts.speech_answer` template, or `None` if missing.

<details>
<summary>Code:</summary>

```python
def get_speech_answer_prompt_template(config: dict[str, Any]) -> str | None:
    return get_prompt_template(config, "speech_answer")
```

</details>
