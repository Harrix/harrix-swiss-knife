"""Shared chart helpers used by tracker applications.

Contains the stable parts of `ChartOperations` that were previously duplicated
in `finance/mixins.py`, `fitness/mixins.py`, `food/mixins.py`, and
`habits/mixins.py`:

- `_add_stats_box`: renders a semi-transparent statistics box on an axes.
- `_show_no_data_label`: inserts a centered `No data` `QLabel` into a layout.
- `_format_default_stats`: formats `Min | Max | Avg` summary.
- `_clear_layout`: removes widgets (and closes matplotlib figures) from a
  layout; parametrised via `close_matplotlib_figures`.

More complex chart plotting logic remains in each app's own
`ChartOperations` mixin because it is tightly coupled to the domain-specific
schema (categories, units, color strategies, etc.).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from PySide6.QtWidgets import QLayout


class ChartOperationsBase:
    """Mixin with generic chart / layout helpers."""

    def _add_stats_box(self, ax: Axes, stats_text: str, color: str = "lightgray") -> None:
        """Add a statistics box at the bottom-center of an axes.

        Args:

        - `ax` (`Axes`): Matplotlib axes object.
        - `stats_text` (`str`): Text to display.
        - `color` (`str`): Background color. Defaults to `"lightgray"`.

        """
        ax.text(
            0.5,
            0.02,
            stats_text,
            transform=ax.transAxes,
            ha="center",
            va="bottom",
            fontsize=10,
            bbox={"boxstyle": "round,pad=0.3", "facecolor": color, "alpha": 0.8},
        )

    def _clear_layout(self, layout: QLayout, *, close_matplotlib_figures: bool = True) -> None:
        """Clear all widgets from a layout.

        Args:

        - `layout` (`QLayout`): Layout to clear.
        - `close_matplotlib_figures` (`bool`): When True (default), close
          Matplotlib figures attached to removed canvases.

        """
        for i in reversed(range(layout.count())):
            item = layout.takeAt(i)
            if item is None:
                continue

            widget = item.widget()
            if widget is not None:
                if close_matplotlib_figures and isinstance(widget, FigureCanvas) and hasattr(widget, "figure"):
                    try:
                        plt.close(widget.figure)
                    except Exception as e:
                        print(f"Error closing Matplotlib figure: {e}")

                widget.hide()
                widget.deleteLater()
                continue

            child_layout = item.layout()
            if child_layout is not None:
                self._clear_layout(child_layout, close_matplotlib_figures=close_matplotlib_figures)

    def _format_default_stats(
        self,
        values: list[float],
        unit: str = "",
        *,
        filter_none: bool = False,
    ) -> str:
        """Format a `Min | Max | Avg` summary line.

        Args:

        - `values` (`list[float]`): Numeric values.
        - `unit` (`str`): Unit suffix. Defaults to `""`.
        - `filter_none` (`bool`): When True, remove `None` items first and
          return `"No data"` if no values remain. Defaults to `False`.

        Returns:

        - `str`: Formatted stats string.

        """
        if filter_none:
            values = [v for v in values if v is not None]
            if not values:
                return "No data"

        min_val = min(values)
        max_val = max(values)
        avg_val = sum(values) / len(values)
        unit_suffix = f" {unit}" if unit else ""

        if all(isinstance(v, int) for v in values):
            return (
                f"Min: {int(min_val)}{unit_suffix} | Max: {int(max_val)}{unit_suffix} | Avg: {avg_val:.1f}{unit_suffix}"
            )
        return f"Min: {min_val:.1f}{unit_suffix} | Max: {max_val:.1f}{unit_suffix} | Avg: {avg_val:.1f}{unit_suffix}"

    def _show_no_data_label(self, layout: QLayout, text: str) -> None:
        """Show a centered text label in the layout.

        Args:

        - `layout` (`QLayout`): Layout to populate.
        - `text` (`str`): Text to display.

        """
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
