---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `template_parser.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TemplateField`](#️-class-templatefield)
  - [⚙️ Method `__init__`](#️-method-__init__)
- [🏛️ Class `TemplateParser`](#️-class-templateparser)
  - [⚙️ Method `fill_template`](#️-method-fill_template)
  - [⚙️ Method `parse_template`](#️-method-parse_template)
  - [⚙️ Method `_format_multiline_value`](#️-method-_format_multiline_value)

</details>

## 🏛️ Class `TemplateField`

```python
class TemplateField
```

Represents a single field in a template.

Attributes:

- `name` (`str`): The field name (e.g., "Title", "Score").
- `field_type` (`str`): The field type (e.g., "line", "int", "float", "date", "bool", "multiline", "combobox").
- `placeholder` (`str`): The original placeholder text from the template.
- `default_value` (`str | None`): Optional default value for the field.
- `options` (`list[str] | None`): Optional list of options for combobox field type. Defaults to `None`.

<details>
<summary>Code:</summary>

```python
class TemplateField:

    def __init__(
        self,
        name: str,
        field_type: str,
        placeholder: str,
        default_value: str | None = None,
        options: list[str] | None = None,
    ) -> None:
        """Initialize a template field."""
        self.name = name
        self.field_type = field_type
        self.placeholder = placeholder
        self.default_value = default_value
        self.options = options or []
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, name: str, field_type: str, placeholder: str, default_value: str | None = None, options: list[str] | None = None) -> None
```

Initialize a template field.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        name: str,
        field_type: str,
        placeholder: str,
        default_value: str | None = None,
        options: list[str] | None = None,
    ) -> None:
        self.name = name
        self.field_type = field_type
        self.placeholder = placeholder
        self.default_value = default_value
        self.options = options or []
```

</details>

## 🏛️ Class `TemplateParser`

```python
class TemplateParser
```

Parser for extracting field definitions from markdown templates.

This class parses templates with placeholders in the format:
{{FieldName:FieldType}}

Supported field types:

- line: Single-line text input
- int: Integer number
- float: Floating-point number
- date: Date picker
- bool: Checkbox (returns "true" or "false")
- multiline: Multi-line text area
- image: Single image selection with drag and drop support
- images: Multiple image selection with drag and drop support
- file: Single file selection with drag and drop support
- files: Multiple file selection with drag and drop support

<details>
<summary>Code:</summary>

```python
class TemplateParser:

    @staticmethod
    def fill_template(template_content: str, field_values: dict[str, str]) -> str:
        """Fill a template with provided field values."""
        placeholder_pattern = re.compile(r"\{\{([^:{}]+):([^:{}]+)(?::([^{}]+))?\}\}")
        result_parts: list[str] = []
        last_end = 0

        str_values: dict[str, str] = {str(k): ("" if v is None else str(v)) for k, v in field_values.items()}

        for match in placeholder_pattern.finditer(template_content):
            name = match.group(1).strip()
            field_type = match.group(2).strip().lower()
            value = str_values.get(name, "")

            if field_type == "multiline" and "\n" in value:
                line_start = template_content.rfind("\n", 0, match.start())
                line_start = line_start + 1 if line_start >= 0 else 0
                line_prefix = template_content[line_start : match.start()]
                value = TemplateParser._format_multiline_value(value, line_prefix)

            if field_type == "images" and value.strip():
                paths = [p.strip() for p in value.split(",") if p.strip()]
                alt = str_values.get("Title", "").strip()
                value = "\n".join(f"![{alt}]({p})" for p in paths)

            result_parts.append(template_content[last_end : match.start()])
            result_parts.append(value)
            last_end = match.end()

        result_parts.append(template_content[last_end:])
        return "".join(result_parts)

    @staticmethod
    def parse_template(template_content: str) -> tuple[list[TemplateField], str]:
        """Parse a template to extract field definitions."""
        pattern = r"\{\{([^:{}]+):([^:{}]+)(?::([^{}]+))?\}\}"
        matches = re.findall(pattern, template_content)

        fields = []
        seen_names = set()

        for match in matches:
            field_type_index = 1
            default_value_index = 2

            name = match[0].strip()
            field_type = match[field_type_index].strip().lower()
            default_value = (
                match[default_value_index].strip()
                if len(match) > default_value_index and match[default_value_index]
                else None
            )

            if name in seen_names:
                continue

            seen_names.add(name)
            placeholder = f"{{{{{name}:{field_type}}}}}"
            fields.append(TemplateField(name, field_type, placeholder, default_value))

        return fields, template_content

    @staticmethod
    def _format_multiline_value(value: str, line_prefix: str) -> str:
        """Format multiline value for markdown list continuation."""
        lines = [line.rstrip() for line in value.strip().split("\n")]
        while lines and not lines[-1]:
            lines.pop()
        if not lines:
            return ""
        if len(lines) == 1:
            return lines[0]
        first_line = lines[0]
        rest = [line for line in lines[1:] if line]
        if not rest:
            return first_line
        is_list_line = bool(re.match(r"^\s*-\s+", line_prefix))
        rest_formatted = "\n\n".join("  " + line for line in rest) if is_list_line else "\n\n".join(rest)
        result = first_line + "\n\n" + rest_formatted
        return result.rstrip("\n")
```

</details>

### ⚙️ Method `fill_template`

```python
def fill_template(template_content: str, field_values: dict[str, str]) -> str
```

Fill a template with provided field values.

<details>
<summary>Code:</summary>

```python
def fill_template(template_content: str, field_values: dict[str, str]) -> str:
        placeholder_pattern = re.compile(r"\{\{([^:{}]+):([^:{}]+)(?::([^{}]+))?\}\}")
        result_parts: list[str] = []
        last_end = 0

        str_values: dict[str, str] = {str(k): ("" if v is None else str(v)) for k, v in field_values.items()}

        for match in placeholder_pattern.finditer(template_content):
            name = match.group(1).strip()
            field_type = match.group(2).strip().lower()
            value = str_values.get(name, "")

            if field_type == "multiline" and "\n" in value:
                line_start = template_content.rfind("\n", 0, match.start())
                line_start = line_start + 1 if line_start >= 0 else 0
                line_prefix = template_content[line_start : match.start()]
                value = TemplateParser._format_multiline_value(value, line_prefix)

            if field_type == "images" and value.strip():
                paths = [p.strip() for p in value.split(",") if p.strip()]
                alt = str_values.get("Title", "").strip()
                value = "\n".join(f"![{alt}]({p})" for p in paths)

            result_parts.append(template_content[last_end : match.start()])
            result_parts.append(value)
            last_end = match.end()

        result_parts.append(template_content[last_end:])
        return "".join(result_parts)
```

</details>

### ⚙️ Method `parse_template`

```python
def parse_template(template_content: str) -> tuple[list[TemplateField], str]
```

Parse a template to extract field definitions.

<details>
<summary>Code:</summary>

```python
def parse_template(template_content: str) -> tuple[list[TemplateField], str]:
        pattern = r"\{\{([^:{}]+):([^:{}]+)(?::([^{}]+))?\}\}"
        matches = re.findall(pattern, template_content)

        fields = []
        seen_names = set()

        for match in matches:
            field_type_index = 1
            default_value_index = 2

            name = match[0].strip()
            field_type = match[field_type_index].strip().lower()
            default_value = (
                match[default_value_index].strip()
                if len(match) > default_value_index and match[default_value_index]
                else None
            )

            if name in seen_names:
                continue

            seen_names.add(name)
            placeholder = f"{{{{{name}:{field_type}}}}}"
            fields.append(TemplateField(name, field_type, placeholder, default_value))

        return fields, template_content
```

</details>

### ⚙️ Method `_format_multiline_value`

```python
def _format_multiline_value(value: str, line_prefix: str) -> str
```

Format multiline value for markdown list continuation.

<details>
<summary>Code:</summary>

```python
def _format_multiline_value(value: str, line_prefix: str) -> str:
        lines = [line.rstrip() for line in value.strip().split("\n")]
        while lines and not lines[-1]:
            lines.pop()
        if not lines:
            return ""
        if len(lines) == 1:
            return lines[0]
        first_line = lines[0]
        rest = [line for line in lines[1:] if line]
        if not rest:
            return first_line
        is_list_line = bool(re.match(r"^\s*-\s+", line_prefix))
        rest_formatted = "\n\n".join("  " + line for line in rest) if is_list_line else "\n\n".join(rest)
        result = first_line + "\n\n" + rest_formatted
        return result.rstrip("\n")
```

</details>
