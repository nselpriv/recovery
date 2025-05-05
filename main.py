from graph_builder import dependencies_digraph, dependencies_digraph_centrality
from module_view_builder import module_view_digraph
from churn_metrics import analyze_churn
from module_view_builder2 import improved_module_view_digraph

def main():
    CODE_ROOT_FOLDER = "./content/numpy/"
    dependencies_digraph(CODE_ROOT_FOLDER)
    print("Dependency graph generated and saved as 'dependency_graph.png'.")

    dependencies_digraph_centrality(CODE_ROOT_FOLDER, top_n=25)
    print("Dependency graph with centrality analysis generated and saved as 'dependency_graph_centrality.png'.")

    module_view_digraph(CODE_ROOT_FOLDER)
    print("Module-level dependency graph generated and saved as 'module_dependency_graph.png'.")

    improved_module_view_digraph(CODE_ROOT_FOLDER)
    print("Improved module-level dependency graph generated and saved as .png'.")

    analyze_churn(CODE_ROOT_FOLDER, 25)
    print("Churn analysis completed and saved as 'churn_analysis.png'.")


if __name__ == "__main__":
    main()