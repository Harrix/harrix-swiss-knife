import ast
from pathlib import Path


def extract_functions_and_classes(filename: Path | str, is_add_link_demo: bool = True, domain:str="") -> str:
    """
    Extracts all classes and functions from a Python file and formats them into a markdown list.

    Args:

    - `filename` (Path | str): The path to the Python file to be parsed.
    - `is_add_link_demo` (`bool`): Whether to add a link to the documentation demo. Defaults to `True`.
    - `domain` (`str`): The domain for the documentation link. Defaults to an empty string.

    Returns:

    - `str`: Returns the markdown-formatted list of classes and functions.

    Example output:

    ```markdown
    ### File `extract_functions_and_classes__before.py`

    | Function/Class | Description |
    |----------------|-------------|
    | Class `Cat (Animal)` | Represents a domestic cat, inheriting from the `Animal` base class. |
    | `add` | Adds two integers. |
    | `multiply` | Multiples two integers. |
    ```
    """
    filename = Path(filename)
    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()

    # Parse the code into an Abstract Syntax Tree (AST)
    tree = ast.parse(code, filename)

    functions = []
    classes = []

    # Traverse the AST to collect function and class definitions
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            functions.append(node)
        elif isinstance(node, ast.ClassDef):
            classes.append(node)
        # Skip other node types (imports, variables, etc.)

    # List of entries for the table
    entries = []

    # Process classes
    for class_node in classes:
        # Get the class name
        class_name = class_node.name
        # Get base classes (inheritance)
        base_classes = [ast.unparse(base) if base is not None else "" for base in class_node.bases]
        base_classes_str = ", ".join(base_classes) if base_classes else ""
        # Retrieve docstring and extract the first line (summary)
        docstring = ast.get_docstring(class_node)
        summary = docstring.splitlines()[0] if docstring else ""
        # Format the class entry
        if base_classes_str:
            name = f"Class `{class_name} ({base_classes_str})`"
        else:
            name = f"Class `{class_name}`"
        description = summary
        entries.append((name, description))

    # Process functions
    for func_node in functions:
        func_name = f"`{func_node.name}`"
        # Retrieve docstring and extract the first line (summary)
        docstring = ast.get_docstring(func_node)
        summary = docstring.splitlines()[0] if docstring else ""
        # Format the function entry
        entries.append((func_name, summary))

    # Create Markdown table
    output_lines = []
    output_lines.append(f"### File `{filename.name}`\n")
    if is_add_link_demo:
        link = f"{domain}/docs/{filename.stem}.md"
        output_lines.append(f"Doc: [{filename.stem}.md]({link})\n")
    output_lines.append("| Function/Class | Description |")
    output_lines.append("|----------------|-------------|")

    for name, description in entries:
        output_lines.append(f"| {name} | {description} |")

    # Combine all lines and return the result
    result = "\n".join(output_lines)
    return result


def generate_markdown_documentation(file_path: Path | str) -> str:
    """
    Generates Markdown documentation for a given Python file without YAML.

    Args:
        file_path (str): The path to the Python file.

    Returns:
        str: A Markdown-formatted string documenting the classes, functions,
             and methods in the file along with their docstrings.
    """
    def get_function_signature(node: ast.FunctionDef) -> str:
        args = []
        defaults = [None]*(len(node.args.args)-len(node.args.defaults)) + node.args.defaults

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

        args_str = ', '.join(args)
        signature = f"def {node.name}({args_str})"
        if node.returns:
            signature += f" -> {ast.unparse(node.returns)}"
        return signature

    def get_class_signature(node: ast.ClassDef) -> str:
        bases = [ast.unparse(base) for base in node.bases]
        bases_str = ', '.join(bases)
        signature = f"class {node.name}"
        if bases_str:
            signature += f"({bases_str})"
        return signature

    def get_node_code(node: ast.AST, source_lines: list[str]) -> str:
        start_line = node.lineno - 1  # AST line numbers start from 1
        end_line = node.end_lineno
        node_lines = source_lines[start_line:end_line]

        # Удаляем docstring, если он есть
        if (isinstance(node.body, list) and node.body and
            isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
            docstring_node = node.body[0]
            docstring_start = docstring_node.lineno - 1
            docstring_end = docstring_node.end_lineno
            # Вычисляем индексы строк, относящихся к docstring
            docstring_lines = set(range(docstring_start, docstring_end))
            node_lines = [line for i, line in enumerate(node_lines, start=start_line) if i not in docstring_lines]

        return ''.join(node_lines)

    file_path = Path(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
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
            # Добавляем название класса и его сигнатуру
            markdown_lines.append(f"## Class `{class_name}`\n")
            markdown_lines.append("```python")
            markdown_lines.append(f"{class_signature}")
            markdown_lines.append("```\n")
            if class_docstring:
                markdown_lines.append(f"{class_docstring}\n")
            else:
                markdown_lines.append("_No docstring provided._\n")
            # Добавляем код в блок details
            markdown_lines.append("<details>")
            markdown_lines.append("<summary>Code:</summary>\n")
            markdown_lines.append("```python")
            markdown_lines.append(class_code.strip())
            markdown_lines.append("```\n")
            markdown_lines.append("</details>\n")

            # Обрабатываем методы класса
            for class_node in node.body:
                if isinstance(class_node, ast.FunctionDef):
                    method_name = class_node.name
                    method_docstring = ast.get_docstring(class_node)
                    method_signature = get_function_signature(class_node)
                    method_code = get_node_code(class_node, source_lines)
                    # Добавляем название метода и его сигнатуру
                    markdown_lines.append(f"### Method `{method_name}`\n")
                    markdown_lines.append("```python")
                    markdown_lines.append(f"{method_signature}")
                    markdown_lines.append("```\n")
                    if method_docstring:
                        markdown_lines.append(f"{method_docstring}\n")
                    else:
                        markdown_lines.append("_No docstring provided._\n")
                    # Добавляем код в блок details
                    markdown_lines.append("<details>")
                    markdown_lines.append("<summary>Code:</summary>\n")
                    markdown_lines.append("```python")
                    markdown_lines.append(method_code.strip())
                    markdown_lines.append("```\n")
                    markdown_lines.append("</details>\n")
        elif isinstance(node, ast.FunctionDef):
            # Функция на уровне модуля
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
            # Добавляем код в блок details
            markdown_lines.append("<details>")
            markdown_lines.append("<summary>Code:</summary>\n")
            markdown_lines.append("```python")
            markdown_lines.append(func_code.strip())
            markdown_lines.append("```\n")
            markdown_lines.append("</details>\n")
    # Объединяем все строки
    markdown_doc = '\n'.join(markdown_lines)
    return markdown_doc