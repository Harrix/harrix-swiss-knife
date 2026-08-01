"""Lock BitLocker-encrypted drives listed in config."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


class OnLockDisks(ActionBase):
    """Lock BitLocker-encrypted drives.

    This action locks all drives specified in the configuration's `block_drives` list
    using BitLocker encryption, forcibly dismounting them if necessary to ensure
    secure protection of the drive contents.

    """

    icon = "🔒"
    title = "Lock disks (BitLocker)"

    @ActionBase.handle_exceptions("locking disks")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Lock BitLocker-encrypted drives."""
        drives = self.config.get("block_drives") or []
        if not drives:
            self.add_line('❌ config "block_drives" is missing or empty.')
            self.show_result()
            return
        commands = "\n".join([f"manage-bde -lock {drive}: -ForceDismount" for drive in drives])
        result = h.dev.run_powershell_script_as_admin(commands)
        self.add_line(result)
        self.show_result()
