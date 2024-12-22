import os
from pathlib import Path

from harrix_swiss_knife import functions


class on_block_disks:
    title = "Block disks"

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs):
        commands = """
            manage-bde -lock E: -ForceDismount
            manage-bde -lock F: -ForceDismount
            """

        result_output = functions.run_powershell_script_as_admin(commands)
        self.__call__.add_line(result_output)


class on_open_camera_uploads:
    title = "Open Camera Uploads"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs):
        folder_path = Path("D:/Dropbox/Camera Uploads")
        os.startfile(folder_path)
        os.startfile(folder_path / "info")
        os.startfile(folder_path / "temp")
        os.startfile(folder_path / "video")
        os.startfile(folder_path / "work")
        os.startfile(folder_path / "work_video")
        os.startfile(folder_path / "screenshots")
        os.startfile(folder_path / "trees_in_city")
