---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `pull_site_submodules.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnPullSiteSubmodules`](#%EF%B8%8F-class-onpullsitesubmodules)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnPullSiteSubmodules`

```python
class OnPullSiteSubmodules(ActionBase)
```

Run `git submodule foreach git pull origin main` in the site repository.

Uses `path_site_repo` from config (or an explicit folder from CLI).

<details>
<summary>Code:</summary>

```python
class OnPullSiteSubmodules(ActionBase):

    icon = "⬇️"
    title = "Pull site submodules"
    description = "git submodule foreach git pull origin main in the site repo"
    cli_available: ClassVar[bool] = True
    cli_hint: ClassVar[str] = "site pull-submodules"

    @ActionBase.handle_exceptions("pulling site submodules")
    def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Pull `origin main` in each submodule of the site Git repository."""
        if folder_path is not None:
            site_repo = Path(folder_path).resolve()
            if not site_repo.is_dir():
                self.add_line(f"❌ Not a folder: {site_repo}")
                if not noninteractive:
                    self.show_result()
                return
        else:
            site_repo = site_repo_from_config(self.config)
            if site_repo is None:
                self.add_line("❌ Site repository not found. Set `path_site_repo` in config.json.")
                if not noninteractive:
                    self.show_result()
                return

        self.add_line(f"📂 Site repo: {site_repo}")
        self.add_line("▶️ Command: git submodule foreach git pull origin main")

        if not noninteractive:
            confirmed = self.dialogs.get_yes_no_question(
                self.title,
                (f"Run in `{site_repo}`?\n\ngit submodule foreach git pull origin main"),
                default_yes=True,
            )
            if not confirmed:
                self.add_line("ℹ️ Cancelled.")  # noqa: RUF001
                self.show_result()
                return

        output = h.dev.run_command(_PULL_COMMAND, cwd=str(site_repo))
        self.add_line(output or "✅ Done (no output).")
        if not noninteractive:
            self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *_args: Any, **_kwargs: Any) -> None
```

Pull `origin main` in each submodule of the site Git repository.

<details>
<summary>Code:</summary>

```python
def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        if folder_path is not None:
            site_repo = Path(folder_path).resolve()
            if not site_repo.is_dir():
                self.add_line(f"❌ Not a folder: {site_repo}")
                if not noninteractive:
                    self.show_result()
                return
        else:
            site_repo = site_repo_from_config(self.config)
            if site_repo is None:
                self.add_line("❌ Site repository not found. Set `path_site_repo` in config.json.")
                if not noninteractive:
                    self.show_result()
                return

        self.add_line(f"📂 Site repo: {site_repo}")
        self.add_line("▶️ Command: git submodule foreach git pull origin main")

        if not noninteractive:
            confirmed = self.dialogs.get_yes_no_question(
                self.title,
                (f"Run in `{site_repo}`?\n\ngit submodule foreach git pull origin main"),
                default_yes=True,
            )
            if not confirmed:
                self.add_line("ℹ️ Cancelled.")  # noqa: RUF001
                self.show_result()
                return

        output = h.dev.run_command(_PULL_COMMAND, cwd=str(site_repo))
        self.add_line(output or "✅ Done (no output).")
        if not noninteractive:
            self.show_result()
```

</details>
