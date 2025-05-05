import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from collections import defaultdict
from graph_builder import dependencies_digraph


def improved_module_view_digraph(code_root_folder):
    G = dependencies_digraph(code_root_folder)
    file_to_module = {}
    for node in G.nodes:
        parts = node.split('.')
        if len(parts) >= 2 and parts[0] == 'numpy':
            module = 'numpy.' + parts[1]
            file_to_module[node] = module
        else:
            file_to_module[node] = 'numpy.misc'
   
    module_graph = nx.DiGraph()
    modules = set(file_to_module.values())
    module_graph.add_nodes_from(modules)
   
    for source_file, target_file in G.edges:
        source_module = file_to_module[source_file]
        target_module = file_to_module[target_file]
        if source_module != target_module:
            if module_graph.has_edge(source_module, target_module):
                module_graph[source_module][target_module]['weight'] += 1
            else:
                module_graph.add_edge(source_module, target_module, weight=1)
    
    in_degree = dict(module_graph.in_degree(weight='weight'))
    out_degree = dict(module_graph.out_degree(weight='weight'))
    betweenness = nx.betweenness_centrality(module_graph, weight='weight')
    
    filtered_graph = nx.DiGraph()
    filtered_graph.add_nodes_from(module_graph.nodes())
    
    edge_weights = [module_graph[u][v]['weight'] for u, v in module_graph.edges()]
    weight_threshold = np.percentile(edge_weights, 50)  
    
    for u, v, data in module_graph.edges(data=True):
        if data['weight'] > weight_threshold:
            filtered_graph.add_edge(u, v, **data)
    
    print(f"Original graph: {len(module_graph.edges())} edges")
    print(f"Filtered graph: {len(filtered_graph.edges())} edges")
    print(f"Weight threshold: {weight_threshold}")
    
    draw_improved_module_graph(filtered_graph, in_degree, out_degree, betweenness)
    
    draw_dependency_matrix(module_graph)
    
    return filtered_graph

def draw_improved_module_graph(G, in_degree, out_degree, betweenness):
    """Draw a more readable module graph."""
    plt.figure(figsize=(16, 12), dpi=300)
    
    pos = nx.spring_layout(G, k=0.3, iterations=50)  
    
    module_types = defaultdict(list)
    for node in G.nodes():
        module_name = node.split('.')[-1]
        module_types[module_name].append(node)
    
    colormap = plt.cm.tab20
    color_list = list(colormap(np.linspace(0, 1, len(module_types))))
    module_colors = {}
    
    for i, module_type in enumerate(module_types):
        for node in module_types[module_type]:
            module_colors[node] = color_list[i]
    
    node_sizes = []
    for node in G.nodes():
        size = 300 + (in_degree.get(node, 0) * 100) + (betweenness.get(node, 0) * 5000)
        node_sizes.append(size)
    
    edge_weights = [G[u][v]['weight'] * 0.8 for u, v in G.edges()]
    
    nx.draw_networkx_nodes(
        G, pos,
        node_size=node_sizes,
        node_color=[mcolors.rgb2hex(module_colors.get(node, (0.7, 0.7, 0.7))) for node in G.nodes()],
        alpha=0.85
    )
    
    nx.draw_networkx_edges(
        G, pos,
        width=edge_weights,
        alpha=0.6,
        arrows=True,
        arrowsize=15,
        edge_color="dimgray"
    )
    
    labels = {node: node.split('.')[-1] for node in G.nodes()}
    
    for node, (x, y) in pos.items():
        plt.text(
            x, y, labels[node],
            fontsize=10,
            ha='center', va='center',
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.3')
        )
    
    plt.title("NumPy Module Dependencies", fontsize=18)
    plt.axis('off')
    
    plt.figtext(0.01, 0.01, "Node size: Importance | Edge width: Connection strength", 
                fontsize=10, ha='left')
    
    plt.tight_layout()
    plt.savefig("./img/improved_module_dependency_graph.png", dpi=300, bbox_inches='tight')
    plt.close()

def draw_dependency_matrix(G, output_file="./img/module_dependency_matrix.png"):
    """Create a dependency matrix visualization that's great for reports."""
    modules = sorted(list(G.nodes()))
    n = len(modules)
    
    matrix = np.zeros((n, n))
    for i, source in enumerate(modules):
        for j, target in enumerate(modules):
            if G.has_edge(source, target):
                matrix[i, j] = G[source][target]['weight']
    
    fig, ax = plt.subplots(figsize=(12, 10), dpi=300)
    
    cmap = plt.cm.Blues
    im = ax.imshow(matrix, cmap=cmap)
    
    tick_labels = [mod.split('.')[-1] for mod in modules]
    
    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(n))
    ax.set_xticklabels(tick_labels, rotation=45, ha='right', fontsize=8)
    ax.set_yticklabels(tick_labels, fontsize=8)
    
    threshold = np.percentile(matrix[matrix > 0], 75)  
    for i in range(n):
        for j in range(n):
            if matrix[i, j] > threshold:
                ax.text(j, i, int(matrix[i, j]),
                        ha="center", va="center", 
                        color="white" if matrix[i, j] > np.max(matrix)/2 else "black",
                        fontsize=7)
    
    cbar = fig.colorbar(im)
    cbar.ax.set_ylabel("Number of dependencies", rotation=-90, va="bottom")
    
    plt.title("NumPy Module Dependency Matrix", fontsize=14)
    plt.tight_layout()
    
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()