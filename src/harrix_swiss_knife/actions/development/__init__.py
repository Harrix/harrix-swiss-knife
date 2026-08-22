"""Actions for development tooling and app maintenance."""

from harrix_swiss_knife.actions.development.about_dialog import OnAboutDialog
from harrix_swiss_knife.actions.development.add_to_autostart import OnAddToAutostart
from harrix_swiss_knife.actions.development.build_install_zips import OnBuildInstallZips
from harrix_swiss_knife.actions.development.clear_temp_folder import OnClearTempFolder
from harrix_swiss_knife.actions.development.create_desktop_shortcut import OnCreateDesktopShortcut
from harrix_swiss_knife.actions.development.download_optimize_dependencies import OnDownloadOptimizeDependencies
from harrix_swiss_knife.actions.development.exit_ import OnExit
from harrix_swiss_knife.actions.development.install_cli import OnInstallCli
from harrix_swiss_knife.actions.development.npm_manage_packages import OnNpmManagePackages
from harrix_swiss_knife.actions.development.open_config_json import OnOpenConfigJson
from harrix_swiss_knife.actions.development.settings_editor import OnSettingsEditor
from harrix_swiss_knife.actions.development.setup_data_for_hsk import OnSetupDataForHsk
from harrix_swiss_knife.actions.development.show_action_usage_stats import OnShowActionUsageStats
from harrix_swiss_knife.actions.development.sync_quick_access_to_total_commander import (
    OnSyncQuickAccessToTotalCommander,
)
from harrix_swiss_knife.actions.development.transfer_private_data import OnTransferPrivateData
from harrix_swiss_knife.actions.development.update_harrix_swiss_knife import OnUpdateHarrixSwissKnife
from harrix_swiss_knife.actions.development.update_node import OnUpdateNode
from harrix_swiss_knife.actions.development.update_uv import OnUpdateUv
from harrix_swiss_knife.actions.development.upgrade_uv_python import OnUpgradeUvPython
from harrix_swiss_knife.actions.development.view_recent_action_logs import OnViewRecentActionLogs

__all__ = [
    "OnAboutDialog",
    "OnAddToAutostart",
    "OnBuildInstallZips",
    "OnClearTempFolder",
    "OnCreateDesktopShortcut",
    "OnDownloadOptimizeDependencies",
    "OnExit",
    "OnInstallCli",
    "OnNpmManagePackages",
    "OnOpenConfigJson",
    "OnSettingsEditor",
    "OnSetupDataForHsk",
    "OnShowActionUsageStats",
    "OnSyncQuickAccessToTotalCommander",
    "OnTransferPrivateData",
    "OnUpdateHarrixSwissKnife",
    "OnUpdateNode",
    "OnUpdateUv",
    "OnUpgradeUvPython",
    "OnViewRecentActionLogs",
]
