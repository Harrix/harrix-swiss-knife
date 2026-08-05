"""Delegates for finance application tables."""

from harrix_swiss_knife.apps.finance.delegates.amount_delegate import AmountDelegate
from harrix_swiss_knife.apps.finance.delegates.category_combo_box_delegate import CategoryComboBoxDelegate
from harrix_swiss_knife.apps.finance.delegates.category_suggest_delegate import NAME_RU_ROLE, CategorySuggestDelegate
from harrix_swiss_knife.apps.finance.delegates.currency_combo_box_delegate import CurrencyComboBoxDelegate
from harrix_swiss_knife.apps.finance.delegates.date_delegate import DateDelegate
from harrix_swiss_knife.apps.finance.delegates.description_delegate import DescriptionDelegate
from harrix_swiss_knife.apps.finance.delegates.report_amount_delegate import ReportAmountDelegate
from harrix_swiss_knife.apps.finance.delegates.tag_delegate import TagDelegate

__all__ = [
    "NAME_RU_ROLE",
    "AmountDelegate",
    "CategoryComboBoxDelegate",
    "CategorySuggestDelegate",
    "CurrencyComboBoxDelegate",
    "DateDelegate",
    "DescriptionDelegate",
    "ReportAmountDelegate",
    "TagDelegate",
]
