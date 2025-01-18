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
    output_lines.append(f"### {filename.stem}\n")

    # Process classes
    for class_node in classes:
        # Get class name
        class_name = class_node.name
        # Get base classes (inheritance)
        base_classes = [ast.unparse(base) if node is not None else "" for base in class_node.bases]
        base_classes_str = "(" + ", ".join(base_classes) + ")" if base_classes else ""
        # Get the docstring and extract the first line (summary)
        docstring = ast.get_docstring(class_node)
        summary = docstring.splitlines()[0] if docstring else ""
        # Format the class entry
        output_lines.append(f"- `class {class_name}{base_classes_str}`: {summary}")

    # Process functions
    for func_node in functions:
        func_name = func_node.name
        arg_list = []
        # Retrieve function arguments and their annotations
        for arg in func_node.args.args:
            arg_name = arg.arg
            if arg.annotation:
                arg_type = ast.unparse(arg.annotation) if node is not None else ""
                arg_list.append(f"{arg_name}: {arg_type}")
            else:
                arg_list.append(arg_name)
        # Handle *args and **kwargs
        if func_node.args.vararg:
            vararg_name = func_node.args.vararg.arg
            arg_list.append(f"*{vararg_name}")
        if func_node.args.kwarg:
            kwarg_name = func_node.args.kwarg.arg
            arg_list.append(f"**{kwarg_name}")
        # Get return type annotation
        return_type = f" -> {ast.unparse(func_node.returns) if node is not None else ''}" if func_node.returns else ""
        # Get the docstring and extract the first line (summary)
        docstring = ast.get_docstring(func_node)
        summary = docstring.splitlines()[0] if docstring else ""
        # Format the function entry
        arg_str = ", ".join(arg_list)
        output_lines.append(f"- `def {func_name}({arg_str}){return_type}`: {summary}")

    # Combine all entries and print the result
    result = "\n".join(output_lines)
    return result
