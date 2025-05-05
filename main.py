import os
from file_utils import file_path, module_name_from_file_path
from import_parser import imports_from_file
from graph_builder import dependencies_digraph, draw_graph
from config import CODE_ROOT_FOLDER

def main():
    # Verify repository exists
    if not os.path.exists(CODE_ROOT_FOLDER):
        raise FileNotFoundError(f"NumPy repository not found at {CODE_ROOT_FOLDER}")

    print(f"Working directory: {os.getcwd()}")

    # Test file path and module name utilities
    test_file = file_path("numpy/_core/getlimits.py")
    assert module_name_from_file_path(test_file) == "numpy._core.getlimits"
    
    # Test import parsing
    internal_imports = imports_from_file(file_path("numpy/_core/_internal.py"))
    einsumfunc_imports = imports_from_file(file_path("numpy/_core/einsumfunc.py"))
    print(f"Internal imports: {internal_imports}")
    print(f"Einsumfunc imports: {einsumfunc_imports}")
    assert internal_imports != einsumfunc_imports

    # Build and visualize dependency graph
    DG = dependencies_digraph(CODE_ROOT_FOLDER)
    draw_graph(DG, figsize=(40, 40), with_labels=True)
    print("Dependency graph generated and saved as 'dependency_graph.png'.")

if __name__ == "__main__":
    main()