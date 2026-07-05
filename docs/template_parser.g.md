---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `template_parser.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TemplateEntry`](#️-class-templateentry)
- [🏛️ Class `TemplateField`](#️-class-templatefield)
  - [⚙️ Method `__init__`](#️-method-__init__)
- [🏛️ Class `TemplateParser`](#️-class-templateparser)
  - [⚙️ Method `build_block_regex`](#️-method-build_block_regex)
  - [⚙️ Method `fill_template`](#️-method-fill_template)
  - [⚙️ Method `parse_block`](#️-method-parse_block)
  - [⚙️ Method `parse_template`](#️-method-parse_template)
  - [⚙️ Method `split_entries`](#️-method-split_entries)
  - [⚙️ Method `_capture_pattern_for_type`](#️-method-_capture_pattern_for_type)
  - [⚙️ Method `_format_multiline_value`](#️-method-_format_multiline_value)
  - [⚙️ Method `_parse_multiline_value`](#️-method-_parse_multiline_value)
  - [⚙️ Method `_sanitize_group_name`](#️-method-_sanitize_group_name)

</details>

## 🏛️ Class `TemplateEntry`

```python
class TemplateEntry
```

A markdown block extracted from a target file for template edit flows.

<details>
<summary>Code:</summary>

```python
class TemplateEntry:

    display_title: str
    block_text: str
    start: int
    end: int
```

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
- coordinates: Latitude and longitude pair (e.g. `55.7558, 37.6173`)

<details>
<summary>Code:</summary>

```python
class TemplateParser:

    _PLACEHOLDER_PATTERN = re.compile(r"\{\{([^:{}]+):([^:{}]+)(?::([^{}]+))?\}\}")
    _IMAGE_PATHS_PATTERN = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")

    @staticmethod
    def build_block_regex(template_content: str, fields: list[TemplateField]) -> re.Pattern[str] | None:
        """Build a regex that matches a filled markdown block for the given template."""
        field_types = {field.name: field.field_type for field in fields}
        parts: list[str] = []
        last_end = 0
        name_to_group: dict[str, str] = {}
        matches = list(TemplateParser._PLACEHOLDER_PATTERN.finditer(template_content))

        for index, match in enumerate(matches):
            literal = template_content[last_end : match.start()]
            parts.append(re.escape(literal))

            name = match.group(1).strip()
            field_type = match.group(2).strip().lower()

            if name in name_to_group:
                parts.append(f"(?P={name_to_group[name]})")
            else:
                group_name = TemplateParser._sanitize_group_name(name)
                name_to_group[name] = group_name
                next_literal = ""
                if index + 1 < len(matches):
                    next_literal = template_content[match.end() : matches[index + 1].start()]
                elif match.end() < len(template_content):
                    next_literal = template_content[match.end() :]
                parts.append(
                    TemplateParser._capture_pattern_for_type(
                        field_type, group_name, next_literal, field_types.get(name)
                    )
                )

            last_end = match.end()

        final_literal = template_content[last_end:]
        if final_literal.strip():
            parts.append(re.escape(final_literal))
        if not name_to_group:
            return None
        return re.compile("^" + "".join(parts) + r"\s*$", re.DOTALL | re.MULTILINE)

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
    def parse_block(
        template_content: str,
        block_text: str,
        fields: list[TemplateField],
    ) -> dict[str, str] | None:
        """Parse a filled markdown block back into field values."""
        pattern = TemplateParser.build_block_regex(template_content, fields)
        if pattern is None:
            return None
        match = pattern.match(block_text.strip())
        if match is None:
            return None

        field_types = {field.name: field.field_type for field in fields}
        result: dict[str, str] = {}
        for field in fields:
            group_name = TemplateParser._sanitize_group_name(field.name)
            try:
                raw = match.group(group_name)
            except IndexError:
                raw = ""
            if raw is None:
                raw = ""
            field_type = field_types[field.name]
            if field_type == "images":
                paths = TemplateParser._IMAGE_PATHS_PATTERN.findall(raw)
                result[field.name] = ",".join(p.strip() for p in paths if p.strip())
            elif field_type == "image":
                result[field.name] = raw.strip()
            elif field_type == "multiline":
                result[field.name] = TemplateParser._parse_multiline_value(raw)
            elif field_type == "files":
                result[field.name] = ",".join(p.strip() for p in raw.split(",") if p.strip())
            else:
                result[field.name] = raw.strip()
        return result

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
    def split_entries(content: str, template_content: str) -> list[TemplateEntry]:
        """Split markdown content into template-shaped entry blocks."""
        first_line = template_content.split("\n", maxsplit=1)[0]
        if first_line.startswith("### "):
            level = 3
        elif first_line.startswith("## "):
            level = 2
        else:
            return []

        heading_re = re.compile(r"^(#{2,3})\s+", re.MULTILINE)
        matches = list(heading_re.finditer(content))
        entries: list[TemplateEntry] = []

        for index, match in enumerate(matches):
            heading_level = len(match.group(1))
            if heading_level != level:
                continue

            start = match.start()
            end = len(content)
            for next_match in matches[index + 1 :]:
                if len(next_match.group(1)) <= level:
                    end = next_match.start()
                    break

            block_text = content[start:end].rstrip()
            newline_pos = content.find("\n", start)
            heading_line = content[start:newline_pos] if newline_pos != -1 else content[start:]
            display_title = heading_line.lstrip("#").strip()
            entries.append(
                TemplateEntry(
                    display_title=display_title,
                    block_text=block_text,
                    start=start,
                    end=end,
                )
            )

        return entries

    @staticmethod
    def _capture_pattern_for_type(
        field_type: str,
        group_name: str,
        next_literal: str,
        declared_type: str | None,
    ) -> str:
        if field_type == "images":
            return f"(?P<{group_name}>(?:!\\[[^\\]]*\\]\\([^)]+\\)\\s*\\n?)*)"
        if field_type == "image":
            return f"(?P<{group_name}>[^)]+)"
        if field_type in {"float", "int"}:
            return f"(?P<{group_name}>[\\d.,]+)"
        if field_type == "date":
            return f"(?P<{group_name}>\\d{{4}}-\\d{{2}}-\\d{{2}})"
        if field_type == "bool":
            return f"(?P<{group_name}>(?:true|false))"
        if field_type == "multiline":
            if not next_literal.strip():
                return f"(?P<{group_name}>[\\s\\S]*)"
            return f"(?P<{group_name}>[\\s\\S]*?)(?={re.escape(next_literal)})"
        if field_type == "files":
            return f"(?P<{group_name}>[^\\n]+)"
        if field_type == "coordinates":
            return f"(?P<{group_name}>[+-]?\\d+(?:\\.\\d+)?,\\s*[+-]?\\d+(?:\\.\\d+)?)"
        if next_literal.strip().startswith("<") and declared_type == "line":
            return f"(?P<{group_name}>[^>\\n]+)"
        return f"(?P<{group_name}>[^\\n]+)"

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

    @staticmethod
    def _parse_multiline_value(raw: str) -> str:
        """Reverse list-aware multiline formatting back to plain text."""
        raw = raw.strip()
        if not raw:
            return ""
        parts = re.split(r"\n\n", raw)
        lines = [parts[0].strip()]
        for part in parts[1:]:
            for line in part.split("\n"):
                stripped = line.strip()
                if stripped.startswith("  "):
                    stripped = stripped[2:].strip()
                if stripped:
                    lines.append(stripped)
        return "\n".join(lines)

    @staticmethod
    def _sanitize_group_name(name: str) -> str:
        group_name = re.sub(r"[^\w]", "_", name)
        if not group_name or not group_name[0].isalpha():
            group_name = f"f_{group_name}"
        return group_name
```

</details>

### ⚙️ Method `build_block_regex`

```python
def build_block_regex(template_content: str, fields: list[TemplateField]) -> re.Pattern[str] | None
```

Build a regex that matches a filled markdown block for the given template.

<details>
<summary>Code:</summary>

```python
def build_block_regex(template_content: str, fields: list[TemplateField]) -> re.Pattern[str] | None:
        field_types = {field.name: field.field_type for field in fields}
        parts: list[str] = []
        last_end = 0
        name_to_group: dict[str, str] = {}
        matches = list(TemplateParser._PLACEHOLDER_PATTERN.finditer(template_content))

        for index, match in enumerate(matches):
            literal = template_content[last_end : match.start()]
            parts.append(re.escape(literal))

            name = match.group(1).strip()
            field_type = match.group(2).strip().lower()

            if name in name_to_group:
                parts.append(f"(?P={name_to_group[name]})")
            else:
                group_name = TemplateParser._sanitize_group_name(name)
                name_to_group[name] = group_name
                next_literal = ""
                if index + 1 < len(matches):
                    next_literal = template_content[match.end() : matches[index + 1].start()]
                elif match.end() < len(template_content):
                    next_literal = template_content[match.end() :]
                parts.append(
                    TemplateParser._capture_pattern_for_type(
                        field_type, group_name, next_literal, field_types.get(name)
                    )
                )

            last_end = match.end()

        final_literal = template_content[last_end:]
        if final_literal.strip():
            parts.append(re.escape(final_literal))
        if not name_to_group:
            return None
        return re.compile("^" + "".join(parts) + r"\s*$", re.DOTALL | re.MULTILINE)
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

### ⚙️ Method `parse_block`

```python
def parse_block(template_content: str, block_text: str, fields: list[TemplateField]) -> dict[str, str] | None
```

Parse a filled markdown block back into field values.

<details>
<summary>Code:</summary>

```python
def parse_block(
        template_content: str,
        block_text: str,
        fields: list[TemplateField],
    ) -> dict[str, str] | None:
        pattern = TemplateParser.build_block_regex(template_content, fields)
        if pattern is None:
            return None
        match = pattern.match(block_text.strip())
        if match is None:
            return None

        field_types = {field.name: field.field_type for field in fields}
        result: dict[str, str] = {}
        for field in fields:
            group_name = TemplateParser._sanitize_group_name(field.name)
            try:
                raw = match.group(group_name)
            except IndexError:
                raw = ""
            if raw is None:
                raw = ""
            field_type = field_types[field.name]
            if field_type == "images":
                paths = TemplateParser._IMAGE_PATHS_PATTERN.findall(raw)
                result[field.name] = ",".join(p.strip() for p in paths if p.strip())
            elif field_type == "image":
                result[field.name] = raw.strip()
            elif field_type == "multiline":
                result[field.name] = TemplateParser._parse_multiline_value(raw)
            elif field_type == "files":
                result[field.name] = ",".join(p.strip() for p in raw.split(",") if p.strip())
            else:
                result[field.name] = raw.strip()
        return result
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

### ⚙️ Method `split_entries`

```python
def split_entries(content: str, template_content: str) -> list[TemplateEntry]
```

Split markdown content into template-shaped entry blocks.

<details>
<summary>Code:</summary>

```python
def split_entries(content: str, template_content: str) -> list[TemplateEntry]:
        first_line = template_content.split("\n", maxsplit=1)[0]
        if first_line.startswith("### "):
            level = 3
        elif first_line.startswith("## "):
            level = 2
        else:
            return []

        heading_re = re.compile(r"^(#{2,3})\s+", re.MULTILINE)
        matches = list(heading_re.finditer(content))
        entries: list[TemplateEntry] = []

        for index, match in enumerate(matches):
            heading_level = len(match.group(1))
            if heading_level != level:
                continue

            start = match.start()
            end = len(content)
            for next_match in matches[index + 1 :]:
                if len(next_match.group(1)) <= level:
                    end = next_match.start()
                    break

            block_text = content[start:end].rstrip()
            newline_pos = content.find("\n", start)
            heading_line = content[start:newline_pos] if newline_pos != -1 else content[start:]
            display_title = heading_line.lstrip("#").strip()
            entries.append(
                TemplateEntry(
                    display_title=display_title,
                    block_text=block_text,
                    start=start,
                    end=end,
                )
            )

        return entries
```

</details>

### ⚙️ Method `_capture_pattern_for_type`

```python
def _capture_pattern_for_type(field_type: str, group_name: str, next_literal: str, declared_type: str | None) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _capture_pattern_for_type(
        field_type: str,
        group_name: str,
        next_literal: str,
        declared_type: str | None,
    ) -> str:
        if field_type == "images":
            return f"(?P<{group_name}>(?:!\\[[^\\]]*\\]\\([^)]+\\)\\s*\\n?)*)"
        if field_type == "image":
            return f"(?P<{group_name}>[^)]+)"
        if field_type in {"float", "int"}:
            return f"(?P<{group_name}>[\\d.,]+)"
        if field_type == "date":
            return f"(?P<{group_name}>\\d{{4}}-\\d{{2}}-\\d{{2}})"
        if field_type == "bool":
            return f"(?P<{group_name}>(?:true|false))"
        if field_type == "multiline":
            if not next_literal.strip():
                return f"(?P<{group_name}>[\\s\\S]*)"
            return f"(?P<{group_name}>[\\s\\S]*?)(?={re.escape(next_literal)})"
        if field_type == "files":
            return f"(?P<{group_name}>[^\\n]+)"
        if field_type == "coordinates":
            return f"(?P<{group_name}>[+-]?\\d+(?:\\.\\d+)?,\\s*[+-]?\\d+(?:\\.\\d+)?)"
        if next_literal.strip().startswith("<") and declared_type == "line":
            return f"(?P<{group_name}>[^>\\n]+)"
        return f"(?P<{group_name}>[^\\n]+)"
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

### ⚙️ Method `_parse_multiline_value`

```python
def _parse_multiline_value(raw: str) -> str
```

Reverse list-aware multiline formatting back to plain text.

<details>
<summary>Code:</summary>

```python
def _parse_multiline_value(raw: str) -> str:
        raw = raw.strip()
        if not raw:
            return ""
        parts = re.split(r"\n\n", raw)
        lines = [parts[0].strip()]
        for part in parts[1:]:
            for line in part.split("\n"):
                stripped = line.strip()
                if stripped.startswith("  "):
                    stripped = stripped[2:].strip()
                if stripped:
                    lines.append(stripped)
        return "\n".join(lines)
```

</details>

### ⚙️ Method `_sanitize_group_name`

```python
def _sanitize_group_name(name: str) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _sanitize_group_name(name: str) -> str:
        group_name = re.sub(r"[^\w]", "_", name)
        if not group_name or not group_name[0].isalpha():
            group_name = f"f_{group_name}"
        return group_name
```

</details>
