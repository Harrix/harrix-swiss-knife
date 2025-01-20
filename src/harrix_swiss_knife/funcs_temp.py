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
    ### extract_functions_and_classes__before.py

    | Function/Class | Description |
    |----------------|-------------|
    | Class `Cat (Animal`) | Represents a domestic cat, inheriting from the `Animal` base class. |
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
    output_lines.append(f"### {filename.stem}.py\n")
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
    Generates Markdown documentation for a given Python file.

    Args:
        file_path (str): The path to the Python file.

    Returns:
        str: A Markdown-formatted string documenting the classes, functions,
             and methods in the file along with their docstrings.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()

    tree = ast.parse(source)

    markdown_lines = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            class_docstring = ast.get_docstring(node)
            # Add class name and docstring to markdown
            markdown_lines.append(f"#### Class `{class_name}`\n")
            if class_docstring:
                markdown_lines.append(f"{class_docstring}\n")
            else:
                markdown_lines.append("_No docstring provided._\n")
            # Now, process methods
            for class_node in node.body:
                if isinstance(class_node, ast.FunctionDef):
                    method_name = class_node.name
                    method_docstring = ast.get_docstring(class_node)
                    # Add method name and docstring to markdown
                    markdown_lines.append(f"##### Method `{method_name}`\n")
                    if method_docstring:
                        markdown_lines.append(f"{method_docstring}\n")
                    else:
                        markdown_lines.append("_No docstring provided._\n")
        elif isinstance(node, ast.FunctionDef):
            # Function at module level
            func_name = node.name
            func_docstring = ast.get_docstring(node)
            markdown_lines.append(f"### Function `{func_name}`\n")
            if func_docstring:
                markdown_lines.append(f"{func_docstring}\n")
            else:
                markdown_lines.append("_No docstring provided._\n")
    # Join all lines
    markdown_doc = '\n'.join(markdown_lines)
    return markdown_doc