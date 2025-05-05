from config import CODE_ROOT_FOLDER

def file_path(file_name):
    """Construct the full file path from a relative file name."""
    return CODE_ROOT_FOLDER + file_name

def module_name_from_file_path(full_path):
    """Convert a file path to a module name (e.g., numpy/_core/getlimits.py -> numpy._core.getlimits)."""
    file_name = full_path[len(CODE_ROOT_FOLDER):]
    file_name = file_name.replace("/__init__.py", "")
    file_name = file_name.replace("/", ".")
    file_name = file_name.replace(".py", "")
    return file_name

if __name__ == "__main__":
    # Test the functions
    test_path = file_path("numpy/_core/getlimits.py")
    assert test_path == "/content/numpy/numpy/_core/getlimits.py"
    assert module_name_from_file_path(test_path) == "numpy._core.getlimits"
    print("File utilities tests passed.")