"""Image optimization and management actions."""

from harrix_swiss_knife.actions.images.clear_images import OnClearImages
from harrix_swiss_knife.actions.images.image_to_markdown_with_ocr import OnImageToMarkdownWithOcr
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

__all__ = [
    "OnClearImages",
    "OnImageToMarkdownWithOcr",
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
]
