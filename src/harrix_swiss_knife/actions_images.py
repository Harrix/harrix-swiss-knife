from datetime import datetime
from PySide6.QtWidgets import QFileDialog

from harrix_swiss_knife import functions

path_default = (
    f"C:/GitHub/_content__harrix-dev/harrix.dev-articles-{datetime.now().year}"
)


class on_images_optimize:
    title = "Optimize images"

    @functions.write_in_output_txt
    def __call__(self, *args, **kwargs):
        f = on_images_optimize.__call__

        commands = "npm run optimize"

        result_output = functions.run_powershell_script(commands)
        f.add_line(result_output)


class on_images_optimize:
    title = "Optimize images"

    @functions.write_in_output_txt
    def __call__(self, *args, **kwargs):
        f = on_images_optimize.__call__

        commands = "npm run optimize"

        result_output = functions.run_powershell_script(commands)
        f.add_line(result_output)


class on_image_optimize_dialog:
    title = "Optimize images in  …"

    @functions.write_in_output_txt
    def __call__(self, *args, **kwargs):
        f = on_image_optimize_dialog.__call__

        title = "Project directory"
        folder_path = QFileDialog.getExistingDirectory(None, title, path_default)

        if folder_path:
            self.path = folder_path
        else:
            f.add_line("The directory was not selected.")
            return

        commands = f'npm run optimize imagesDir="{folder_path}" replace=true'

        result_output = functions.run_powershell_script(commands)
        f.add_line(result_output)
