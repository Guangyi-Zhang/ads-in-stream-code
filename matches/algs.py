import numpy as np
import networkx as nx
#from scipy.optimize import linear_sum_assignment
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


def match_less(G, M, q, k):
    M = set(M)
    while len(M) > k:
        R = revenue(G, M, q)
        losses = [(R - revenue(G, M.difference({(i,j)}), q), (i,j)) for i,j in M]
        loss, e = min(losses, key=itemgetter(0))
        M.remove(e)

    return list(M)


##### Algorithms #####
# Checcklist: negative weight, j starts from 0, remove asserts

def match_by_backward_greedy(G, q):
    V1 = [n for n, d in G.nodes(data=True) if d["bipartite"] == 0]
    V2 = [n for n, d in G.nodes(data=True) if d["bipartite"] == 1]
    assert is_sorted(V2)

    M = set()
    R = 0
    lastj = dict()

    for j in reversed(V2):

        def gain(i, w):
            if i in lastj:
                M.remove((i, lastj[i]))
                M.add((i,j))
                Ri = revenue(G, M, q, jth=j)
                M.add((i, lastj[i]))
                M.remove((i,j))
                return Ri - R
            else:
                return w - q * R

        iw = [(i, gain(i, -d['weight'])) for i, _, d in G.in_edges(nbunch=j, data=True)]
        if len(iw) == 0:
            continue
        i_star, g_star = max(iw, key=itemgetter(1))

        if g_star <= 0:
            R = (1-q) * R
            continue

        M.add((i_star, j))
        if i_star in lastj:
            M.remove((i_star, lastj[i_star]))
        lastj[i_star] = j

        #print(f"j={j}, R={R + g_star}, rev={revenue(G, M, q, jth=j)}")
        #assert(eq(R + g_star, revenue(G, M, q, jth=j)))
        R = (1-q) * (R + g_star)
    
    return list(M)


def match_by_backward_greedy_proxy(G, q):
    V1 = [n for n, d in G.nodes(data=True) if d["bipartite"] == 0]
    V2 = [n for n, d in G.nodes(data=True) if d["bipartite"] == 1]
    assert is_sorted(V2)

    def update_lastgain(lastgain, M):
        R = 0
        jlast = len(V2) - 1
        for i,j in reversed(sorted(M, key=itemgetter(1))): # sorted by j
            if jlast > j:
                R = R * (1-q) ** (jlast - j)
            w = -G.edges[i,j]['weight']
            lastgain[i] = w - q * R
            R = (1-q) * R + w 
            jlast = j

        return R # missing one (1-q) before the first ad

    M = set()
    R = 0
    lastgain = defaultdict(float)
    lastj = dict()

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

        if i_star in lastj: # re-assign
            M.remove((i_star, lastj[i_star]))
            R = update_lastgain(lastgain, M)
            #print(f"j={j}, R={R}, rev={revenue(G, M, q, jth=j)}")
            #assert(eq(R, revenue(G, M, q, jth=j)))
        else: # assign i_star for the first time
            R = (1-q) * R + w
            lastgain[i_star] = w - q * R
            #assert(eq(R, revenue(G, M, q, jth=j)))
        R = (1-q) * R
        lastj[i_star] = j
    
    return list(M)


def match_by_online_greedy(G, q, thr=None):
    if thr is not None:
        thr = thr if thr < 0 else -thr

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

        if thr is None: # set thr to be the first best 
            thr = w_star
        if -w_star * (1-q)**(j+1) < -thr:
            continue

        i_taken.add(i_star)
        M.append((i_star, j))
    
    return M


def match_by_global_greedy(G, q, M=None, k=None):
    h = []
    for i, j, d in G.edges(data=True):
        heappush(h, (d['weight'] * (1-q)**(j+1), (i,j,0)))

    if M is None:
        M = []
        i_taken = set()
        j_taken = set()
    else:
        i_taken = set([i for i,j in M])
        j_taken = set([j for i,j in M])

    # update edge weights in a lazy greedy fashion
    if k is None:
        k = len(h) # an UB of the matching size limit
    while(len(h) > 0 and len(M) < k):
        w, (i, j, nj) = heappop(h)

        if j in j_taken or i in i_taken:
            continue

        if eq(nj, len(j_taken)): # (i,j) is up-to-date
            if -w > 0: 
                M.append((i, j))
                i_taken.add(i)
                j_taken.add(j)
            # else we discard (i,j)
        else:
            g = revenue(G, M+[(i,j)], q) - revenue(G, M, q)
            heappush(h, (-g, (i,j,len(j_taken))))

    return M


def match_by_forward_greedy(G, k=None):
    V1 = [n for n, d in G.nodes(data=True) if d["bipartite"] == 0]
    V2 = [n for n, d in G.nodes(data=True) if d["bipartite"] == 1]
    assert is_sorted(V2)

    M = []
    i_taken = set()
    for j in V2:
        if k is not None and len(M) > k:
            break

        iw = [(i, d['weight']) for i, _, d in G.in_edges(nbunch=j, data=True) if i not in i_taken]
        if len(iw) == 0:
            continue
        i_star, w_star = min(iw, key=itemgetter(1))
        i_taken.add(i_star)
        M.append((i_star, j))
    
    return M


def match_by_mwm(G):
    '''
    nx.bipartite.minimum_weight_full_matching and linear_sum_assignment in scipy do not work.
    use a general matching instead.
    '''
    edges = [(i,j,-d['biased_w']) for i,j,d in G.edges(data=True)]
    G_ = nx.Graph()
    G_.add_weighted_edges_from(edges) # remake a graph with non-neg weights

    M = nx.max_weight_matching(G_)
    M = [(i,j) if j<i else (j,i) for i,j in M] # re-orient

    #mat = nx.to_numpy_array(G, weight='biased_w')
    #row_ind, col_ind = linear_sum_assignment(mat)
    #print(f"rows={row_ind}, cols={col_ind}, cost = {mat[row_ind, col_ind].sum()}")
    
    #V1 = [n for n, d in G.nodes(data=True) if d["bipartite"] == 0]
    #Mdict = nx.bipartite.minimum_weight_full_matching(G, top_nodes=V1, weight='biased_w')
    #M = [(v, Mdict[v]) for v in V1 if v in Mdict]

    return M


def match_by_flow(G, q, k=None):
    h = math.floor(np.log(0.5) / np.log(1-q))
    if k is not None:
        h = k

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

    # have to try every demand, as the best may not be a max flow
    Mbest, Rbest = [], 0
    for h_ in range(1,h+1):
        try:
            G.nodes["s"]['demand'] = -h_
            G.nodes["t"]['demand'] = h_
            flowDict = nx.min_cost_flow(G, weight='biased_w')

            M = []
            A = [v for v, flow in flowDict['s'].items() if flow == 1]
            for i in A:
                j = [v for v, flow in flowDict[i].items() if flow == 1][0]
                M.append((i,j))

            #print(f"h_={h_}, R={revenue(G,M,q)}, M={M}")
            R = revenue(G,M,q)
            if R > Rbest:
                Rbest = R
                Mbest = M
        except: # can't fulfill demand h_
            pass

    #flowDict = nx.min_cost_flow(G)
    #flowDict = nx.max_flow_min_cost(G, 's', 't', weight='biased_w') # doesn't work with fractional weights
    # print(f"mincost = {nx.cost_of_flow(G, flowDict)}")

    #M = []
    #A = [v for v, flow in flowDict['s'].items() if flow == 1]
    #for i in A:
    #    j = [v for v, flow in flowDict[i].items() if flow == 1][0]
    #    M.append((i,j))

    return Mbest


def match_by_flow_plus_greedy(G, q):
    M = match_by_flow(G, q)
    M = match_by_global_greedy(G, q, M)
    return M
