"""Show sorted invocation statistics for registered menu actions."""

from __future__ import annotations

from typing import Any, ClassVar

from harrix_swiss_knife.action_title import strip_md_inline_code_markers
from harrix_swiss_knife.action_usage import load_action_usage
from harrix_swiss_knife.actions.action_usage_stats_browser import ActionUsageStatsRow
from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.quick_launcher.registry import iter_menu_actions_with_category


class OnShowActionUsageStats(ActionBase):
    """Show registered actions by usage in a sortable table (or text for CLI)."""

    icon = "📊"
    title = "Show action usage stats"
    description = "Show which menu actions are used and which are never called"
    cli_available: ClassVar[bool] = True
    cli_hint: ClassVar[str] = "dev action-usage"

    @ActionBase.handle_exceptions("show action usage stats")
    def execute(self, *args: Any, noninteractive: bool = False, **kwargs: Any) -> None:  # noqa: ARG002
        """Open usage table dialog, or print a text report when `noninteractive`."""
        # Lazy import: menu_structure registers this class (circular import).
        from harrix_swiss_knife.menu_structure import get_menu_structure  # noqa: PLC0415

        usage = load_action_usage()
        seen: set[str] = set()
        rows: list[ActionUsageStatsRow] = []
        used_count = 0
        total_calls = 0

        for action_cls, category in iter_menu_actions_with_category(get_menu_structure()):
            class_name = action_cls.__name__
            if class_name in seen:
                continue
            seen.add(class_name)

            entry = usage.get(class_name)
            count = int(entry["count"]) if entry is not None else 0
            gui = int(entry["gui"]) if entry is not None else 0
            cli = int(entry["cli"]) if entry is not None else 0
            last_used = entry["last_used"] if entry is not None else ""
            total_calls += count
            if count > 0:
                used_count += 1

            title = strip_md_inline_code_markers(action_cls.title)
            rows.append(
                ActionUsageStatsRow(
                    count=count,
                    title=title,
                    icon=getattr(action_cls, "icon", "") or "",
                    category=category,
                    gui=gui,
                    cli=cli,
                    last_used=last_used,
                ),
            )

        rows.sort(key=lambda row: (-int(row["count"]), row["title"].casefold()))
        unused_count = len(rows) - used_count
        summary = f"Actions: {len(rows)} · Unused: {unused_count} · Used: {used_count} · Total calls: {total_calls}"

        if noninteractive:
            self.add_line(summary)
            self.add_line("")
            for row in rows:
                last = row["last_used"] or "—"
                category = row["category"] or "—"
                self.add_line(
                    f"  {row['count']:>4}  {row['title']}  [{category}]  "
                    f"(gui={row['gui']} cli={row['cli']}, last {last})",
                )
            return

        self.dialogs.show_action_usage_stats_browser(rows, summary=summary)
