"""Show sorted invocation statistics for registered menu actions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from harrix_swiss_knife.action_title import strip_md_inline_code_markers
from harrix_swiss_knife.action_usage import load_action_usage
from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.quick_launcher.registry import iter_menu_structure

if TYPE_CHECKING:
    from harrix_swiss_knife.action_usage import ActionUsageEntry


class OnShowActionUsageStats(ActionBase):
    """List registered actions by usage: unused first, then used by count."""

    icon = "📊"
    title = "Show action usage stats"
    description = "Show which menu actions are used and which are never called"
    cli_available: ClassVar[bool] = True
    cli_hint: ClassVar[str] = "dev action-usage"

    @ActionBase.handle_exceptions("show action usage stats")
    def execute(self, *args: Any, noninteractive: bool = False, **kwargs: Any) -> None:  # noqa: ARG002
        """Print unused and used actions from menu structure plus saved counters."""
        # Lazy import: menu_structure registers this class (circular import).
        from harrix_swiss_knife.menu_structure import get_menu_structure  # noqa: PLC0415

        usage = load_action_usage()
        action_classes = list(dict.fromkeys(iter_menu_structure(get_menu_structure())))
        unused: list[type[ActionBase]] = []
        used: list[tuple[type[ActionBase], ActionUsageEntry]] = []
        total_calls = 0

        for action_cls in action_classes:
            entry = usage.get(action_cls.__name__)
            count = int(entry["count"]) if entry is not None else 0
            total_calls += count
            if count == 0 or entry is None:
                unused.append(action_cls)
            else:
                used.append((action_cls, entry))

        unused.sort(key=lambda cls: strip_md_inline_code_markers(cls.title).casefold())
        used.sort(
            key=lambda item: (-int(item[1]["count"]), strip_md_inline_code_markers(item[0].title).casefold()),
        )

        self.add_line(
            f"Actions: {len(action_classes)} · Unused: {len(unused)} · Used: {len(used)} · Total calls: {total_calls}",
        )
        self.add_line("")
        self.add_line(f"Unused ({len(unused)}):")
        if unused:
            for action_cls in unused:
                self.add_line(f"  {strip_md_inline_code_markers(action_cls.title)}")
        else:
            self.add_line("  (none)")

        self.add_line("")
        self.add_line(f"Used ({len(used)}):")
        if used:
            for action_cls, entry in used:
                title = strip_md_inline_code_markers(action_cls.title)
                last = entry["last_used"] or "?"
                self.add_line(
                    f"  {entry['count']:>4}  {title}  (gui={entry['gui']} cli={entry['cli']}, last {last})",
                )
        else:
            self.add_line("  (none)")

        if not noninteractive:
            self.show_result()
