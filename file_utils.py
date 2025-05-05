from pathlib import Path
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def module_name_from_file_path(full_path: str, code_root_folder: str, strict: bool = False, excluded_dirs: set[str] | None = None) -> str | None:

    full_path = Path(full_path).resolve()
    code_root_folder = Path(code_root_folder).resolve()

    if not full_path.is_file():
        return None
    if not code_root_folder.is_dir():
        raise ValueError(f"Code root '{code_root_folder}' is not a directory.")

    try:
        relative_path = full_path.relative_to(code_root_folder)
    except ValueError:
        return None

    if excluded_dirs and any(part in excluded_dirs for part in relative_path.parts):
        return None

    is_package_file = False
    parent = full_path.parent
    while parent != code_root_folder and parent != parent.parent:  
        if (parent / "__init__.py").is_file():
            is_package_file = True
            break
        parent = parent.parent

    if not is_package_file and full_path.name != "__init__.py":
        return None

    relative_path_str = str(relative_path)

    if relative_path_str.endswith("/__init__.py"):
        relative_path_str = relative_path_str[:-len("/__init__.py")]

    if not (relative_path_str.endswith(".py") or relative_path.name == "__init__.py"):
        return None

    if relative_path_str.endswith(".py"):
        relative_path_str = relative_path_str[:-3]

    module_name = re.sub(r"[/\\]", ".", relative_path_str).strip(".")

    if not module_name:
        return None

    if not all(part.isidentifier() for part in module_name.split(".")):
        if strict:
            raise ValueError(f"Invalid module name '{module_name}' derived from path '{full_path}'.")
        else:
            return None

    return module_name