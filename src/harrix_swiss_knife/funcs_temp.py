import ast
from pathlib import Path


def extract_functions_and_classes(filename: Path | str) -> str:
    """
    Extracts all classes and functions from a Python file and formats them into a markdown list.

    Args:

    - `filename` (Path | str): The path to the Python file to be parsed.

    Returns:

     - `str`: Returns the markdown-formatted list of classes and functions.

    Example output:

    ```markdown
    ### funcs

    - `class Cat(Animal)`: Represents a domestic cat, inheriting from the `Animal` base class.
    - `def add(a: int, b: int) -> int`: Adds two integers.
    - `def multiply(a: int, b: int) -> int`: Multiples two integers.
    ```
    """
    filename = Path(filename)
    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()

    # Parse the code into an Abstract Syntax Tree (AST)
    tree = ast.parse(code, filename)

    functions = []
    classes = []

    # Traverse the AST and collect function and class definitions
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            functions.append(node)
        elif isinstance(node, ast.ClassDef):
            classes.append(node)
        # Skip other types of nodes (imports, variables, etc.)

    output_lines = []
    output_lines.append(f"### {filename.stem}.py\n")

    # Process classes
    for class_node in classes:
        # Get class name
        class_name = class_node.name
        # Get base classes (inheritance)
        base_classes = [ast.unparse(base) if base is not None else "" for base in class_node.bases]
        base_classes_str = ", ".join(base_classes) if base_classes else ""
        # Get the docstring and extract the first line (summary)
        docstring = ast.get_docstring(class_node)
        summary = docstring.splitlines()[0] if docstring else ""
        # Format the class entry
        if base_classes_str:
            output_lines.append(f"- Class `{class_name}`: {summary}, inheriting from `{base_classes_str}`.")
        else:
            output_lines.append(f"- Class `{class_name}`: {summary}.")

    # Process functions
    for func_node in functions:
        func_name = func_node.name
        # Get the docstring and extract the first line (summary)
        docstring = ast.get_docstring(func_node)
        summary = docstring.splitlines()[0] if docstring else ""
        # Format the function entry
        output_lines.append(f"- `{func_name}`: {summary}")

    # Combine all entries and print the result
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