import pytest
import networkx as nx

from matches.bip import create_random_weighted_dibipartite
from matches.algs import match_by_flow


@pytest.fixture
def G_1vs2():
    n1 = 2  
    n2 = 2  

    top_nodes = set(range(n1))
    bottom_nodes = set(range(n1, n1 + n2))

    G = nx.DiGraph()
    G.add_nodes_from(top_nodes, bipartite=0)
    G.add_nodes_from(bottom_nodes, bipartite=1)
    
    G.add_edge(0, 2, weight=-2, capacity=1)
    G.add_edge(1, 3, weight=-2, capacity=1)
    G.add_edge(0, 3, weight=-3, capacity=1)

    return G


def test_flow(G_1vs2):
    M = match_by_flow(G_1vs2, 0.1)
    R = 0
    for e in M:
        R = R + G_1vs2.edges[e]['weight']

    assert R == -4