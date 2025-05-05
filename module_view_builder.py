import networkx as nx
import matplotlib.pyplot as plt
from graph_builder import dependencies_digraph

def module_view_digraph(code_root_folder):
    """Build a directed module-level dependency graph for NumPy, with centrality analysis and visualization."""
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
    
    in_degree_nonzero = {k: v for k, v in in_degree.items() if v > 0}
    out_degree_nonzero = {k: v for k, v in out_degree.items() if v > 0}
    betweenness_nonzero = {k: v for k, v in betweenness.items() if v > 0}
    
    draw_module_graph(module_graph, in_degree_nonzero, out_degree_nonzero, betweenness_nonzero)
    
    return module_graph

def draw_module_graph(G, in_degree, out_degree, betweenness):
    plt.figure(figsize=(20, 20))
    pos = nx.spring_layout(G)
    
    node_sizes = [in_degree.get(node, 0) * 1000 for node in G.nodes()]
    
    max_betweenness = max(betweenness.values(), default=1) or 1
    node_colors = [betweenness.get(node, 1) / max_betweenness for node in G.nodes()]
    
    edge_weights = [G[u][v]['weight'] * 0.5 for u, v in G.edges()]
    
    nx.draw(
        G, pos,
        with_labels=True,
        node_size=node_sizes,
        node_color=node_colors,
        cmap=plt.cm.Reds,
        font_size=10,
        arrows=True,
        edge_color="black",
        width=edge_weights,
        alpha=0.7
    )
    
    plt.savefig("./img/module_dependency_graph.png", dpi=300, bbox_inches='tight')
    plt.close()

