import os
from typing import Callable
from pathlib import Path

from harrix_swiss_knife import functions

path_camera_uploads = "D:/Dropbox/Camera Uploads"


class on_block_disks:
    title: str = "Block disks"

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        commands = """
            manage-bde -lock E: -ForceDismount
            manage-bde -lock F: -ForceDismount
            """

        output = functions.run_powershell_script_as_admin(commands)
        self.__call__.add_line(output)


class on_open_camera_uploads:
    title: str = "Open Camera Uploads"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        folder_path = Path(path_camera_uploads)
        os.startfile(folder_path)
        os.startfile(folder_path / "info")
        os.startfile(folder_path / "temp")
        os.startfile(folder_path / "video")
        os.startfile(folder_path / "work")
        os.startfile(folder_path / "work_video")
        os.startfile(folder_path / "screenshots")
        self.__call__.add_line('The folder "Camera Uploads" is opened.')
