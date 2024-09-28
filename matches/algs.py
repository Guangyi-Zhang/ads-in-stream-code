import numpy as np
import networkx as nx
import math


def match_by_flow(G, q):
    h = math.floor(np.log(0.5) / np.log(1-q))

    # add source and target
    V1 = [n for n, d in G.nodes(data=True) if d["bipartite"] == 0]
    V2 = [n for n, d in G.nodes(data=True) if d["bipartite"] == 1]

    G.add_node("s", demand=-h)
    G.add_node("t", demand=h)
    G.add_node("t0")

    for v in V1:
        G.add_edge("s", v, weight=0, capacity=1)

    for v in V2:
        G.add_edge(v, "t0", weight=0, capacity=1)

    G.add_edge("t0", "t", weight=0, capacity=h)

    #flowDict = nx.min_cost_flow(G)
    flowDict = nx.max_flow_min_cost(G, 's', 't')
    # print(f"mincost = {nx.cost_of_flow(G, flowDict)}")

    M = set()
    A = [v for v, flow in flowDict['s'].items() if flow == 1]
    for i in A:
        j = [v for v, flow in flowDict[i].items() if flow == 1][0]
        M.add((i,j))

    return M