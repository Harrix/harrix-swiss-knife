import ast
import shutil
from pathlib import Path

import harrix_pylib as h


def generate_docs_for_project(folder: Path | str, beginning_of_md: str, domain: str) -> str:
    result_lines = []
    folder = Path(folder)

    docs_folder = folder / "docs"
    docs_folder.mkdir(parents=True, exist_ok=True)
    shutil.copytree(folder / "img", docs_folder / "img", dirs_exist_ok=True)
    result_lines.append(f"Folder img is copied.")

    list_funcs_all = ""

    for filename in (Path(folder) / "src").rglob(f"*.py"):
        if not (filename.is_file() and not filename.stem.startswith("__")):
            continue

        list_funcs = h.py.extract_functions_and_classes(filename, True, domain)
        docs = generate_markdown_documentation(filename)

        filename_docs = docs_folder / f"{filename.stem}.md"
        Path(filename_docs).write_text(beginning_of_md + "\n" + docs, encoding="utf8")

        list_funcs_all += list_funcs + "\n\n"

        result_lines.append(f"File {filename.name} is processed.")

    if len(list_funcs_all.splitlines()) > 2:
        list_funcs_all = list_funcs_all[:-1]

    h.md.replace_section(folder / "README.md", list_funcs_all, "## List of functions")
    shutil.copy(folder / "README.md", docs_folder / "index.md")
    result_lines.append(f"File README.md is copied.")

    return "\n".join(result_lines)


def generate_markdown_documentation(file_path: Path | str) -> str:
    def get_function_signature(node: ast.FunctionDef) -> str:
        args = []
        defaults = [None] * (len(node.args.args) - len(node.args.defaults)) + node.args.defaults

        for arg, default in zip(node.args.args, defaults):
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            if default:
                arg_str += f" = {ast.unparse(default)}"
            args.append(arg_str)

        if node.args.vararg:
            arg_str = f"*{node.args.vararg.arg}"
            if node.args.vararg.annotation:
                arg_str += f": {ast.unparse(node.args.vararg.annotation)}"
            args.append(arg_str)

        if node.args.kwarg:
            arg_str = f"**{node.args.kwarg.arg}"
            if node.args.kwarg.annotation:
                arg_str += f": {ast.unparse(node.args.kwarg.annotation)}"
            args.append(arg_str)

        args_str = ", ".join(args)
        args_str = args_str.replace("'", '"')
        signature = f"def {node.name}({args_str})"  # Create the function signature
        if node.returns:
            signature += f" -> {ast.unparse(node.returns)}"
        return signature

    def get_class_signature(node: ast.ClassDef) -> str:
        bases = [ast.unparse(base) for base in node.bases]
        bases_str = ", ".join(bases)
        signature = f"class {node.name}"
        if bases_str:
            signature += f"({bases_str})"
        return signature

    def get_node_code(node: ast.AST, source_lines: list[str]) -> str:
        start_line = node.lineno - 1  # AST line numbers start from 1
        end_line = node.end_lineno
        node_lines = source_lines[start_line:end_line]

        # Remove the docstring if it exists
        if (
            isinstance(node.body, list)
            and node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            docstring_node = node.body[0]
            docstring_start = docstring_node.lineno - 1
            docstring_end = docstring_node.end_lineno
            # Calculate the indexes of the lines related to the docstring
            docstring_lines = set(range(docstring_start, docstring_end))
            node_lines = [line for i, line in enumerate(node_lines, start=start_line) if i not in docstring_lines]

        return "".join(node_lines)

    file_path = Path(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()
    source_lines = source.splitlines(keepends=True)
    tree = ast.parse(source)

    markdown_lines = []
    markdown_lines.append(f"# File `{file_path.name}`\n")

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            class_docstring = ast.get_docstring(node)
            class_signature = get_class_signature(node)
            class_code = get_node_code(node, source_lines)
            # Add the class name and its signature
            markdown_lines.append(f"## Class `{class_name}`\n")
            markdown_lines.append("```python")
            markdown_lines.append(f"{class_signature}")
            markdown_lines.append("```\n")
            if class_docstring:
                markdown_lines.append(f"{class_docstring}\n")
            else:
                markdown_lines.append("_No docstring provided._\n")
            # Add the code to the details block
            markdown_lines.append("<details>")
            markdown_lines.append("<summary>Code:</summary>\n")
            markdown_lines.append("```python")
            markdown_lines.append(class_code.strip())
            markdown_lines.append("```\n")
            markdown_lines.append("</details>\n")

            # Process class methods
            for class_node in node.body:
                if isinstance(class_node, ast.FunctionDef):
                    method_name = class_node.name
                    method_docstring = ast.get_docstring(class_node)
                    method_signature = get_function_signature(class_node)
                    method_code = get_node_code(class_node, source_lines)
                    # Add the method name and its signature
                    markdown_lines.append(f"### Method `{method_name}`\n")
                    markdown_lines.append("```python")
                    markdown_lines.append(f"{method_signature}")
                    markdown_lines.append("```\n")
                    if method_docstring:
                        markdown_lines.append(f"{method_docstring}\n")
                    else:
                        markdown_lines.append("_No docstring provided._\n")
                    # Add the code to the details block
                    markdown_lines.append("<details>")
                    markdown_lines.append("<summary>Code:</summary>\n")
                    markdown_lines.append("```python")
                    markdown_lines.append(method_code.strip())
                    markdown_lines.append("```\n")
                    markdown_lines.append("</details>\n")
        elif isinstance(node, ast.FunctionDef):
            # Module level function
            func_name = node.name
            func_docstring = ast.get_docstring(node)
            func_signature = get_function_signature(node)
            func_code = get_node_code(node, source_lines)
            markdown_lines.append(f"## Function `{func_name}`\n")
            markdown_lines.append("```python")
            markdown_lines.append(f"{func_signature}")
            markdown_lines.append("```\n")
            if func_docstring:
                markdown_lines.append(f"{func_docstring}\n")
            else:
                markdown_lines.append("_No docstring provided._\n")
            # Add the code to the details block
            markdown_lines.append("<details>")
            markdown_lines.append("<summary>Code:</summary>\n")
            markdown_lines.append("```python")
            markdown_lines.append(func_code.strip())
            markdown_lines.append("```\n")
            markdown_lines.append("</details>\n")
    # Join all lines
    markdown_doc = "\n".join(markdown_lines)
    return markdown_doc
