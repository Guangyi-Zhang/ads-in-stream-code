import pytest
import networkx as nx

from matches.bip import create_dibipartite, create_random_weighted_dibipartite
from matches.algs import match_by_flow, match_by_forward_greedy


def sum_of_weight(G, M):
    R = 0
    for e in M:
        R = R + G.edges[e]['weight']

    return R


@pytest.fixture
def G_empty():
    # small p
    return create_random_weighted_dibipartite(10, 10, q=0.1, p=0.1)


@pytest.fixture
def edges_1vs2():
    edges_with_w = [
        (0, 2, 2),
        (1, 3, 2),
        (0, 3, 3),
    ]

    return edges_with_w


@pytest.fixture
def edges_end_big():
    edges_with_w = [
        (0, 10, 2),
        (1, 11, 2),
        (0, 11, 3),

        (2, 12, 1),
        (3, 13, 1),
        (4, 14, 1),
        (5, 15, 1),
        (6, 16, 1),
        (7, 17, 1),
        (8, 18, 1),
        (9, 19, 1),

        (0, 19, 100),
    ]

    return edges_with_w


def test_forward_greedy(edges_end_big, G_empty):
    q = 0.1
    G = create_dibipartite(edges_end_big, q)
    M = match_by_forward_greedy(G)
    R = sum_of_weight(G, M)
    assert R == -4 + -8

    M = match_by_forward_greedy(G_empty)


def test_flow(edges_1vs2):
    q = 0.1
    G = create_dibipartite(edges_1vs2, q)
    M = match_by_flow(G, q)
    R = sum_of_weight(G, M)
    assert R == -4

    q = 0.3 # so h=1
    G = create_dibipartite(edges_1vs2, q)
    M = match_by_flow(G, q)
    R = sum_of_weight(G, M)
    assert R == -3

