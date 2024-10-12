import argparse
import random
import json
import logging
import time

from matches.bip import create_random_weighted_dibipartite
from matches.bip import loadAdsData
from matches.algs import match_by_flow, \
                         match_by_flow_plus_greedy, \
                         match_by_forward_greedy, \
                         match_by_global_greedy, \
                         match_by_online_greedy, \
                         match_by_backward_greedy, \
                         match_by_backward_greedy_proxy, \
                         match_by_mwm, \
                         match_less, \
                         revenue


dictFiles = {"criteo": "realData/criteo-ads-bip2.json", "yt":"realData/youtube-ads3.json"}
typFiles = {"criteo": 2, "yt":1} # TODO

def get_weights(G,M):
    weights = []
    for i,j in M: # sorted by j
        weights.append(-G.edges[i,j]['weight'])
    
    return weights

def main(use_logfile=False):
    if use_logfile:
        logging.basicConfig(
            filename='logs/mylog.txt',
            format='[%(asctime)s] [%(levelname)-8s] %(message)s',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S')

    ## Parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--ver', type=int)
    parser.add_argument('-r', '--rep', type=int)
    parser.add_argument('-s', '--seed', type=int)
    parser.add_argument('-m', '--method')
    parser.add_argument('-d', '--dataset')
    parser.add_argument('-q', '--q', type=float)
    parser.add_argument('-k', '--k', type=int)
    parser.add_argument('--thr', type=float) # only for onlinegreedy
    #parser.add_argument('-m', '--method', action='store_true')
    args = parser.parse_args()

    random.seed(args.seed)

    ## Data
    real = False
    if args.dataset.startswith("randombip"):
        items = args.dataset.split('-') # randombip-n1-n2-p
        n1 = int(items[1])
        n2 = int(items[2])
        p = float(items[3])
        typ = float(items[4]) if len(items) > 4 else 0
        G = create_random_weighted_dibipartite(n1, n2, args.q, p, typ=typ)
    elif args.dataset.startswith("realData"):
        items = args.dataset.split('-') # realData-source
        fileName = dictFiles[items[1]]
        print(fileName)
        real = True
        G = loadAdsData(fileName, 0.2, p=1.0, directed=True)
    else:
        raise Exception(f"dataset={args.dataset}")

    print(f"Number of nodes: {G.number_of_nodes()}")
    print(f"Number of edges: {G.number_of_edges()}")

    ## Run
    start_time = time.time()

    m = args.method
    q = args.q
    k = args.k
    if m == "flow":
        M = match_by_flow(G, q, k=k)
    if m == "flowgreedy":
        M = match_by_flow_plus_greedy(G, q)
    elif m == "mwm":
        M = match_by_mwm(G)
    elif m == "forwardgreedy":
        M = match_by_forward_greedy(G, k=k)
    elif m == "greedy":
        M = match_by_global_greedy(G, q, k=k)
    elif m == "onlinegreedy":
        M = match_by_online_greedy(G, q, thr=args.thr)
    elif m == "backwardgreedy":
        M = match_by_backward_greedy(G, q)
    elif m == "backwardgreedyproxy":
        M = match_by_backward_greedy_proxy(G, q)

    if k is not None:
        M = match_less(G, M, q, k)

    runtime = time.time() - start_time
    wedges = get_weights(G,M)
    #print(f"M: {M}")
    #print(f"W: {wedges}")

    ## Log
    log = dict()
    log['ver'] = args.ver
    log['rep'] = args.rep
    log['seed'] = args.seed
    log['method'] = args.method
    log['dataset'] = args.dataset

    log['q'] = args.q
    log['k'] = args.k
    log['thr'] = args.thr
    log['n1'] = len([n for n, d in G.nodes(data=True) if d["bipartite"] == 0])
    log['n2'] = len([n for n, d in G.nodes(data=True) if d["bipartite"] == 1])
    log['nE'] = G.number_of_edges()
    log['matching'] = M
    log['weights'] = wedges

    log['runtime'] = runtime
    log['R'] = revenue(G, M, q)
    log['nmatches'] = len(M)

    logtext = json.dumps(log)
    logging.info(logtext)
    print(logtext)


if __name__ == "__main__":
    main(use_logfile=True)
