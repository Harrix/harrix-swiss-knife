"""Split actions/<section>.py into actions/<section>/ with one class per file."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

RESERVED_MODULE_NAMES = frozenset({"exit"})


def class_to_module(class_name: str) -> str:
    """Map OnAboutDialog -> about_dialog; OnExit -> exit_."""
    if not class_name.startswith("On"):
        msg = f"Expected On* class name, got {class_name!r}"
        raise ValueError(msg)
    base = class_name[2:]
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", base)
    snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
    if snake in RESERVED_MODULE_NAMES:
        return f"{snake}_"
    return snake


def split_module(src_path: Path, package_name: str) -> list[str]:
    source = src_path.read_text(encoding="utf-8")
    lines = source.splitlines(keepends=True)
    tree = ast.parse(source)

    header_end = 0
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name.startswith("On"):
            break
        header_end = max(header_end, node.end_lineno or node.lineno)

    header_lines = lines[:header_end]
    has_future = any(isinstance(n, ast.ImportFrom) and n.module == "__future__" for n in tree.body[: header_end // 1])
    has_future = "from __future__ import annotations" in "".join(header_lines)

    pkg_doc = ast.get_docstring(tree)
    import_lines: list[str] = []
    for line in header_lines:
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        if stripped.startswith("from __future__"):
            continue
        import_lines.append(line)

    header_parts: list[str] = []
    if pkg_doc:
        header_parts.append(f'"""{pkg_doc}"""\n\n')
    if not has_future:
        header_parts.append("from __future__ import annotations\n\n")
    elif any("from __future__" in ln for ln in header_lines):
        for line in header_lines:
            if "from __future__" in line:
                header_parts.append(line if line.endswith("\n") else line + "\n")
        header_parts.append("\n")
    header_parts.extend(import_lines)
    header = "".join(header_parts)

    classes: list[tuple[str, str]] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name.startswith("On"):
            start = node.lineno - 1
            end = node.end_lineno
            class_source = "".join(lines[start:end])
            if not class_source.endswith("\n"):
                class_source += "\n"
            classes.append((node.name, class_source))

    dest_dir = src_path.parent / package_name
    dest_dir.mkdir(parents=True, exist_ok=True)

    exports: list[str] = []
    for class_name, class_source in classes:
        module_stem = class_to_module(class_name)
        file_path = dest_dir / f"{module_stem}.py"
        body = header.rstrip() + "\n\n\n" + class_source
        file_path.write_text(body, encoding="utf-8")
        exports.append(class_name)

    pkg_doc = ast.get_docstring(tree) or "Actions package."
    init_lines = [
        f'"""{pkg_doc}"""',
        "",
    ]
    for class_name in exports:
        module_stem = class_to_module(class_name)
        init_lines.append(
            f"from harrix_swiss_knife.actions.{package_name}.{module_stem} import {class_name}",
        )
    init_lines.extend(["", "__all__ = [", *[f'    "{name}",' for name in exports], "]", ""])
    (dest_dir / "__init__.py").write_text("\n".join(init_lines) + "\n", encoding="utf-8")
    return exports


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: split_actions_module.py <section>", file=sys.stderr)
        return 1
    section = argv[1]
    root = Path(__file__).resolve().parents[1]
    src = root / "src" / "harrix_swiss_knife" / "actions" / f"{section}.py"
    if not src.is_file():
        print(f"Missing {src}", file=sys.stderr)
        return 1
    names = split_module(src, section)
    print(f"Split {src.name} -> {section}/ ({len(names)} classes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
