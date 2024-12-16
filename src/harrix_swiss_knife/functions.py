import os
from pathlib import Path
import subprocess
import tempfile


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


def run_powershell_script_as_admin(commands):
    command = ";".join(map(str.strip, commands.strip().splitlines()))

    # Create a temporary file with a PowerShell script
    with tempfile.NamedTemporaryFile(suffix=".ps1", delete=False) as tmp_file:
        tmp_file.write(command.encode("utf-8"))
        tmp_script_path = tmp_file.name

    try:
        # Run PowerShell with administrator rights
        process = subprocess.run(
            [
                "powershell",
                "-Command",
                "Start-Process",
                "powershell",
                f'-ArgumentList \'"-File", "{tmp_script_path}"\'',
                "-Verb",
                "RunAs",
            ],
            check=True,
        )
    finally:
        # Delete the temporary file after execution
        os.remove(tmp_script_path)
    return "\n".join(filter(None, [process.stdout, process.stderr]))
