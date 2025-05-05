import networkx as nx
from pathlib import Path
import matplotlib.pyplot as plt
from file_utils import module_name_from_file_path
from import_parser import imports_from_file


def dependencies_digraph(code_root_folder: str) -> nx.DiGraph:
    files = list(Path(code_root_folder).rglob("*.py"))
    G = nx.DiGraph()
    excluded_dirs = {"_pyinstaller", "tools", "doc", "benchmarks", "ci", "wheels", "swig"}

    valid_modules = set()
    for file in files:
        file_path = str(file)
        module_name = module_name_from_file_path(file_path, code_root_folder, strict=False, excluded_dirs=excluded_dirs)
        if module_name is not None:
            valid_modules.add(module_name)

    for file in files:
        file_path = str(file)
        source_module = module_name_from_file_path(file_path, code_root_folder, strict=False, excluded_dirs=excluded_dirs)
        if source_module is None:
            continue

        G.add_node(source_module)

        for target_module in imports_from_file(file_path, code_root_folder, excluded_dirs=excluded_dirs):
            target_base = target_module.split('.')[0]
            if any(target_module.startswith(vm) or target_base == vm.split('.')[0] for vm in valid_modules):
                G.add_edge(source_module, target_module)

    isolated = list(nx.isolates(G))
    G.remove_nodes_from(isolated)

    draw_graph(G)
    return G
    
def dependencies_digraph_centrality(code_root_folder: str, top_n) -> nx.DiGraph:
   
    files = list(Path(code_root_folder).rglob("*.py"))
    G = nx.DiGraph()
    excluded_dirs = {"_pyinstaller", "tools", "doc", "benchmarks", "ci", "wheels", "swig"}

    valid_modules = set()
    for file in files:
        file_path = str(file)
        module_name = module_name_from_file_path(file_path, code_root_folder, strict=False, excluded_dirs=excluded_dirs)
        if module_name is not None:
            valid_modules.add(module_name)

    for file in files:
        file_path = str(file)
        source_module = module_name_from_file_path(file_path, code_root_folder, strict=False, excluded_dirs=excluded_dirs)
        if source_module is None:
            continue

        G.add_node(source_module)

        for target_module in imports_from_file(file_path, code_root_folder, excluded_dirs=excluded_dirs):
            target_base = target_module.split('.')[0]
            if any(target_module.startswith(vm) or target_base == vm.split('.')[0] for vm in valid_modules):
                G.add_edge(source_module, target_module)

    isolated = list(nx.isolates(G))
    G.remove_nodes_from(isolated)

    in_degree = dict(G.in_degree())
    out_degree = dict(G.out_degree())
    betweenness = nx.betweenness_centrality(G)

    in_degree_nonzero = {k: v for k, v in in_degree.items() if v > 0}
    out_degree_nonzero = {k: v for k, v in out_degree.items() if v > 0}
    betweenness_nonzero = {k: v for k, v in betweenness.items() if v > 0}

    draw_graph_centrality(G, out_degree_nonzero, in_degree_nonzero, betweenness_nonzero, top_n)
    draw_graph_centrality_barplot(out_degree_nonzero, in_degree_nonzero, betweenness_nonzero, top_n)

    return G

def draw_graph(G):
    """Draw and save a graph visualization using matplotlib."""
    plt.figure(figsize=(40,40))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=500, font_size=8)
    plt.savefig("./img/dependency_graph.png")
    plt.close()

def draw_graph_centrality_barplot(out_degree, in_degree, betweenness, top_n=20):
    """Draw and save a bar plot visualization of centrality metrics using matplotlib."""
    in_degree_top = dict(sorted(in_degree.items(), key=lambda x: x[1], reverse=True)[:top_n])
    out_degree_top = dict(sorted(out_degree.items(), key=lambda x: x[1], reverse=True)[:top_n])
    betweenness_top = dict(sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:top_n])
    
    plt.figure(figsize=(15, 15))
    
    plt.subplot(3, 1, 1)
    plt.bar(range(len(in_degree_top)), list(in_degree_top.values()), tick_label=list(in_degree_top.keys()))
    plt.xticks(rotation=45, ha='right', fontsize=8)  
    plt.title("In-Degree Centrality (Modules Imported By Others)")
    
    plt.subplot(3, 1, 2)
    plt.bar(range(len(out_degree_top)), list(out_degree_top.values()), tick_label=list(out_degree_top.keys()))
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.title("Out-Degree Centrality (Modules That Import Others)")
    
    plt.subplot(3, 1, 3)
    plt.bar(range(len(betweenness_top)), list(betweenness_top.values()), tick_label=list(betweenness_top.keys()))
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.title("Betweenness Centrality (Modules as Bridges)")
    
    plt.tight_layout(pad=3.0) 
    plt.savefig("./img/dependency_graph_centrality.png", dpi=300, bbox_inches='tight') 
    plt.close()

def draw_graph_centrality(G,out_degree, in_degree, betweenness, top_n=20):
    """Draw and save a graph visualization using NetworkX with centrality-based styling."""

    top_nodes = sorted(in_degree.items(), key=lambda x: x[1], reverse=True)[:top_n]
    G = G.subgraph([node for node, _ in top_nodes])

    plt.figure(figsize=(40, 40))
    pos = nx.spring_layout(G)
    
    node_sizes = [in_degree.get(node, 0) * 500 for node in G.nodes()]
    
    max_betweenness = max(betweenness.values(), default=1) or 1  
    node_colors = [betweenness.get(node, 0) / max_betweenness for node in G.nodes()]
    
    nx.draw(
        G, pos,
        with_labels=True,
        node_size=node_sizes,
        node_color=node_colors,
        cmap=plt.cm.Blues, 
        font_size=8,
        arrows=True,
        edge_color="gray",
        alpha=0.7
    )
    
    plt.savefig("./img/dependency_graph_emphasized.png")
    plt.close()