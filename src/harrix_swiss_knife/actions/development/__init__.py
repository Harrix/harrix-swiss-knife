"""Actions for Python development and code management."""

from harrix_swiss_knife.actions.development.about_dialog import OnAboutDialog
from harrix_swiss_knife.actions.development.clear_temp_folder import OnClearTempFolder
from harrix_swiss_knife.actions.development.create_desktop_shortcut import OnCreateDesktopShortcut
from harrix_swiss_knife.actions.development.download_optimize_dependencies import OnDownloadOptimizeDependencies
from harrix_swiss_knife.actions.development.exit_ import OnExit
from harrix_swiss_knife.actions.development.install_cli import OnInstallCli
from harrix_swiss_knife.actions.development.install_harrix_notes_explorer_extension import (
    OnInstallHarrixNotesExplorerExtension,
)
from harrix_swiss_knife.actions.development.node_update import OnNodeUpdate
from harrix_swiss_knife.actions.development.npm_manage_packages import OnNpmManagePackages
from harrix_swiss_knife.actions.development.open_config_json import OnOpenConfigJson
from harrix_swiss_knife.actions.development.sync_quick_access_to_total_commander import (
    OnSyncQuickAccessToTotalCommander,
)
from harrix_swiss_knife.actions.development.update_harrix_swiss_knife import OnUpdateHarrixSwissKnife
from harrix_swiss_knife.actions.development.uv_update import OnUvUpdate
from harrix_swiss_knife.actions.development.view_recent_action_logs import OnViewRecentActionLogs

__all__ = [
    "OnAboutDialog",
    "OnClearTempFolder",
    "OnCreateDesktopShortcut",
    "OnDownloadOptimizeDependencies",
    "OnExit",
    "OnInstallCli",
    "OnInstallHarrixNotesExplorerExtension",
    "OnNodeUpdate",
    "OnNpmManagePackages",
    "OnOpenConfigJson",
    "OnSyncQuickAccessToTotalCommander",
    "OnUpdateHarrixSwissKnife",
    "OnUvUpdate",
    "OnViewRecentActionLogs",
]
