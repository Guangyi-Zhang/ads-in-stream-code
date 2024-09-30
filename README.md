# ads-in-stream-code

Prerequisites:
```
pip install numpy networkx pytest sortedcontainers
```

To run experiments, run
```
bash run.sh
```

To run tests, run
```
py.test
```

Note that, the input bipartitie has node indexs starting with 0, and it starts indexing the slots side first.
E.g., given 2 slots `{j}` and 2 ads `{i}`, their indexs are `j=0,1` and `i=2,3`.

## Datasets

See `matches/bip.py`.
Different types of bipartites can be generated, by setting `typ` to a different number.



