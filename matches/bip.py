import networkx as nx
import random
import math


def create_random_weighted_dibipartite(n1, n2, q, p=1.0, weight_range=(1, 10), C=1e5):
    '''
    C is a scale factor to convert and truncate factional weights
    '''

    # Create sets of nodes
    top_nodes = set(range(n2)) # easier if top for j's
    bottom_nodes = set(range(n2, n1 + n2))
    
    # Create the graph
    G = nx.DiGraph()
    G.add_nodes_from(top_nodes, bipartite=1)
    G.add_nodes_from(bottom_nodes, bipartite=0)
    
    # Add edges with random weights
    for j in top_nodes:
        for i in bottom_nodes:
            if random.random() < p:
                #weight = random.uniform(*weight_range)
                weight = random.randint(*weight_range)
                G.add_edge(i, j, weight=-weight, # negative weight!
                                 biased_w=-math.floor(weight * (1-q)**(j+1) * C), 
                                 capacity=1) 
    
    return G


def create_dibipartite(edges_with_w, q, C=1e5):
    '''
    C is a scale factor to convert and truncate factional weights
    '''

    # Create sets of nodes
    top_nodes = set([j for i,j,w in edges_with_w])
    bottom_nodes = set([i for i,j,w in edges_with_w])
    
    # Create the graph
    G = nx.DiGraph()
    G.add_nodes_from(top_nodes, bipartite=1)
    G.add_nodes_from(bottom_nodes, bipartite=0)
    
    # Add edges with random weights
    for i,j,w in edges_with_w:
        G.add_edge(i, j, weight=-w,
                         biased_w=-math.floor(w * (1-q)**(j+1) * C), 
                         capacity=1) 
    
    return G