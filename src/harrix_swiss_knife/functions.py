import os
from pathlib import Path
import subprocess
import tempfile
import time


def write_in_output_txt(is_show_output=True):
    def decorator(func):
        output_lines = []

        def wrapper(*args, **kwargs):
            output_lines.clear()
            print("Start")
            func(*args, **kwargs)
            data_path = Path("data")
            if not data_path.exists():
                data_path.mkdir(parents=True, exist_ok=True)
            file = Path("data/output.txt")
            output_text = "\n".join(output_lines) if output_lines else ""
            file.write_text(output_text, encoding="utf8")
            if is_show_output:
                os.startfile(file)
            print("End")

        def add_line(line):
            output_lines.append(line)
            print(line)

        wrapper.add_line = add_line
        return wrapper

    return decorator


def run_powershell_script(commands):
    command = ";".join(map(str.strip, commands.strip().splitlines()))

    process = subprocess.run(
        [
            "powershell",
            "-Command",
            (
                "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
                "$OutputEncoding = [System.Text.Encoding]::UTF8; "
                f"{command}"
            ),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return "\n".join(filter(None, [process.stdout, process.stderr]))


def run_powershell_script_as_admin(commands):
    res_output = []
    command = ";".join(map(str.strip, commands.strip().splitlines()))

    # Create a temporary file with the PowerShell script
    with tempfile.NamedTemporaryFile(suffix=".ps1", delete=False) as tmp_script_file:
        tmp_script_file.write(command.encode("utf-8"))
        tmp_script_path = tmp_script_file.name

    # Create a temporary file for the output
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_output_file:
        tmp_output_path = tmp_output_file.name

    try:
        # Wrapper script that runs the main script and writes the output to a file
        wrapper_script = f"& '{tmp_script_path}' | Out-File -FilePath '{tmp_output_path}' -Encoding UTF8"

        # Save the wrapper script to a temporary file
        with tempfile.NamedTemporaryFile(
            suffix=".ps1", delete=False
        ) as tmp_wrapper_file:
            tmp_wrapper_file.write(wrapper_script.encode("utf-8"))
            tmp_wrapper_path = tmp_wrapper_file.name

        # Command to run PowerShell with administrator privileges
        cmd = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            f"Start-Process powershell.exe -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"{tmp_wrapper_path}\"' -Verb RunAs",
        ]

        # Start the process
        process = subprocess.Popen(cmd)

        # Wait for the process to finish
        process.wait()

        # Ensure the output file has been created
        while not os.path.exists(tmp_output_path):
            time.sleep(0.1)

        # Wait until the file is fully written (can adjust wait time as needed)
        time.sleep(1)  # Delay to complete writing to the file

        # Read the output data from the file
        with open(tmp_output_path, "r", encoding="utf-8") as f:
            output = f.read()
            res_output.append(output)

    finally:
        # Delete temporary files after execution
        if os.path.exists(tmp_script_path):
            os.remove(tmp_script_path)
        if os.path.exists(tmp_output_path):
            os.remove(tmp_output_path)
        if os.path.exists(tmp_wrapper_path):
            os.remove(tmp_wrapper_path)
    return "\n".join(filter(None, res_output))
