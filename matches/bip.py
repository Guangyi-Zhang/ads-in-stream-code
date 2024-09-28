import networkx as nx
import random


def create_random_weighted_dibipartite(n1, n2, p=1.0, weight_range=(1, 10)):
    # Create sets of nodes
    top_nodes = set(range(n1))
    bottom_nodes = set(range(n1, n1 + n2))
    
    # Create the graph
    G = nx.DiGraph()
    G.add_nodes_from(top_nodes, bipartite=0)
    G.add_nodes_from(bottom_nodes, bipartite=1)
    
    # Add edges with random weights
    for i in top_nodes:
        for j in bottom_nodes:
            if random.random() < p:
                #weight = random.uniform(*weight_range)
                weight = random.randint(*weight_range)
                G.add_edge(i, j, weight=-weight, capacity=1) # negative weight!
    
    return G