"""Shared table view delegates for apps."""

from harrix_swiss_knife.apps.common.delegates.combo_box_delegate import ComboBoxDelegate
from harrix_swiss_knife.apps.common.delegates.date_delegate import DateDelegate
from harrix_swiss_knife.apps.common.delegates.name_local_list_delegate import (
    NAME_LOCAL_ROLE,
    NameLocalLayout,
    NameLocalListDelegate,
)
from harrix_swiss_knife.apps.common.delegates.yes_no_combo_delegate import YesNoComboDelegate

__all__ = [
    "NAME_LOCAL_ROLE",
    "ComboBoxDelegate",
    "DateDelegate",
    "NameLocalLayout",
    "NameLocalListDelegate",
    "YesNoComboDelegate",
]
