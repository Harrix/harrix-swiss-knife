import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

import harrix_swiss_knife as hsk
from harrix_swiss_knife import resources_rc  # noqa
from harrix_swiss_knife import main_menu_base, tray_icon


class MainMenu(main_menu_base.MainMenuBase):
    def __init__(self):
        super().__init__()

        # Menu Dev
        self.menu_dev = self.new_menu("Dev", "🛠️")
        self.add_item(self.menu_dev, hsk.dev.on_get_menu)
        self.add_item(self.menu_dev, hsk.dev.on_open_config_json)
        self.add_item(self.menu_dev, hsk.dev.on_npm_install_packages)
        self.add_item(self.menu_dev, hsk.dev.on_npm_update_packages)

        # Menu Apps
        self.menu_apps = self.new_menu("Apps", "💻")
        self.add_item(self.menu_apps, hsk.apps.on_fitness)

        # Menu Images
        self.menu_images = self.new_menu("Images", "🖼️")
        self.add_item(self.menu_images, hsk.images.on_optimize)
        self.add_item(self.menu_images, hsk.images.on_optimize_quality)
        self.add_item(self.menu_images, hsk.images.on_optimize_dialog_replace)
        self.add_item(self.menu_images, hsk.images.on_optimize_dialog)
        self.add_item(self.menu_images, hsk.images.on_optimize_file)
        self.menu_images.addSeparator()
        self.add_item(self.menu_images, hsk.images.on_clear_images)
        self.add_item(self.menu_images, hsk.images.on_open_images)
        self.add_item(self.menu_images, hsk.images.on_open_optimized_images)

        # Menu File operations
        self.menu_file = self.new_menu("File operations", "🪟")
        self.add_item(self.menu_file, hsk.file.on_all_files_to_parent_folder)
        self.add_item(self.menu_file, hsk.file.on_check_featured_image)
        self.add_item(self.menu_file, hsk.file.on_check_featured_image_in_folders)
        self.add_item(self.menu_file, hsk.file.on_block_disks)
        self.add_item(self.menu_file, hsk.file.on_open_camera_uploads)
        self.add_item(self.menu_file, hsk.file.on_tree_view_folder_ignore_hidden_folders)
        self.add_item(self.menu_file, hsk.file.on_tree_view_folder)

        # Menu Markdown
        self.menu_md = self.new_menu("Markdown", "📓")
        self.add_item(self.menu_md, hsk.md.on_diary_new_dream)
        self.add_item(self.menu_md, hsk.md.on_diary_new_with_images)
        self.add_item(self.menu_md, hsk.md.on_diary_new)
        self.add_item(self.menu_md, hsk.md.on_new_article)
        self.add_item(self.menu_md, hsk.md.on_new_note_dialog_with_images)
        self.add_item(self.menu_md, hsk.md.on_new_note_dialog)
        self.menu_md.addSeparator()
        self.add_item(self.menu_md, hsk.md.on_download_and_replace_images)
        self.add_item(self.menu_md, hsk.md.on_download_and_replace_images_folder)
        self.add_item(self.menu_md, hsk.md.on_format_yaml)
        self.add_item(self.menu_md, hsk.md.on_generate_author_book)
        self.add_item(self.menu_md, hsk.md.on_generate_image_captions_folder)
        self.add_item(self.menu_md, hsk.md.on_generate_image_captions)
        self.add_item(self.menu_md, hsk.md.on_generate_toc_folder)
        self.add_item(self.menu_md, hsk.md.on_generate_toc)
        self.add_item(self.menu_md, hsk.md.on_get_list_movies_books)
        self.add_item(self.menu_md, hsk.md.on_increase_heading_level_content)
        self.add_item(self.menu_md, hsk.md.on_prettier_folder)
        self.add_item(self.menu_md, hsk.md.on_sort_sections_folder)
        self.add_item(self.menu_md, hsk.md.on_sort_sections)
        self.add_item(self.menu_md, hsk.md.on_combine_markdown_files)

        # Menu Python
        self.menu_python = self.new_menu("Python", "py.svg")
        self.add_item(self.menu_python, hsk.py.on_sort_isort_fmt_python_code_folder)
        self.add_item(self.menu_python, hsk.py.on_uv_new_project_dialog)
        self.add_item(self.menu_python, hsk.py.on_uv_new_project)
        self.add_item(self.menu_python, hsk.py.on_sort_code)
        self.add_item(self.menu_python, hsk.py.on_sort_code_folder)
        self.add_item(self.menu_python, hsk.py.on_extract_functions_and_classes)
        self.add_item(self.menu_python, hsk.py.on_generate_md_docs)
        self.menu_python.addSeparator()
        self.add_item(self.menu_python, hsk.py.on_harrix_pylib_01_prepare)
        self.add_item(self.menu_python, hsk.py.on_harrix_pylib_02_publish)

        # MainMenu
        self.menu.addMenu(self.menu_dev)
        self.menu.addMenu(self.menu_apps)
        self.menu.addMenu(self.menu_images)
        self.menu.addMenu(self.menu_file)
        self.menu.addMenu(self.menu_md)
        self.menu.addMenu(self.menu_python)
        self.menu.addSeparator()
        self.add_item(self.menu, hsk.images.on_optimize_clipboard)
        self.add_item(self.menu, hsk.images.on_optimize_clipboard_dialog)
        self.menu.addSeparator()
        self.add_item(self.menu, hsk.dev.on_exit)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon(":/assets/logo.svg"))

    main_menu = MainMenu()

    tray_icon = tray_icon.TrayIcon(QIcon(":/assets/logo.svg"), menu=main_menu.menu, parent=app)
    tray_icon.setToolTip("harrix-swiss-knife")
    tray_icon.show()
    sys.exit(app.exec())
