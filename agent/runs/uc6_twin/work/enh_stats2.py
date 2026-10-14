import numpy as np
S={'230':([28.00,28.50,29.20],[24.52,21.90,23.53]),'380':([31.409,32.473,32.259],[21.192,23.210,22.681])}
for k,(e,f) in S.items():
    print(f"ENH{k}_mean={np.mean(e):.3f}")
    print(f"ENH{k}_std={np.std(e,ddof=1):.3f}")
    print(f"FAR{k}_mean={np.mean(f):.3f}")
    print(f"FAR{k}_std={np.std(f,ddof=1):.3f}")
print("REALIZATIONS=3")
