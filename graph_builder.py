import networkx as nx
from pathlib import Path
import matplotlib.pyplot as plt
from config import CODE_ROOT_FOLDER
from file_utils import module_name_from_file_path
from import_parser import imports_from_file

def dependencies_graph(code_root_folder):
    """Build an undirected dependency graph for Python files."""
    py_files = Path(code_root_folder).rglob("*.py")
    pyi_files = Path(code_root_folder).rglob("*.pyi")
    files = list(py_files) + list(pyi_files)
    G = nx.Graph()

    for file in files:
        file_path = str(file)
        module_name = module_name_from_file_path(file_path)
        if module_name not in G.nodes:
            G.add_node(module_name)
        for each in imports_from_file(file_path):
            G.add_edge(module_name, each)

    return G

def dependencies_digraph(code_root_folder):
    """Build a directed dependency graph for Python files."""
    py_files = Path(code_root_folder).rglob("*.py")
    pyi_files = Path(code_root_folder).rglob("*.pyi")
    files = list(py_files) + list(pyi_files)
    G = nx.DiGraph()

    for file in files:
        file_path = str(file)
        source_module = module_name_from_file_path(file_path)
        if source_module not in G.nodes:
            G.add_node(source_module)
        for target_module in imports_from_file(file_path):
            G.add_edge(source_module, target_module)

    return G

def draw_graph(G, figsize=(10, 10), with_labels=True):
    """Draw and save a graph visualization using matplotlib."""
    plt.figure(figsize=figsize)
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=with_labels, node_size=500, font_size=8)
    plt.savefig("dependency_graph.png")
    plt.close()

if __name__ == "__main__":
    # Test graph building
    DG = dependencies_digraph(CODE_ROOT_FOLDER)
    print(f"Directed graph created with {DG.number_of_nodes()} nodes and {DG.number_of_edges()} edges.")
    draw_graph(DG, figsize=(10, 10), with_labels=True)