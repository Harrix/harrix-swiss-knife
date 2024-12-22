from datetime import datetime
from PySide6.QtWidgets import QFileDialog

from harrix_swiss_knife import functions

path_default = (
    f"C:/GitHub/_content__harrix-dev/harrix.dev-articles-{datetime.now().year}"
)


class on_images_optimize:
    title = "Optimize images"

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs):
        commands = "npm run optimize"

        result_output = functions.run_powershell_script(commands)
        self.__call__.add_line(result_output)


class on_image_optimize_dialog:
    title = "Optimize images in  …"

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs):
        title = "Project directory"
        folder_path = QFileDialog.getExistingDirectory(None, title, path_default)

        if folder_path:
            self.path = folder_path
        else:
            self.__call__.add_line("The directory was not selected.")
            return

        commands = f'npm run optimize imagesDir="{folder_path}"'

        result_output = functions.run_powershell_script(commands)


        self.__call__.add_line(result_output)
