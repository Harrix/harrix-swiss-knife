"""Shared Qt widgets for tracker applications."""

from harrix_swiss_knife.apps.common.widgets.compact_image_drop_zone import CompactImageDropZone
from harrix_swiss_knife.apps.common.widgets.file_drop_widget import FileDropWidget, FilesListWidget
from harrix_swiss_knife.apps.common.widgets.image_drop_widget import ImageDropWidget
from harrix_swiss_knife.apps.common.widgets.images_list_widget import ImagesListWidget
from harrix_swiss_knife.apps.common.widgets.path_drop_helpers import install_url_drop_handlers

__all__ = [
    "CompactImageDropZone",
    "FileDropWidget",
    "FilesListWidget",
    "ImageDropWidget",
    "ImagesListWidget",
    "install_url_drop_handlers",
]
