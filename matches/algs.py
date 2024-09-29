import numpy as np
import networkx as nx
import math
from operator import itemgetter
from heapq import heappush, heappop
import bisect 
from collections import defaultdict
from sortedcontainers import SortedList


##### Utilities #####
def eq(a, b):
    return abs(a-b) < 1e-6


def is_sorted(l):  
    return all(l[i] <= l[i+1] for i in range(len(l) - 1))


def revenue(G, M, q, jth=-1):
    R = 0
    nj = 0
    for i,j in sorted(M, key=itemgetter(1)): # sorted by j
        R = R + -G.edges[i,j]['weight'] * (1-q) ** (j - jth + nj)
        nj = nj + 1
    
    return R


##### Algorithms #####
# Checcklist: negative weight, j starts from 0, remove asserts

def match_by_backward_greedy(G, q):
    pass


def match_by_backward_oblivious_greedy(G, q):
    V1 = [n for n, d in G.nodes(data=True) if d["bipartite"] == 0]
    V2 = [n for n, d in G.nodes(data=True) if d["bipartite"] == 1]
    assert is_sorted(V2)

    M = set()
    R = 0
    lastgain = defaultdict(float)
    lastj = dict()
    j_taken_sorted = SortedList()

    for j in reversed(V2):
        diffj = lambda i: (1-q) ** (lastj[i]-j if i in lastj else 0)
        iw = [(i, -d['weight'] - lastgain[i] * diffj(i)) for i, _, d in G.in_edges(nbunch=j, data=True)]
        if len(iw) == 0:
            continue
        i_star, wg_star = max(iw, key=itemgetter(1))

        if wg_star <= q * R:
            R = (1-q) * R
            continue

        w = -G.edges[i_star, j]['weight']
        M.add((i_star, j))
        lastgain[i_star] = w - q * R
        if i_star in lastj:
            M.remove((i_star, lastj[i_star]))

            nj_smaller = j_taken_sorted.bisect_left(lastj[i_star])
            j_taken_sorted.remove(lastj[i_star])

            offset = -G.edges[i_star, lastj[i_star]]['weight'] * (1-q) ** (lastj[i_star] - j + 1 + nj_smaller)
            R = (1-q) * R + w - offset
            assert(wg_star < w - offset)
            assert(eq(R, revenue(G, M, q, jth=j)))
        else:
            R = (1-q) * R + w
            assert(eq(R, revenue(G, M, q, jth=j)))
        R = (1-q) * R
        lastj[i_star] = j
        j_taken_sorted.add(j) 
    
    return list(M)


def match_by_online_greedy(G, q, thr):
    V1 = [n for n, d in G.nodes(data=True) if d["bipartite"] == 0]
    V2 = [n for n, d in G.nodes(data=True) if d["bipartite"] == 1]
    assert is_sorted(V2)

    M = []
    i_taken = set()
    for j in V2:
        iw = [(i, d['weight']) for i, _, d in G.in_edges(nbunch=j, data=True) if i not in i_taken]
        if len(iw) == 0:
            continue
        i_star, w_star = min(iw, key=itemgetter(1))

        if -w_star * (1-q)**(j+1) < -thr:
            continue

        i_taken.add(i_star)
        M.append((i_star, j))
    
    return M


def match_by_global_greedy(G, q):
    h = []
    for i, j, d in G.edges(data=True):
        heappush(h, (d['biased_w'], (i,j,0)))

    M = []
    i_taken = set()
    j_taken = set()
    j_taken_sorted = []

    # update edge weights in a lazy greedy fashion
    while(len(h) > 0):
        w, (i, j, nj) = heappop(h)

        if j in j_taken or i in i_taken:
            continue

        nj_smaller = bisect.bisect_left(j_taken_sorted, j)
        if nj == nj_smaller:
            M.append((i, j))
            i_taken.add(i)
            j_taken.add(j)
            bisect.insort(j_taken_sorted, j) 
        else:
            w_new = w * (1-q) ** (nj_smaller - nj)
            heappush(h, (w_new, (i,j,nj_smaller)))

    return M


def match_by_forward_greedy(G):
    V1 = [n for n, d in G.nodes(data=True) if d["bipartite"] == 0]
    V2 = [n for n, d in G.nodes(data=True) if d["bipartite"] == 1]
    assert is_sorted(V2)

    M = []
    i_taken = set()
    for j in V2:
        iw = [(i, d['weight']) for i, _, d in G.in_edges(nbunch=j, data=True) if i not in i_taken]
        if len(iw) == 0:
            continue
        i_star, w_star = min(iw, key=itemgetter(1))
        i_taken.add(i_star)
        M.append((i_star, j))
    
    return M


def match_by_flow(G, q):
    h = math.floor(np.log(0.5) / np.log(1-q))

    G = G.copy() # as we need to modify G

    # add source and target
    V1 = [n for n, d in G.nodes(data=True) if d["bipartite"] == 0]
    V2 = [n for n, d in G.nodes(data=True) if d["bipartite"] == 1]

    G.add_node("s", demand=-h)
    G.add_node("t", demand=h)
    G.add_node("t0")

    for v in V1:
        G.add_edge("s", v, weight=0, biased_w=0, capacity=1)

    for v in V2:
        G.add_edge(v, "t0", weight=0, biased_w=0, capacity=1)

    G.add_edge("t0", "t", weight=0, biased_w=0, capacity=h)

    #flowDict = nx.min_cost_flow(G)
    flowDict = nx.max_flow_min_cost(G, 's', 't', weight='biased_w') # doesn't work with fractional weights
    # print(f"mincost = {nx.cost_of_flow(G, flowDict)}")

    M = []
    A = [v for v, flow in flowDict['s'].items() if flow == 1]
    for i in A:
        j = [v for v, flow in flowDict[i].items() if flow == 1][0]
        M.append((i,j))

    return M