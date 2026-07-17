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
  - [⚙️ Method `_build_line_regex_pattern`](#️-method-_build_line_regex_pattern)
  - [⚙️ Method `_capture_pattern_for_type`](#️-method-_capture_pattern_for_type)
  - [⚙️ Method `_fill_template_line`](#️-method-_fill_template_line)
  - [⚙️ Method `_format_multiline_value`](#️-method-_format_multiline_value)
  - [⚙️ Method `_is_field_value_filled`](#️-method-_is_field_value_filled)
  - [⚙️ Method `_line_has_any_filled_placeholder`](#️-method-_line_has_any_filled_placeholder)
  - [⚙️ Method `_line_omits_when_all_fields_empty`](#️-method-_line_omits_when_all_fields_empty)
  - [⚙️ Method `_next_template_literal`](#️-method-_next_template_literal)
  - [⚙️ Method `_parse_date_field_link`](#️-method-_parse_date_field_link)
  - [⚙️ Method `_parse_field_link`](#️-method-_parse_field_link)
  - [⚙️ Method `_parse_multiline_value`](#️-method-_parse_multiline_value)
  - [⚙️ Method `_parse_placeholder_match`](#️-method-_parse_placeholder_match)
  - [⚙️ Method `_sanitize_group_name`](#️-method-_sanitize_group_name)
  - [⚙️ Method `_template_lines`](#️-method-_template_lines)

</details>

## 🏛️ Class `TemplateEntry`

```python
class TemplateEntry
```

A Markdown block extracted from a target file for template edit flows.

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
- `field_link` (`str | None`): Optional `@` link from the placeholder (field name for
  image filename base, or `subfolders` for combobox options).
- `image_optimize` (`bool`): When `True`, images are optimized after save (from `#size`
  suffix on `image`/`images` fields).
- `image_max_size` (`int | None`): Max width/height in pixels when `image_optimize` is enabled.
- `date_from_images` (`str | None`): For `date` fields: name of `image`/`images` field to
  read dates from filenames.
- `date_from_images_overwrite` (`bool`): When `True`, update the date on every new image drop;
  otherwise fill only if empty.

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
        field_link: str | None = None,
        *,
        image_optimize: bool = False,
        image_max_size: int | None = None,
        date_from_images: str | None = None,
        date_from_images_overwrite: bool = False,
    ) -> None:
        """Initialize a template field."""
        self.name = name
        self.field_type = field_type
        self.placeholder = placeholder
        self.default_value = default_value
        self.options = options or []
        self.field_link = field_link
        self.image_optimize = image_optimize
        self.image_max_size = image_max_size
        self.date_from_images = date_from_images
        self.date_from_images_overwrite = date_from_images_overwrite
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, name: str, field_type: str, placeholder: str, default_value: str | None = None, options: list[str] | None = None, field_link: str | None = None) -> None
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
        field_link: str | None = None,
        *,
        image_optimize: bool = False,
        image_max_size: int | None = None,
        date_from_images: str | None = None,
        date_from_images_overwrite: bool = False,
    ) -> None:
        self.name = name
        self.field_type = field_type
        self.placeholder = placeholder
        self.default_value = default_value
        self.options = options or []
        self.field_link = field_link
        self.image_optimize = image_optimize
        self.image_max_size = image_max_size
        self.date_from_images = date_from_images
        self.date_from_images_overwrite = date_from_images_overwrite
```

</details>

## 🏛️ Class `TemplateParser`

```python
class TemplateParser
```

Parser for extracting field definitions from Markdown templates.

This class parses templates with placeholders in the format:
{{FieldName:FieldType}}
{{FieldName:FieldType@Link#1024}}
{{FieldName:FieldType@Link#1024:DefaultValue}}

`@Link` for `image`/`images` is another field name used for filename base.
`#1024` after `@Link` enables image optimization with max side 1024 px.
`@subfolders` on `line` loads combobox options from existing subfolders of `path_target`.
`@note_name` marks the field used as note folder/file stem in `city_note` layout.
`@Images` on `date` fills the date from dropped image filenames (fill-if-empty).
`@Images!` on `date` always updates the date when new images are added.

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

    FIELD_LINK_SUBFOLDERS = "subfolders"
    FIELD_LINK_NOTE_NAME = "note_name"

    _PLACEHOLDER_PATTERN = re.compile(r"\{\{([^:{}]+):([^:{}@]+)(?:@([^:{}]+))?(?::([^{}]+))?\}\}")
    _IMAGE_PATHS_PATTERN = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")

    @staticmethod
    def build_block_regex(template_content: str, fields: list[TemplateField]) -> re.Pattern[str] | None:
        """Build a regex that matches a filled Markdown block for the given template."""
        field_types = {field.name: field.field_type for field in fields}
        line_parts: list[str] = []
        name_to_group: dict[str, str] = {}
        template_lines = TemplateParser._template_lines(template_content)

        for line_index, line in enumerate(template_lines):
            matches = list(TemplateParser._PLACEHOLDER_PATTERN.finditer(line))
            if not matches:
                segment = re.escape(line)
            else:
                line_pattern = TemplateParser._build_line_regex_pattern(
                    line,
                    matches,
                    field_types,
                    name_to_group,
                    template_lines,
                    line_index,
                )
                segment = (
                    f"(?:{line_pattern})?"
                    if TemplateParser._line_omits_when_all_fields_empty(matches)
                    else line_pattern
                )

            if line_index == 0:
                line_parts.append(segment)
            elif TemplateParser._line_omits_when_all_fields_empty(matches) if matches else False:
                line_parts.append(f"(?:\n{segment})?")
            else:
                line_parts.append(f"\n{segment}")

        if not name_to_group:
            return None
        return re.compile("^" + "".join(line_parts) + r"\s*$", re.DOTALL | re.MULTILINE)

    @staticmethod
    def fill_template(template_content: str, field_values: dict[str, str]) -> str:
        """Fill a template with provided field values."""
        str_values: dict[str, str] = {str(k): ("" if v is None else str(v)) for k, v in field_values.items()}
        result_lines: list[str] = []

        for line in TemplateParser._template_lines(template_content):
            matches = list(TemplateParser._PLACEHOLDER_PATTERN.finditer(line))
            if matches and not TemplateParser._line_has_any_filled_placeholder(matches, str_values):
                continue
            result_lines.append(TemplateParser._fill_template_line(line, str_values))

        return "\n".join(result_lines)

    @staticmethod
    def parse_block(
        template_content: str,
        block_text: str,
        fields: list[TemplateField],
    ) -> dict[str, str] | None:
        """Parse a filled Markdown block back into field values."""
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
        fields = []
        seen_names = set()

        for match in TemplateParser._PLACEHOLDER_PATTERN.finditer(template_content):
            parsed = TemplateParser._parse_placeholder_match(match)
            name = parsed[0]
            field_type = parsed[1]
            field_link = parsed[2]
            default_value = parsed[3]
            image_optimize = parsed[4]
            image_max_size = parsed[5]
            date_from_images = parsed[6]
            date_from_images_overwrite = parsed[7]

            if name in seen_names:
                continue

            seen_names.add(name)
            fields.append(
                TemplateField(
                    name,
                    field_type,
                    match.group(0),
                    default_value,
                    field_link=field_link,
                    image_optimize=image_optimize,
                    image_max_size=image_max_size,
                    date_from_images=date_from_images,
                    date_from_images_overwrite=date_from_images_overwrite,
                )
            )

        return fields, template_content

    @staticmethod
    def split_entries(content: str, template_content: str) -> list[TemplateEntry]:
        """Split Markdown content into template-shaped entry blocks."""
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
    def _build_line_regex_pattern(
        line: str,
        matches: list[re.Match[str]],
        field_types: dict[str, str],
        name_to_group: dict[str, str],
        template_lines: list[str],
        line_index: int,
    ) -> str:
        parts: list[str] = []
        last_end = 0
        for match in matches:
            parts.append(re.escape(line[last_end : match.start()]))
            parsed = TemplateParser._parse_placeholder_match(match)
            name = parsed[0]
            field_type = parsed[1]
            if name in name_to_group:
                parts.append(f"(?P={name_to_group[name]})")
            else:
                group_name = TemplateParser._sanitize_group_name(name)
                name_to_group[name] = group_name
                next_literal = TemplateParser._next_template_literal(template_lines, line_index, line[match.end() :])
                parts.append(
                    TemplateParser._capture_pattern_for_type(
                        field_type, group_name, next_literal, field_types.get(name)
                    )
                )
            last_end = match.end()
        parts.append(re.escape(line[last_end:]))
        return "".join(parts)

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
    def _fill_template_line(line: str, str_values: dict[str, str]) -> str:
        result_parts: list[str] = []
        last_end = 0
        for match in TemplateParser._PLACEHOLDER_PATTERN.finditer(line):
            _parsed = TemplateParser._parse_placeholder_match(match)
            name = _parsed[0]
            field_type = _parsed[1]
            value = str_values.get(name, "")

            if field_type == "multiline" and "\n" in value:
                line_prefix = line[: match.start()]
                value = TemplateParser._format_multiline_value(value, line_prefix)

            if field_type == "images" and value.strip():
                paths = [p.strip() for p in value.split(",") if p.strip()]
                alt = str_values.get("Title", "").strip()
                value = "\n".join(f"![{alt}]({p})" for p in paths)

            result_parts.append(line[last_end : match.start()])
            result_parts.append(value)
            last_end = match.end()
        result_parts.append(line[last_end:])
        return "".join(result_parts)

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
    def _is_field_value_filled(field_type: str, value: str) -> bool:
        if field_type == "bool":
            return True
        return bool(value.strip())

    @staticmethod
    def _line_has_any_filled_placeholder(matches: list[re.Match[str]], str_values: dict[str, str]) -> bool:
        for match in matches:
            _parsed = TemplateParser._parse_placeholder_match(match)
            name = _parsed[0]
            field_type = _parsed[1]
            if TemplateParser._is_field_value_filled(field_type, str_values.get(name, "")):
                return True
        return False

    @staticmethod
    def _line_omits_when_all_fields_empty(matches: list[re.Match[str]]) -> bool:
        return bool(matches)

    @staticmethod
    def _next_template_literal(template_lines: list[str], line_index: int, remainder: str) -> str:
        if remainder.strip():
            return remainder
        following = template_lines[line_index + 1 :]
        while following and not following[0].strip():
            following = following[1:]
        if not following:
            return ""
        return "\n" + following[0]

    @staticmethod
    def _parse_date_field_link(raw_link: str | None) -> tuple[str | None, bool]:
        """Parse ``Images`` or ``Images!`` link for date fields."""
        if not raw_link:
            return None, False
        overwrite = raw_link.endswith("!")
        images_field = raw_link.rstrip("!").strip() or None
        return images_field, overwrite

    @staticmethod
    def _parse_field_link(raw_link: str | None) -> tuple[str | None, bool, int | None]:
        """Split ``Title#1024`` into link name and optional optimize max side."""
        if not raw_link:
            return None, False, None
        if "#" not in raw_link:
            return raw_link, False, None
        link_part, _, size_part = raw_link.partition("#")
        field_link = link_part.strip() or None
        size_text = size_part.strip()
        if size_text.isdigit():
            return field_link, True, int(size_text)
        return raw_link, False, None

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
    def _parse_placeholder_match(
        match: re.Match[str],
    ) -> tuple[str, str, str | None, str | None, bool, int | None, str | None, bool]:
        """Return field metadata from a placeholder match."""
        name = match.group(1).strip()
        field_type = match.group(2).strip().lower()
        raw_link = match.group(3).strip() if match.group(3) else None
        default_value = match.group(4).strip() if match.group(4) else None
        if field_type.split("#", maxsplit=1)[0] in ("image", "images") and "#" in field_type:
            base_type, _, size_suffix = field_type.partition("#")
            field_type = base_type
            if raw_link is None and size_suffix.strip().isdigit():
                raw_link = f"#{size_suffix.strip()}"
        date_from_images: str | None = None
        date_from_images_overwrite = False
        if field_type == "date":
            date_from_images, date_from_images_overwrite = TemplateParser._parse_date_field_link(raw_link)
            field_link = None
            image_optimize = False
            image_max_size = None
        elif field_type in ("image", "images"):
            field_link, image_optimize, image_max_size = TemplateParser._parse_field_link(raw_link)
        else:
            field_link = raw_link
            image_optimize = False
            image_max_size = None
        return (
            name,
            field_type,
            field_link,
            default_value,
            image_optimize,
            image_max_size,
            date_from_images,
            date_from_images_overwrite,
        )

    @staticmethod
    def _sanitize_group_name(name: str) -> str:
        group_name = re.sub(r"[^\w]", "_", name)
        if not group_name or not group_name[0].isalpha():
            group_name = f"f_{group_name}"
        return group_name

    @staticmethod
    def _template_lines(template_content: str) -> list[str]:
        lines = template_content.split("\n")
        while lines and not lines[-1].strip():
            lines.pop()
        return lines
```

</details>

### ⚙️ Method `build_block_regex`

```python
def build_block_regex(template_content: str, fields: list[TemplateField]) -> re.Pattern[str] | None
```

Build a regex that matches a filled Markdown block for the given template.

<details>
<summary>Code:</summary>

```python
def build_block_regex(template_content: str, fields: list[TemplateField]) -> re.Pattern[str] | None:
        field_types = {field.name: field.field_type for field in fields}
        line_parts: list[str] = []
        name_to_group: dict[str, str] = {}
        template_lines = TemplateParser._template_lines(template_content)

        for line_index, line in enumerate(template_lines):
            matches = list(TemplateParser._PLACEHOLDER_PATTERN.finditer(line))
            if not matches:
                segment = re.escape(line)
            else:
                line_pattern = TemplateParser._build_line_regex_pattern(
                    line,
                    matches,
                    field_types,
                    name_to_group,
                    template_lines,
                    line_index,
                )
                segment = (
                    f"(?:{line_pattern})?"
                    if TemplateParser._line_omits_when_all_fields_empty(matches)
                    else line_pattern
                )

            if line_index == 0:
                line_parts.append(segment)
            elif TemplateParser._line_omits_when_all_fields_empty(matches) if matches else False:
                line_parts.append(f"(?:\n{segment})?")
            else:
                line_parts.append(f"\n{segment}")

        if not name_to_group:
            return None
        return re.compile("^" + "".join(line_parts) + r"\s*$", re.DOTALL | re.MULTILINE)
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
        str_values: dict[str, str] = {str(k): ("" if v is None else str(v)) for k, v in field_values.items()}
        result_lines: list[str] = []

        for line in TemplateParser._template_lines(template_content):
            matches = list(TemplateParser._PLACEHOLDER_PATTERN.finditer(line))
            if matches and not TemplateParser._line_has_any_filled_placeholder(matches, str_values):
                continue
            result_lines.append(TemplateParser._fill_template_line(line, str_values))

        return "\n".join(result_lines)
```

</details>

### ⚙️ Method `parse_block`

```python
def parse_block(template_content: str, block_text: str, fields: list[TemplateField]) -> dict[str, str] | None
```

Parse a filled Markdown block back into field values.

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
        fields = []
        seen_names = set()

        for match in TemplateParser._PLACEHOLDER_PATTERN.finditer(template_content):
            parsed = TemplateParser._parse_placeholder_match(match)
            name = parsed[0]
            field_type = parsed[1]
            field_link = parsed[2]
            default_value = parsed[3]
            image_optimize = parsed[4]
            image_max_size = parsed[5]
            date_from_images = parsed[6]
            date_from_images_overwrite = parsed[7]

            if name in seen_names:
                continue

            seen_names.add(name)
            fields.append(
                TemplateField(
                    name,
                    field_type,
                    match.group(0),
                    default_value,
                    field_link=field_link,
                    image_optimize=image_optimize,
                    image_max_size=image_max_size,
                    date_from_images=date_from_images,
                    date_from_images_overwrite=date_from_images_overwrite,
                )
            )

        return fields, template_content
```

</details>

### ⚙️ Method `split_entries`

```python
def split_entries(content: str, template_content: str) -> list[TemplateEntry]
```

Split Markdown content into template-shaped entry blocks.

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

### ⚙️ Method `_build_line_regex_pattern`

```python
def _build_line_regex_pattern(line: str, matches: list[re.Match[str]], field_types: dict[str, str], name_to_group: dict[str, str], template_lines: list[str], line_index: int) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _build_line_regex_pattern(
        line: str,
        matches: list[re.Match[str]],
        field_types: dict[str, str],
        name_to_group: dict[str, str],
        template_lines: list[str],
        line_index: int,
    ) -> str:
        parts: list[str] = []
        last_end = 0
        for match in matches:
            parts.append(re.escape(line[last_end : match.start()]))
            parsed = TemplateParser._parse_placeholder_match(match)
            name = parsed[0]
            field_type = parsed[1]
            if name in name_to_group:
                parts.append(f"(?P={name_to_group[name]})")
            else:
                group_name = TemplateParser._sanitize_group_name(name)
                name_to_group[name] = group_name
                next_literal = TemplateParser._next_template_literal(template_lines, line_index, line[match.end() :])
                parts.append(
                    TemplateParser._capture_pattern_for_type(
                        field_type, group_name, next_literal, field_types.get(name)
                    )
                )
            last_end = match.end()
        parts.append(re.escape(line[last_end:]))
        return "".join(parts)
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

### ⚙️ Method `_fill_template_line`

```python
def _fill_template_line(line: str, str_values: dict[str, str]) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _fill_template_line(line: str, str_values: dict[str, str]) -> str:
        result_parts: list[str] = []
        last_end = 0
        for match in TemplateParser._PLACEHOLDER_PATTERN.finditer(line):
            _parsed = TemplateParser._parse_placeholder_match(match)
            name = _parsed[0]
            field_type = _parsed[1]
            value = str_values.get(name, "")

            if field_type == "multiline" and "\n" in value:
                line_prefix = line[: match.start()]
                value = TemplateParser._format_multiline_value(value, line_prefix)

            if field_type == "images" and value.strip():
                paths = [p.strip() for p in value.split(",") if p.strip()]
                alt = str_values.get("Title", "").strip()
                value = "\n".join(f"![{alt}]({p})" for p in paths)

            result_parts.append(line[last_end : match.start()])
            result_parts.append(value)
            last_end = match.end()
        result_parts.append(line[last_end:])
        return "".join(result_parts)
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

### ⚙️ Method `_is_field_value_filled`

```python
def _is_field_value_filled(field_type: str, value: str) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _is_field_value_filled(field_type: str, value: str) -> bool:
        if field_type == "bool":
            return True
        return bool(value.strip())
```

</details>

### ⚙️ Method `_line_has_any_filled_placeholder`

```python
def _line_has_any_filled_placeholder(matches: list[re.Match[str]], str_values: dict[str, str]) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _line_has_any_filled_placeholder(matches: list[re.Match[str]], str_values: dict[str, str]) -> bool:
        for match in matches:
            _parsed = TemplateParser._parse_placeholder_match(match)
            name = _parsed[0]
            field_type = _parsed[1]
            if TemplateParser._is_field_value_filled(field_type, str_values.get(name, "")):
                return True
        return False
```

</details>

### ⚙️ Method `_line_omits_when_all_fields_empty`

```python
def _line_omits_when_all_fields_empty(matches: list[re.Match[str]]) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _line_omits_when_all_fields_empty(matches: list[re.Match[str]]) -> bool:
        return bool(matches)
```

</details>

### ⚙️ Method `_next_template_literal`

```python
def _next_template_literal(template_lines: list[str], line_index: int, remainder: str) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _next_template_literal(template_lines: list[str], line_index: int, remainder: str) -> str:
        if remainder.strip():
            return remainder
        following = template_lines[line_index + 1 :]
        while following and not following[0].strip():
            following = following[1:]
        if not following:
            return ""
        return "\n" + following[0]
```

</details>

### ⚙️ Method `_parse_date_field_link`

```python
def _parse_date_field_link(raw_link: str | None) -> tuple[str | None, bool]
```

Parse `Images` or `Images!` link for date fields.

<details>
<summary>Code:</summary>

```python
def _parse_date_field_link(raw_link: str | None) -> tuple[str | None, bool]:
        if not raw_link:
            return None, False
        overwrite = raw_link.endswith("!")
        images_field = raw_link.rstrip("!").strip() or None
        return images_field, overwrite
```

</details>

### ⚙️ Method `_parse_field_link`

```python
def _parse_field_link(raw_link: str | None) -> tuple[str | None, bool, int | None]
```

Split `Title#1024` into link name and optional optimize max side.

<details>
<summary>Code:</summary>

```python
def _parse_field_link(raw_link: str | None) -> tuple[str | None, bool, int | None]:
        if not raw_link:
            return None, False, None
        if "#" not in raw_link:
            return raw_link, False, None
        link_part, _, size_part = raw_link.partition("#")
        field_link = link_part.strip() or None
        size_text = size_part.strip()
        if size_text.isdigit():
            return field_link, True, int(size_text)
        return raw_link, False, None
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

### ⚙️ Method `_parse_placeholder_match`

```python
def _parse_placeholder_match(match: re.Match[str]) -> tuple[str, str, str | None, str | None, bool, int | None, str | None, bool]
```

Return field metadata from a placeholder match.

<details>
<summary>Code:</summary>

```python
def _parse_placeholder_match(
        match: re.Match[str],
    ) -> tuple[str, str, str | None, str | None, bool, int | None, str | None, bool]:
        name = match.group(1).strip()
        field_type = match.group(2).strip().lower()
        raw_link = match.group(3).strip() if match.group(3) else None
        default_value = match.group(4).strip() if match.group(4) else None
        if field_type.split("#", maxsplit=1)[0] in ("image", "images") and "#" in field_type:
            base_type, _, size_suffix = field_type.partition("#")
            field_type = base_type
            if raw_link is None and size_suffix.strip().isdigit():
                raw_link = f"#{size_suffix.strip()}"
        date_from_images: str | None = None
        date_from_images_overwrite = False
        if field_type == "date":
            date_from_images, date_from_images_overwrite = TemplateParser._parse_date_field_link(raw_link)
            field_link = None
            image_optimize = False
            image_max_size = None
        elif field_type in ("image", "images"):
            field_link, image_optimize, image_max_size = TemplateParser._parse_field_link(raw_link)
        else:
            field_link = raw_link
            image_optimize = False
            image_max_size = None
        return (
            name,
            field_type,
            field_link,
            default_value,
            image_optimize,
            image_max_size,
            date_from_images,
            date_from_images_overwrite,
        )
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

### ⚙️ Method `_template_lines`

```python
def _template_lines(template_content: str) -> list[str]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _template_lines(template_content: str) -> list[str]:
        lines = template_content.split("\n")
        while lines and not lines[-1].strip():
            lines.pop()
        return lines
```

</details>
