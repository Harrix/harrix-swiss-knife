"""Image optimization and management actions."""

from harrix_swiss_knife.actions.images.clear_images import OnClearImages
from harrix_swiss_knife.actions.images.open_images import OnOpenImages
from harrix_swiss_knife.actions.images.open_optimized_images import OnOpenOptimizedImages
from harrix_swiss_knife.actions.images.open_photos_in_viewer import OnOpenPhotosInViewer
from harrix_swiss_knife.actions.images.optimize import OnOptimize
from harrix_swiss_knife.actions.images.optimize_clipboard import OnOptimizeClipboard
from harrix_swiss_knife.actions.images.optimize_clipboard_dialog import OnOptimizeClipboardDialog
from harrix_swiss_knife.actions.images.optimize_dialog_replace import OnOptimizeDialogReplace
from harrix_swiss_knife.actions.images.optimize_quality import OnOptimizeQuality
from harrix_swiss_knife.actions.images.optimize_resize import OnOptimizeResize
from harrix_swiss_knife.actions.images.optimize_single_image import OnOptimizeSingleImage
from harrix_swiss_knife.actions.images.recognize_text_with_ai import OnRecognizeTextWithAI
from harrix_swiss_knife.actions.images.recognize_text_with_ocr import OnRecognizeTextWithOcr
from harrix_swiss_knife.actions.images.screenshot_region import OnScreenshotRegion
from harrix_swiss_knife.actions.images.screenshot_region_clipboard import OnScreenshotRegionClipboard

__all__ = [
    "OnClearImages",
    "OnOpenImages",
    "OnOpenOptimizedImages",
    "OnOpenPhotosInViewer",
    "OnOptimize",
    "OnOptimizeClipboard",
    "OnOptimizeClipboardDialog",
    "OnOptimizeDialogReplace",
    "OnOptimizeQuality",
    "OnOptimizeResize",
    "OnOptimizeSingleImage",
    "OnRecognizeTextWithAI",
    "OnRecognizeTextWithOcr",
    "OnScreenshotRegion",
    "OnScreenshotRegionClipboard",
]
