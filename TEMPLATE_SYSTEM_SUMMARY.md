# Template System Implementation Summary

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [Overview](#overview)
- [Components Created](#components-created)
  - [1. Template Files (config/)](#1-template-files-config)
  - [2. Template System Module (src/harrix_swiss_knife/template_dialog.py)](#2-template-system-module-srcharrix_swiss_knifetemplate_dialogpy)
  - [3. Action Class (src/harrix_swiss_knife/actions/markdown.py)](#3-action-class-srcharrix_swiss_knifeactionsmarkdownpy)
  - [4. Configuration (config/config.json)](#4-configuration-configconfigjson)
  - [5. Menu Integration (src/harrix_swiss_knife/main.py)](#5-menu-integration-srcharrix_swiss_knifemainpy)
- [Features](#features)
  - [Supported Field Types](#supported-field-types)
  - [Template Format](#template-format)
  - [Workflow](#workflow)
- [Testing](#testing)
- [Benefits](#benefits)
- [Usage](#usage)
- [Files Modified](#files-modified)
- [Files Created](#files-created)

</details>

## Overview

Implemented a flexible template-based form system for adding structured markdown elements (movies, series, books, etc.) to markdown files.

## Components Created

### 1. Template Files (config/)

- `template-movie.md` - Template for movie entries
- `template-series.md` - Template for TV series entries
- `template-book.md` - Template for book entries

### 2. Template System Module (src/harrix_swiss_knife/template_dialog.py)

- `TemplateField` - Data class representing a template field
- `TemplateParser` - Parser for extracting fields and filling templates
- `TemplateDialog` - Dynamic form dialog that generates input widgets based on template fields

### 3. Action Class (src/harrix_swiss_knife/actions/markdown.py)

- `OnAddMarkdownFromTemplate` - Main action that orchestrates the template workflow

### 4. Configuration (config/config.json)

Added `markdown_templates` section with three template configurations:

- movie
- series
- book

Each template configuration includes:

- `template_file` - Path to the template markdown file
- `target_file` - Target markdown file to insert content into
- `insert_position` - Where to insert ("end" or "start")

### 5. Menu Integration (src/harrix_swiss_knife/main.py)

Added the new action to the "New Markdown" menu

## Features

### Supported Field Types

- `line` - Single-line text input (QLineEdit)
- `int` - Integer number with spinner (QSpinBox)
- `float` - Floating-point number with spinner (QDoubleSpinBox)
- `date` - Date picker with calendar popup (QDateEdit)
- `multiline` - Multi-line text area (QPlainTextEdit)

### Template Format

Fields are defined using the syntax: `{{FieldName:FieldType}}` or `{{FieldName:FieldType:DefaultValue}}`

**Examples without default values:**

```markdown
## {{Title:line}}: {{Score:float}}

- **Date watching:** {{Date watching:date}}
- **Comments:** {{Comments:multiline}}
```

**Examples with default values:**

```markdown
## {{Title:line}}: {{Score:float:10}}

- **Season:** {{Season:int:1}}
- **Date watching:** {{Date watching:date:2025-01-01}}
- **Comments:** {{Comments:multiline:No comments yet}}
```

**Supported default value formats:**

- `line` - Any text string
- `int` - Integer number (e.g., `1`, `5`, `100`)
- `float` - Decimal number (e.g., `10`, `7.5`, `9.2`)
- `date` - Date in format `yyyy-MM-dd` (e.g., `2025-01-15`)
- `multiline` - Any text string (can include spaces)

### Workflow

1. User selects a template from a list
2. System reads the template file and parses field definitions
3. Dynamic form dialog is generated with appropriate widgets
4. User fills in the form
5. Template is filled with user values
6. Result is either:
   - Inserted into the configured target file (at end or start)
   - Displayed as output if no target file is configured

## Testing

Created and successfully ran test script that verified:

- Template parsing correctly extracts field definitions
- Template filling correctly replaces placeholders
- All template files are valid and parseable
- Movie template: 7 fields
- Series template: 7 fields
- Book template: 9 fields

## Benefits

1. **Flexible** - Not tied to markdown, can be used for any templated text
2. **Extensible** - Easy to add new field types by extending the widget creation logic
3. **User-friendly** - Provides appropriate input widgets (date pickers, number spinners, etc.)
4. **Configurable** - Templates and insertion points are configured in config.json
5. **Reusable** - Same system can be used for movies, books, or any other structured content

## Usage

1. Select "New Markdown" → "Add markdown from template" from the menu
2. Choose a template (movie, series, or book)
3. Fill in the form fields
4. Click OK
5. Content is added to the configured file or displayed

## Files Modified

- `config/config.json` - Added markdown_templates configuration
- `src/harrix_swiss_knife/actions/markdown.py` - Added OnAddMarkdownFromTemplate class
- `src/harrix_swiss_knife/main.py` - Added action to menu
- `src/harrix_swiss_knife/template_dialog.py` - New file with template system

## Files Created

- `config/template-movie.md`
- `config/template-series.md`
- `config/template-book.md`
- `src/harrix_swiss_knife/template_dialog.py`
