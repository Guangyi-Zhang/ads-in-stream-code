import pytest
import networkx as nx

from matches.bip import create_random_weighted_dibipartite
from matches.algs import match_by_flow, match_by_forward_greedy


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


@pytest.fixture
def G_end_big():
    n1 = 10
    n2 = 10

    top_nodes = set(range(n1))
    bottom_nodes = set(range(n1, n1 + n2))

    G = nx.DiGraph()
    G.add_nodes_from(top_nodes, bipartite=0)
    G.add_nodes_from(bottom_nodes, bipartite=1)
    
    G.add_edge(0, 10, weight=-2, capacity=1)
    G.add_edge(1, 11, weight=-2, capacity=1)
    G.add_edge(0, 11, weight=-3, capacity=1)

    G.add_edge(2, 12, weight=-1, capacity=1)
    G.add_edge(3, 13, weight=-1, capacity=1)
    G.add_edge(4, 14, weight=-1, capacity=1)
    G.add_edge(5, 15, weight=-1, capacity=1)
    G.add_edge(6, 16, weight=-1, capacity=1)
    G.add_edge(7, 17, weight=-1, capacity=1)
    #G.add_edge(8, 18, weight=-1, capacity=1)

    G.add_edge(0, 19, weight=-100, capacity=1)

    return G


def test_forward_greedy(G_end_big):
    M = match_by_forward_greedy(G_end_big)
    R = 0
    for e in M:
        R = R + G_end_big.edges[e]['weight']

    assert R == -4 + -6


def test_flow(G_1vs2):
    M = match_by_flow(G_1vs2, 0.1)
    R = 0
    for e in M:
        R = R + G_1vs2.edges[e]['weight']

    assert R == -4

