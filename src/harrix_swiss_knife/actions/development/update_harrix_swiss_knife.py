"""Actions for Python development and code management."""

from __future__ import annotations

import copy
import json
import shutil
import subprocess
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Literal, TypedDict, cast
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.development._github_https import (
    github_api_headers,
    validate_https_url,
)
from harrix_swiss_knife.integrations.http_download import download_https_to_path
from harrix_swiss_knife.integrations.http_transport import https_ssl_context
from harrix_swiss_knife.paths import clear_directory_contents


class OnUpdateHarrixSwissKnife(ActionBase):
    """Update Harrix stack repos from Git or GitHub ZIP archives.

    For `harrix-swiss-knife`, `harrix-pylib`, and `harrix-pyssg` paths taken from
    `paths_python_projects`: if `.git` exists, runs `git pull --ff-only` (optional
    commit when the tree is dirty). Without `.git`, downloads the default branch ZIP
    from GitHub and replaces the tree. Swiss Knife keeps `temp/` and merges
    `config/config.json` with a checkbox dialog (default: keep local values).
    """

    icon = "⬆️"
    title = "Update Harrix Swiss Knife from GitHub…"

    _PROJECT_NAMES = ("harrix-swiss-knife", "harrix-pylib", "harrix-pyssg")
    _GITHUB_UA = "Harrix-Swiss-Knife/1.0 (Python; urllib)"
    _ALLOWED_SCHEMES = ("https",)
    _GIT_DIRTY_COMMIT = "Commit all changes and pull"
    _GIT_DIRTY_SKIP = "Skip this repository"
    _GIT_DIRTY_CANCEL = "Cancel entire update"

    @ActionBase.handle_exceptions("update Harrix Swiss Knife stack")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Run updates for Harrix sibling repos (Git pull or GitHub ZIP)."""
        steps = self._collect_steps_interactive()
        if steps is None:
            return
        if not steps:
            self.add_line("Nothing to update (no valid project paths).")
            self.show_result()
            return
        self.start_thread(lambda: self._worker_run(steps), self._worker_finished, self.title, cancellable=True)

    @staticmethod
    def _build_swiss_config_merged(
        local: dict[str, Any] | None,
        incoming: dict[str, Any],
        keys_keep_local: set[str],
    ) -> dict[str, Any]:
        merged = copy.deepcopy(incoming)
        if local:
            for k, v in local.items():
                if k not in merged:
                    merged[k] = copy.deepcopy(v)
            for k in keys_keep_local:
                if k in local:
                    merged[k] = copy.deepcopy(local[k])
        return merged

    def _collect_steps_interactive(self) -> list[OnUpdateHarrixSwissKnife._UpdateStep] | None:
        raw = self.config.get("paths_python_projects")
        if not isinstance(raw, list):
            self.add_line('❌ config "paths_python_projects" must be a list.')
            return None

        by_name: dict[str, Path] = {}
        for entry in raw:
            p = Path(str(entry)).expanduser()
            name = p.name
            if name in self._PROJECT_NAMES and name not in by_name:
                try:
                    by_name[name] = p.resolve()
                except OSError:
                    self.add_line(f"⚠️ Could not resolve path: {entry}")

        ordered_paths = [by_name[n] for n in self._PROJECT_NAMES if n in by_name]
        if not ordered_paths:
            self.add_line(
                f'❌ None of {self._PROJECT_NAMES} found in "paths_python_projects". Add them in config.json.'
            )
            return None

        steps: list[OnUpdateHarrixSwissKnife._UpdateStep] = []
        for root in ordered_paths:
            if not root.is_dir():
                self.add_line(f"⚠️ Skip (not a directory): {root}")
                continue

            if (root / ".git").exists():
                dirty = self._git_porcelain(root).strip()
                commit_message: str | None = None
                if dirty:
                    choice = self.get_choice_from_list(
                        "Git: uncommitted changes",
                        f"{root.name}: the working tree has local changes. Choose an action:",
                        [self._GIT_DIRTY_COMMIT, self._GIT_DIRTY_SKIP, self._GIT_DIRTY_CANCEL],
                    )
                    if choice is None or choice == self._GIT_DIRTY_CANCEL:
                        self.add_line("❌ Update cancelled.")
                        self.show_result()
                        return None
                    if choice == self._GIT_DIRTY_SKIP:
                        steps.append(
                            {
                                "kind": "skip",
                                "path": root,
                                "commit_message": None,
                                "skip_reason": "Skipped (dirty tree)",
                            }
                        )
                        continue
                    msg = self.get_text_input(
                        "Commit message",
                        "Enter a commit message for all current changes (or cancel to skip this repo):",
                        default_value="🔧 Modify local changes before update",
                    )
                    if msg is None or not str(msg).strip():
                        self.add_line(f"⚠️ {root.name}: no commit message — skipped.")
                        steps.append(
                            {
                                "kind": "skip",
                                "path": root,
                                "commit_message": None,
                                "skip_reason": "Skipped (no commit message)",
                            }
                        )
                        continue
                    commit_message = str(msg).strip()

                steps.append(
                    {
                        "kind": "git_pull",
                        "path": root,
                        "commit_message": commit_message,
                        "skip_reason": None,
                    }
                )
            else:
                steps.append({"kind": "zip", "path": root, "commit_message": None, "skip_reason": None})

        return steps

    @staticmethod
    def _copy_tree_contents(src: Path, dest: Path) -> None:
        dest.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            target = dest / item.name
            if item.is_dir():
                shutil.copytree(item, target, dirs_exist_ok=True)
            else:
                shutil.copy2(item, target)

    @staticmethod
    def _deep_equal_json(a: object, b: object) -> bool:
        if type(a) is not type(b):
            return False
        if isinstance(a, dict):
            b_dict = cast("dict[str, Any]", b)
            a_dict = cast("dict[str, Any]", a)
            if set(a_dict) != set(b_dict):
                return False
            return all(OnUpdateHarrixSwissKnife._deep_equal_json(a_dict[k], b_dict[k]) for k in a_dict)
        if isinstance(a, list):
            b_list = cast("list[Any]", b)
            a_list = cast("list[Any]", a)
            if len(a_list) != len(b_list):
                return False
            return all(OnUpdateHarrixSwissKnife._deep_equal_json(x, y) for x, y in zip(a_list, b_list, strict=True))
        return a == b

    def _download_https_to_path(self, url: str, dest: Path) -> None:
        validate_https_url(url)
        download_https_to_path(
            url,
            dest,
            headers={"User-Agent": self._GITHUB_UA},
            timeout=300,
            chunk_size=256 * 1024,
            should_cancel=self.is_work_cancelled,
        )

    def _fetch_github_default_branch(self, owner: str, repo: str) -> str:
        url = f"https://api.github.com/repos/{owner}/{repo}"
        validate_https_url(url)
        req = Request(url, headers=github_api_headers())  # noqa: S310
        with urlopen(req, timeout=60, context=https_ssl_context()) as resp:  # noqa: S310
            data = json.loads(resp.read().decode())
        branch = data.get("default_branch")
        if not isinstance(branch, str) or not branch.strip():
            msg = "Missing default_branch in API response"
            raise ValueError(msg)
        return branch.strip()

    @staticmethod
    def _git_porcelain(repo: Path) -> str:
        p = OnUpdateHarrixSwissKnife._git_run(repo, "status", "--porcelain")
        return p.stdout if p.returncode == 0 else ""

    @staticmethod
    def _git_run(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],  # noqa: S607
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    @staticmethod
    @staticmethod
    @staticmethod
    def _load_json_dict(path: Path) -> tuple[dict[str, Any] | None, str | None]:
        if not path.is_file():
            return None, None
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as e:
            return None, str(e)
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            return None, str(e)
        if not isinstance(data, dict):
            return None, "Root JSON value must be an object"
        return cast("dict[str, Any]", data), None

    @staticmethod
    def _restore_config_dir_except_json(backup: Path, dest_config: Path) -> None:
        if not backup.is_dir():
            return
        for f in backup.rglob("*"):
            if not f.is_file():
                continue
            rel = f.relative_to(backup)
            if rel.as_posix() == "config.json":
                continue
            out = dest_config / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, out)

    @staticmethod
    def _top_level_keys_differing(local: dict[str, Any], incoming: dict[str, Any]) -> list[str]:
        out: list[str] = []
        for k, v_loc in local.items():
            if k not in incoming:
                continue
            if not OnUpdateHarrixSwissKnife._deep_equal_json(v_loc, incoming[k]):
                out.append(k)
        return sorted(out)

    @ActionBase.handle_exceptions("update Harrix Swiss Knife stack thread completion")
    def _worker_finished(self, merge_tasks: Any) -> None:
        if not isinstance(merge_tasks, list):
            merge_tasks = []

        for task in merge_tasks:
            if not isinstance(task, dict):
                continue
            cfg_path = task.get("config_path")
            if not isinstance(cfg_path, Path):
                continue
            err = task.get("error")
            if err:
                continue
            local_read_error = str(task.get("local_read_error") or "")
            if local_read_error:
                self.add_line(f"⚠️ {cfg_path}: skipping config merge ({local_read_error}).")
                continue
            local = task.get("local")
            incoming = task.get("incoming")
            if not isinstance(incoming, dict):
                continue

            if local is None:
                self._write_config_json_pretty(cfg_path, incoming)
                self.add_line(f"✅ Wrote {cfg_path.name} (no previous local JSON).")
                continue

            if not isinstance(local, dict):
                self.add_line(f"⚠️ {cfg_path}: skipping merge (unexpected local type).")
                continue

            local_dict = local
            diff_keys = self._top_level_keys_differing(local_dict, incoming)
            if not diff_keys:
                merged = self._build_swiss_config_merged(local_dict, incoming, set())
                self._write_config_json_pretty(cfg_path, merged)
                self.add_line(f"✅ Merged {cfg_path} (no conflicting top-level keys).")
                continue

            labels = [f"Keep current value: {k}" for k in diff_keys]
            selected = self.get_checkbox_selection(
                "config.json merge",
                "Checked keys keep your current value. Uncheck to take the value from the repository.",
                labels,
                default_selected=labels,
            )
            if selected is None:
                self.add_line(f"⚠️ {cfg_path}: merge dialog cancelled — left repository version on disk.")
                continue

            key_by_label = {f"Keep current value: {k}": k for k in diff_keys}
            keep_local_keys = {key_by_label[lab] for lab in selected if lab in key_by_label}
            merged = self._build_swiss_config_merged(local_dict, incoming, keep_local_keys)
            self._write_config_json_pretty(cfg_path, merged)
            self.add_line(f"✅ Merged {cfg_path} with your key selection.")

        self.show_toast("Harrix projects update finished")
        self.show_result()

    def _worker_git_pull(self, repo: Path, commit_message: str | None) -> list[OnUpdateHarrixSwissKnife._MergeTask]:
        tasks: list[OnUpdateHarrixSwissKnife._MergeTask] = []
        swiss = repo.name == "harrix-swiss-knife"
        cfg = repo / "config" / "config.json"
        local_data: dict[str, Any] | None = None
        local_read_error = ""
        if swiss:
            local_data, local_err = self._load_json_dict(cfg)
            if local_err:
                self.add_line(f"⚠️ {repo.name}: could not read local config.json: {local_err}")
                local_read_error = local_err

        if commit_message:
            self.add_line(f"🔵 {repo.name}: committing local changes…")
            add_p = self._git_run(repo, "add", "-A")
            if add_p.returncode != 0:
                self.add_line(f"❌ git add failed: {add_p.stderr.strip() or add_p.stdout}")
                return tasks
            commit_p = self._git_run(repo, "commit", "-m", commit_message)
            if commit_p.returncode != 0:
                self.add_line(f"❌ git commit failed: {commit_p.stderr.strip() or commit_p.stdout}")
                return tasks
            self.add_line(f"✅ {repo.name}: committed.")

        self.add_line(f"🔵 {repo.name}: git pull --ff-only…")
        pull_p = self._git_run(repo, "pull", "--ff-only")
        out = (pull_p.stdout + "\n" + pull_p.stderr).strip()
        if out:
            self.add_line(out)
        if pull_p.returncode != 0:
            self.add_line(f"❌ {repo.name}: git pull failed (exit {pull_p.returncode}).")
            return tasks
        self.add_line(f"✅ {repo.name}: pull completed.")

        if swiss:
            incoming, inc_err = self._load_json_dict(cfg)
            if inc_err:
                self.add_line(f"❌ {repo.name}: config.json after pull is invalid: {inc_err}")
                tasks.append(
                    {
                        "config_path": cfg,
                        "local": local_data,
                        "incoming": None,
                        "error": inc_err,
                        "local_read_error": local_read_error,
                    }
                )
            else:
                tasks.append(
                    {
                        "config_path": cfg,
                        "local": local_data,
                        "incoming": incoming,
                        "error": None,
                        "local_read_error": local_read_error,
                    }
                )
        return tasks

    def _worker_run(
        self, steps: list[OnUpdateHarrixSwissKnife._UpdateStep]
    ) -> list[OnUpdateHarrixSwissKnife._MergeTask]:
        owner = str(self.config.get("github_user") or "Harrix").strip() or "Harrix"
        merge_tasks: list[OnUpdateHarrixSwissKnife._MergeTask] = []

        for step in steps:
            self.raise_if_work_cancelled()
            path = step["path"]
            if step["kind"] == "skip":
                self.add_line(f"⏭️ {path.name}: {step.get('skip_reason') or 'skipped'}")
                continue
            if step["kind"] == "git_pull":
                merge_tasks.extend(self._worker_git_pull(path, step.get("commit_message")))
            elif step["kind"] == "zip":
                merge_tasks.extend(self._worker_zip_update(path, owner))

        return merge_tasks

    def _worker_zip_swiss_knife(
        self, dest: Path, src_root: Path, cfg: Path, tmp_path: Path
    ) -> list[OnUpdateHarrixSwissKnife._MergeTask]:
        tasks: list[OnUpdateHarrixSwissKnife._MergeTask] = []
        local_data, local_err = self._load_json_dict(cfg)
        if local_err:
            self.add_line(f"⚠️ harrix-swiss-knife: could not read local config.json: {local_err}")

        temp_bak = tmp_path / "temp_bak"
        cfg_bak = tmp_path / "config_bak"
        temp_dir = dest / "temp"
        config_dir = dest / "config"

        if temp_dir.is_dir():
            shutil.copytree(temp_dir, temp_bak, dirs_exist_ok=True)
        if config_dir.is_dir():
            shutil.copytree(config_dir, cfg_bak, dirs_exist_ok=True)

        self.add_line("🔵 harrix-swiss-knife: replacing directory contents (ZIP)…")
        clear_directory_contents(dest)
        self._copy_tree_contents(src_root, dest)

        if temp_bak.is_dir():
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
            shutil.copytree(temp_bak, temp_dir, dirs_exist_ok=True)
            self.add_line("✅ Restored temp/ from backup.")

        if cfg_bak.is_dir():
            config_dir.mkdir(parents=True, exist_ok=True)
            self._restore_config_dir_except_json(cfg_bak, config_dir)
            self.add_line("✅ Restored config/* from backup (except config.json).")

        incoming, inc_err = self._load_json_dict(cfg)
        local_read_error = local_err or ""
        if inc_err:
            self.add_line(f"❌ harrix-swiss-knife: config.json invalid after ZIP: {inc_err}")
            tasks.append(
                {
                    "config_path": cfg,
                    "local": local_data,
                    "incoming": None,
                    "error": inc_err,
                    "local_read_error": local_read_error,
                }
            )
        else:
            tasks.append(
                {
                    "config_path": cfg,
                    "local": local_data,
                    "incoming": incoming,
                    "error": None,
                    "local_read_error": local_read_error,
                }
            )

        self.add_line("✅ harrix-swiss-knife: tree updated from ZIP.")
        return tasks

    def _worker_zip_update(self, dest: Path, owner: str) -> list[OnUpdateHarrixSwissKnife._MergeTask]:
        tasks: list[OnUpdateHarrixSwissKnife._MergeTask] = []
        repo_name = dest.name
        cfg = dest / "config" / "config.json"

        try:
            branch = self._fetch_github_default_branch(owner, repo_name)
        except (OSError, ValueError, URLError, HTTPError, json.JSONDecodeError) as e:
            self.add_line(f"❌ {repo_name}: could not resolve default branch: {e}")
            return tasks

        zip_url = f"https://github.com/{owner}/{repo_name}/archive/refs/heads/{branch}.zip"
        self.add_line(f"⬇️ {repo_name}: downloading {zip_url} …")

        try:
            with TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                zip_path = tmp_path / f"{repo_name}.zip"
                self._download_https_to_path(zip_url, zip_path)
                extract_root = tmp_path / "extracted"
                extract_root.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zf.extractall(extract_root)
                members = [p for p in extract_root.iterdir() if p.name]
                if len(members) != 1 or not members[0].is_dir():
                    self.add_line(f"❌ {repo_name}: unexpected ZIP layout.")
                    return tasks
                src_root = members[0]

                if repo_name == "harrix-swiss-knife":
                    tasks.extend(self._worker_zip_swiss_knife(dest, src_root, cfg, tmp_path))
                else:
                    self.add_line(f"🔵 {repo_name}: replacing directory contents…")
                    clear_directory_contents(dest)
                    self._copy_tree_contents(src_root, dest)
                    self.add_line(f"✅ {repo_name}: updated from ZIP.")
        except (OSError, ValueError, URLError, HTTPError) as e:
            self.add_line(f"❌ {repo_name}: ZIP update failed: {e}")

        return tasks

    @staticmethod
    def _write_config_json_pretty(path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        path.write_text(text, encoding="utf-8")

    class _UpdateStep(TypedDict):
        kind: Literal["git_pull", "zip", "skip"]
        path: Path
        commit_message: str | None
        skip_reason: str | None

    class _MergeTask(TypedDict):
        config_path: Path
        local: dict[str, Any] | None
        incoming: dict[str, Any] | None
        error: str | None
        local_read_error: str
