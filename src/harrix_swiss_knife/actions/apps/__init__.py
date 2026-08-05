"""Actions for launching applications."""

from harrix_swiss_knife.actions.apps.finance import OnFinance
from harrix_swiss_knife.actions.apps.fitness import OnFitness
from harrix_swiss_knife.actions.apps.food import OnFood
from harrix_swiss_knife.actions.apps.habits import OnHabits
from harrix_swiss_knife.actions.apps.media_sorter import OnMediaSorter

__all__ = [
    "OnFinance",
    "OnFitness",
    "OnFood",
    "OnHabits",
    "OnMediaSorter",
]
