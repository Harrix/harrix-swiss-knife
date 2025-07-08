"""harrix-swiss-knife - Python + Node.js application for automating personal tasks in Windows."""

from harrix_swiss_knife import fitness, main_menu_base, tray_icon
from harrix_swiss_knife.actions import apps, images
from harrix_swiss_knife.actions import development as dev
from harrix_swiss_knife.actions import files as file
from harrix_swiss_knife.actions import markdown as md
from harrix_swiss_knife.actions import python as py

__all__ = ["apps", "dev", "file", "fitness", "images", "main_menu_base", "md", "py", "tray_icon"]
