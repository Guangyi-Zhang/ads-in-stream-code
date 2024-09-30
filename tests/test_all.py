import pytest
import networkx as nx

from matches.bip import create_dibipartite, \
                        create_random_weighted_dibipartite
from matches.algs import match_by_flow, \
                         match_by_forward_greedy, \
                         match_by_global_greedy, \
                         match_by_online_greedy, \
                         match_by_backward_greedy, \
                         match_by_backward_oblivious_greedy, \
                         match_by_mwm, \
                         revenue, eq


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
        (2, 0, 2),
        (3, 1, 2),
        (2, 1, 3),
    ]

    return edges_with_w


@pytest.fixture
def edges_end_big():
    edges_with_w = [
        (10, 0, 2),
        (11, 1, 2),
        (10, 1, 3),

        (12, 2, 1),
        (13, 3, 1),
        (14, 4, 1),
        (15, 5, 1),
        (16, 6, 1),
        (17, 7, 1),
        (18, 8, 1),
        (19, 9, 1),

        (10, 9, 100),
    ]

    return edges_with_w


@pytest.fixture
def edges_reassign():
    edges_with_w = [
        (4, 0, 3),
        (5, 1, 10),
        (6, 2, 3),
        (5, 3, 1),
    ]

    return edges_with_w


def test_revenue(edges_1vs2):
    q = 0.1
    G = create_dibipartite(edges_1vs2, q)
    M = [
        (2, 0),
    ]

    assert eq(revenue(G, M, q), 2*0.9)

    M = [
        (2, 0),
        (3, 1),
    ]

    assert eq(revenue(G, M, q), 2*0.9 + 2*0.9**3)


def test_backward_oblivious_greedy(edges_end_big, edges_reassign):
    q = 0.1

    G = create_dibipartite(edges_end_big, q)
    M = match_by_backward_oblivious_greedy(G, q)
    R = sum_of_weight(G, M)
    assert R == -100

    M = match_by_backward_greedy(G, q)
    R = sum_of_weight(G, M)
    assert R == -100

    G = create_dibipartite(edges_reassign, q)
    M = match_by_backward_oblivious_greedy(G, q)
    R = sum_of_weight(G, M)
    assert R == -3 * 2 + -10

    M = match_by_backward_greedy(G, q)
    R = sum_of_weight(G, M)
    assert R == -3 * 2 + -10


def test_online_greedy(edges_end_big, G_empty):
    q = 0.1
    G = create_dibipartite(edges_end_big, q)

    M = match_by_online_greedy(G, q, thr=-1)
    R = sum_of_weight(G, M)
    assert R == -4 # M = [(10, 0), (11, 1)]

    M = match_by_online_greedy(G, q, thr=-2)
    R = sum_of_weight(G, M)
    assert R == -3 # M = [(10, 1)] 

    M = match_by_online_greedy(G, q, thr=-3)
    R = sum_of_weight(G, M)
    assert R == -100 # M = [(10, 9)] 



def test_global_greedy(edges_1vs2, edges_end_big, G_empty):
    q = 0.1
    G = create_dibipartite(edges_1vs2, q)
    M = match_by_global_greedy(G, q)
    R = sum_of_weight(G, M)
    assert R == -3

    G = create_dibipartite(edges_end_big, q)
    M = match_by_global_greedy(G, q)
    R = sum_of_weight(G, M)
    assert R == -100


def test_forward_greedy(edges_end_big, G_empty):
    q = 0.1
    G = create_dibipartite(edges_end_big, q)
    M = match_by_forward_greedy(G)
    R = sum_of_weight(G, M)
    assert R == -4 + -8

    M = match_by_forward_greedy(G_empty)


def test_mwm(edges_1vs2):
    q = 0.1

    G = create_dibipartite(edges_1vs2, q)
    M = match_by_mwm(G)
    R = sum_of_weight(G, M)
    assert R == -4

    edges_with_w = [
        (2, 0, 2),
        (3, 1, 2),
        (2, 1, 10),
    ]
    G = create_dibipartite(edges_with_w, q)
    M = match_by_mwm(G)
    R = sum_of_weight(G, M)
    assert R == -10


def test_flow(edges_1vs2, edges_end_big):
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

    q = 0.1
    G = create_dibipartite(edges_end_big, q)
    M = match_by_flow(G, q)
    R = sum_of_weight(G, M)
    assert R == -100
