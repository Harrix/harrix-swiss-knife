# -*- coding: utf-8 -*-
"""Post-process locale `strings.xml` for valid Android escaping."""
from __future__ import annotations

import re
from pathlib import Path

RES = Path(__file__).resolve().parent.parent / "app" / "src" / "main" / "res"


def fix_content(content: str) -> str:
    content = content.replace("\x1a", " - ")
    content = content.replace("\ufffd", "")
    # leftover English possessives after machine translation
    content = content.replace("\\'s", "")
    content = content.replace("foto\\'", "foto")
    content = content.replace("photo\\'", "photo")
    # broken "Don't" style translations: Non\'non / Ne \'ne
    content = re.sub(r"Non\\'non\s*", "Non ", content, flags=re.IGNORECASE)
    content = re.sub(r"Ne \\'ne\s*", "Ne ", content, flags=re.IGNORECASE)
    content = re.sub(r"Не\\'не\s*", "Не ", content)  # ignore: HP001
    content = re.sub(r"не\\'не\s*", "не ", content)  # ignore: HP001
    # protect existing escapes
    content = content.replace("\\'", "\0A\0")
    content = content.replace('\\"', "\0Q\0")
    content = content.replace("\\n", "\0N\0")
    # escape bare apostrophes / quotes
    content = content.replace("'", "\\'")
    content = content.replace('"', '\\"')
    # restore
    content = content.replace("\0A\0", "\\'")
    content = content.replace("\0Q\0", '\\"')
    content = content.replace("\0N\0", "\\n")
    return content


def fix_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    def repl(match: re.Match[str]) -> str:
        name = match.group(1)
        content = fix_content(match.group(2))
        return f'<string name="{name}">{content}</string>'

    text2 = re.sub(r'<string name="([^"]+)">([^<]*)</string>', repl, text)
    path.write_text(text2, encoding="utf-8")
    print(f"fixed {path.parent.name}")


def main() -> None:
    for folder in sorted(RES.glob("values-*")):
        f = folder / "strings.xml"
        if f.exists():
            fix_file(f)


if __name__ == "__main__":
    main()
