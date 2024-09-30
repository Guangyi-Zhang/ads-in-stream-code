import networkx as nx
import random
import math


def create_random_weighted_dibipartite(n1, n2, q, p=1.0, weight_range=(1, 10), C=1e5, directed=True, typ=1):
    '''
    C is a scale factor to convert and truncate factional weights

    typ:
    - 0: a fully random bip
    - 1: every ad has a single favorite slot with a large reward

    Every edge has multi attributes:
    - weight: a weight made negative, for compatibility with some optim algs
    - biased_w: a position-biased weight, also negative
    '''

    # Create sets of nodes
    top_nodes = set(range(n2)) # easier if top for j's
    bottom_nodes = set(range(n2, n1 + n2))
    
    # Create the graph
    G = nx.DiGraph() if directed else nx.Graph()
    G.add_nodes_from(top_nodes, bipartite=1)
    G.add_nodes_from(bottom_nodes, bipartite=0)
    
    # Add edges with random weights
    for i in bottom_nodes:
        jt = random.randint(0, n2-1)
        for j in top_nodes:
            if random.random() < p:
                if typ == 0:
                    weight = random.uniform(*weight_range)
                elif typ == 1:
                    weight = weight_range[1] if j == jt else weight_range[0]
                else:
                    raise Exception(f"unknown type={typ}")

                G.add_edge(i, j, weight=-weight, # negative weight!
                                 biased_w=-math.floor(weight * (1-q)**(j+1) * C), 
                                 capacity=1) 
    
    return G


def create_dibipartite(edges_with_w, q, C=1e5, directed=True):
    '''
    C is a scale factor to convert and truncate factional weights
    '''

    # Create sets of nodes
    top_nodes = set([j for i,j,w in edges_with_w])
    bottom_nodes = set([i for i,j,w in edges_with_w])
    
    # Create the graph
    G = nx.DiGraph() if directed else nx.Graph()
    G.add_nodes_from(top_nodes, bipartite=1)
    G.add_nodes_from(bottom_nodes, bipartite=0)
    
    # Add edges with random weights
    for i,j,w in edges_with_w:
        G.add_edge(i, j, weight=-w,
                         biased_w=-math.floor(w * (1-q)**(j+1) * C), 
                         capacity=1) 
    
    return G