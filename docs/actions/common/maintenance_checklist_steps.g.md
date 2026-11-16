---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `maintenance_checklist_steps.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `MaintenanceStep`](#%EF%B8%8F-class-maintenancestep)
  - [⚙️ Method `class_name (property)`](#%EF%B8%8F-method-class_name-property)
  - [⚙️ Method `title (property)`](#%EF%B8%8F-method-title-property)
- [🏛️ Class `MaintenanceStepSpec`](#%EF%B8%8F-class-maintenancestepspec)
- [🔧 Function `format_last_used`](#-function-format_last_used)
- [🔧 Function `last_used_for_class`](#-function-last_used_for_class)
- [🔧 Function `maintenance_groups`](#-function-maintenance_groups)
- [🔧 Function `maintenance_steps`](#-function-maintenance_steps)

</details>

## 🏛️ Class `MaintenanceStep`

```python
class MaintenanceStep
```

One resolved row in the maintenance checklist.

<details>
<summary>Code:</summary>

```python
class MaintenanceStep:

    action_cls: type[ActionBase]
    group: str
    lucide_icon: str
    note: str = ""
    include_in_run_all: bool = True
    title_override: str | None = None

    @property
    def class_name(self) -> str:
        """Action class name used in `action_usage.json`."""
        return self.action_cls.__name__

    @property
    def title(self) -> str:
        """Display title for the checklist row."""
        if self.title_override:
            return self.title_override
        raw = getattr(self.action_cls, "title", self.class_name)
        return str(raw).replace("`", "")
```

</details>

### ⚙️ Method `class_name (property)`

```python
def class_name(self) -> str
```

Action class name used in `action_usage.json`.

<details>
<summary>Code:</summary>

```python
def class_name(self) -> str:
        return self.action_cls.__name__
```

</details>

### ⚙️ Method `title (property)`

```python
def title(self) -> str
```

Display title for the checklist row.

<details>
<summary>Code:</summary>

```python
def title(self) -> str:
        if self.title_override:
            return self.title_override
        raw = getattr(self.action_cls, "title", self.class_name)
        return str(raw).replace("`", "")
```

</details>

## 🏛️ Class `MaintenanceStepSpec`

```python
class MaintenanceStepSpec
```

Declarative checklist row (action imported lazily).

<details>
<summary>Code:</summary>

```python
class MaintenanceStepSpec:

    module: str
    class_name: str
    group: str
    lucide_icon: str
    note: str = ""
    include_in_run_all: bool = True
    title_override: str | None = None
```

</details>

## 🔧 Function `format_last_used`

```python
def format_last_used(iso_stamp: str | None) -> str
```

Return a short relative or absolute label for a usage timestamp.

<details>
<summary>Code:</summary>

```python
def format_last_used(iso_stamp: str | None) -> str:
    if not iso_stamp or not str(iso_stamp).strip():
        return "Never"
    try:
        parsed = datetime.fromisoformat(str(iso_stamp).strip())
    except ValueError:
        return str(iso_stamp)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    now = datetime.now(UTC).astimezone()
    local = parsed.astimezone()
    delta = now - local
    seconds = int(delta.total_seconds())
    if seconds < 0:
        return local.strftime("%Y-%m-%d %H:%M")
    if seconds < 60:
        return "Just now"
    if seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} min ago"
    if seconds < 86400:
        hours = seconds // 3600
        return f"{hours} h ago"
    if seconds < 86400 * 7:
        days = seconds // 86400
        return f"{days} d ago"
    return local.strftime("%Y-%m-%d %H:%M")
```

</details>

## 🔧 Function `last_used_for_class`

```python
def last_used_for_class(class_name: str) -> str
```

Return the ISO `last_used` stamp for [`class_name`](#%EF%B8%8F-method-class_name-property), or empty string.

<details>
<summary>Code:</summary>

```python
def last_used_for_class(class_name: str) -> str:
    entry = load_action_usage().get(class_name)
    if entry is None:
        return ""
    return entry.get("last_used") or ""
```

</details>

## 🔧 Function `maintenance_groups`

```python
def maintenance_groups() -> list[tuple[str, list[MaintenanceStep]]]
```

Group resolved steps preserving order.

<details>
<summary>Code:</summary>

```python
def maintenance_groups() -> list[tuple[str, list[MaintenanceStep]]]:
    groups: list[tuple[str, list[MaintenanceStep]]] = []
    index: dict[str, list[MaintenanceStep]] = {}
    for step in maintenance_steps():
        bucket = index.get(step.group)
        if bucket is None:
            bucket = []
            index[step.group] = bucket
            groups.append((step.group, bucket))
        bucket.append(step)
    return groups
```

</details>

## 🔧 Function `maintenance_steps`

```python
def maintenance_steps() -> tuple[MaintenanceStep, ...]
```

Resolve and cache checklist steps.

<details>
<summary>Code:</summary>

```python
def maintenance_steps() -> tuple[MaintenanceStep, ...]:
    return tuple(_resolve_spec(spec) for spec in MAINTENANCE_STEP_SPECS)
```

</details>
