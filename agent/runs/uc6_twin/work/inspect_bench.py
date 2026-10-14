import numpy as np
for i in (4,5,6):
    d=np.load(f"bench/experiment_{i:02d}.npz",allow_pickle=True)
    print(f"EXP{i}_KEYS={list(d.keys())}")
    for k in d.keys():
        a=d[k]
        print(f"EXP{i}_{k}_shape={a.shape}_dtype={a.dtype}", (f"min={a.min():.4g} max={a.max():.4g} mean={a.mean():.4g}" if a.dtype.kind in 'fiu' and a.size else ""))
