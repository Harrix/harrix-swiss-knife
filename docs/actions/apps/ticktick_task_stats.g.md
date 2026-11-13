---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ticktick_task_stats.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnShowTickTickTaskStats`](#%EF%B8%8F-class-onshowtickticktaskstats)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnShowTickTickTaskStats`

```python
class OnShowTickTickTaskStats(ActionBase)
```

Open a GitHub-like calendar of completed TickTick tasks from the local DB.

<details>
<summary>Code:</summary>

```python
class OnShowTickTickTaskStats(ActionBase):

    icon = "📅"
    title = "TickTick task stats"
    description = "Show a contribution calendar of completed TickTick tasks from the local database"
    cli_available: ClassVar[bool] = False

    @ActionBase.handle_exceptions("show TickTick task stats")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Open the TickTick task-stats dialog."""
        self.dialogs.show_ticktick_task_stats()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Open the TickTick task-stats dialog.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.dialogs.show_ticktick_task_stats()
```

</details>
