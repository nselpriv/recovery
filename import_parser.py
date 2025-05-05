import ast
import re
from file_utils import file_path

def import_from_line(line):
    """Extract imported module from a single line using regex."""
    try:
        y = re.search(r"^from (\S+)", line)
        if not y:
            y = re.search(r"^import (\S+)", line)
        return y.group(1)
    except:
        return None

def imports_from_file(file):
    """Extract all imported modules from a Python file."""
    all_imports = set()

    try:
        with open(file, 'r', encoding='utf-8') as f:
            source = f.read()

        tree = ast.parse(source, filename=file)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    all_imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    all_imports.add(node.module)

    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"AST parsing failed for {file}: {e}. Falling back to regex.")
        with open(file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for line in lines:
            imp = import_from_line(line)
            if imp:
                all_imports.add(imp)

    return list(all_imports)

if __name__ == "__main__":
    # Test import parsing
    test_file = file_path("numpy/_core/getlimits.py")
    imports = imports_from_file(test_file)
    print(f"Imports from {test_file}: {imports}")