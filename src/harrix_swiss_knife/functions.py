import os
from pathlib import Path
import subprocess


def write_in_output_txt(func):
    output_lines = []

    def wrapper(*args, **kwargs):
        output_lines.clear()
        func(*args, **kwargs)
        data_path = Path("data")
        if not data_path.exists():
            data_path.mkdir(parents=True, exist_ok=True)
        file = Path("data/output.txt")
        output_text = "\n".join(output_lines) if not output_lines else ""
        file.write_text(output_text, encoding="utf8")
        print(output_text)
        os.startfile(file)

    def add_line(line):
        output_lines.append(line)

    wrapper.add_line = add_line
    return wrapper


def run_powershell_script(commands):
    command = ";".join(map(str.strip, commands.strip().splitlines()))

    process = subprocess.run(
        [
            "powershell",
            "-Command",
            f"[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; {command}",
        ],
        capture_output=True,
        text=True,
    )
    return "\n".join(filter(None, [process.stdout, process.stderr]))
