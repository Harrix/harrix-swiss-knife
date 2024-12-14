import os
from pathlib import Path


def write_in_output_txt(func):
    output_lines = []

    def wrapper(*args, **kwargs):
        output_lines.clear()
        func(*args, **kwargs)
        file = Path("output.txt")
        file.write_text("\n".join(output_lines), encoding="utf8")
        print("\n".join(output_lines))
        os.startfile(file)

    def add_line(line):
        output_lines.append(line)

    wrapper.add_line = add_line
    return wrapper
