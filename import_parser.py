import ast
import re
from file_utils import module_name_from_file_path
from pathlib import Path


def import_from_line(line):
    """Extract imported module from a single line using regex."""
    try:
        y = re.search(r"^from (\S+)", line)
        if not y:
            y = re.search(r"^import (\S+)", line)
        return y.group(1)
    except:
        return None
    
def imports_from_file(file: str, code_root_folder: str, excluded_dirs: set[str] | None = None) -> list[str]:

    all_imports = set()
    file_path = Path(file)
    source_module = module_name_from_file_path(str(file_path), code_root_folder, strict=False, excluded_dirs=excluded_dirs)

    if source_module is None:
        return []

    try:
        with open(file, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source, filename=file)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name:
                        all_imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module
                    all_imports.add(module_name)
                elif node.level > 0:
                    parts = source_module.split('.')
                    level = node.level
                    if level <= len(parts):
                        base_module = '.'.join(parts[:-level] or [''])
                        if node.module:
                            relative_module = node.module
                            full_module = f"{base_module}.{relative_module}" if base_module else relative_module
                        else:
                            for name in node.names:
                                if name.name:
                                    full_module = f"{base_module}.{name.name}" if base_module else name.name
                                    all_imports.add(full_module)

    except (SyntaxError, UnicodeDecodeError) as e:
        with open(file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for line in lines:
            imp = import_from_line(line)
            if imp:
                all_imports.add(imp)

    valid_imports = []
    for imp in all_imports:
        possible_path = f"{code_root_folder}/{imp.replace('.', '/')}.py"
        module_name = module_name_from_file_path(possible_path, code_root_folder, strict=False, excluded_dirs=excluded_dirs)
        if module_name:
            valid_imports.append(module_name)
    return valid_imports