# ads-in-stream-code

Prerequisites:
```
pip install numpy networkx pytest sortedcontainers
```

## Usage

All algorithms can be found in `matches/algs.py`.

```python
>>> from matches.algs import match_by_flow, \
...                          match_by_forward_greedy, \
...                          match_by_flow_plus_greedy, \
...                          match_by_global_greedy, \
...                          match_by_online_greedy, \
...                          match_by_backward_greedy, \
...                          match_by_backward_greedy_proxy, \
...                          match_by_mwm, \
...                          revenue
>>> from matches.bip import create_dibipartite
>>> 
>>> # We require the node indexs of a bipartite start with 0, and index the slots side first.
>>> # E.g., given 2 slots `{j}` and 2 ads `{i}`, their indexs are `j=0,1` and `i=2,3`.
>>> edges_with_w = [ 
...     (2, 0, 2), # (ad, slot, weight)
...     (3, 1, 2),
...     (2, 1, 3),
... ]
>>> q = 0.1
>>> G = create_dibipartite(edges_with_w, q)
>>> 
>>> M = match_by_backward_greedy_proxy(G, q)
>>> print(revenue(G, M, q))
2.43
>>> print(M)
[(2, 1)]
>>> 
```

## Implementation details

We require the node indexs of a bipartite start with 0, and 
index the slots side first.
E.g., given 2 slots `{j}` and 2 ads `{i}`, 
their indexs are `j=0,1` and `i=2,3`.

Inside a bipartite `G` returned by `create_dibipartite`,
its edge weights are turned into negative and stored.
Besides, we keep another position-based weight in attribute `biased_w`, 
which is essentially an integer `floor(w * (1-q)**(j+1) * C)` for edge (i,j),
where `C` is a large constant.
These decisions are made to remain compatible with some existing APIs for optimization.
E.g.,

```python
In [6]: G.edges(data=True)
Out[6]: OutEdgeDataView([(2, 0, {'weight': -2, 'biased_w': -180000, 'capacity': 1}), (2, 1, {'weight': -3, 'biased_w': -243000, 'capacity': 1}), (3, 1, {'weight': -2, 'biased_w': -162000, 'capacity': 1})])
```


## Scripts

To run experiments, run
```
bash run.sh
```

To run tests, run
```
py.test -vv -s --doctest-glob="README.md"
# py.test -vv -s -k 'test_case_name'
```

## Datasets

See `matches/bip.py`.
Different types of bipartites can be generated, by setting `typ` to a different number.



