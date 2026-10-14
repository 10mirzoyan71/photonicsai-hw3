import numpy as np
d='camera/'
def load(f):
    a=np.load(d+f).astype(float)
    if a.ndim==2: a=a[None]
    return a
def roi(a): return a[:,156:356,220:420]
dark1=roi(load('cap001_dark_1000us.npy')).mean()
dark10=roi(load('cap002_dark_10000us.npy')).mean()
print(f"DARK_1000_MEAN_DN={dark1:.3f}")
print(f"DARK_10000_MEAN_DN={dark10:.3f}")
files=[('cap004_flicker_1000us.npy','1000',dark1),('cap005_flicker_8333us.npy','8333',dark10),
('cap006_flicker_10000us.npy','10000',dark10),('cap007_flicker_20000us.npy','20000',dark10),
('cap008_flicker_30000us.npy','30000',dark10),('cap009_series_30000us.npy','30000_series',dark10)]
res={}
for f,k,dk in files:
    a=roi(load(f)); m=a.mean(axis=(1,2))-dk
    mean=m.mean(); fs=m.std(ddof=1)/mean*100; fpp=(m.max()-m.min())/mean*100
    sat=(a>=4094).mean(); floor=np.sqrt(mean)/mean/np.sqrt(a[0].size)*100
    res[k]=(fs,fpp)
    print(f"EXP_{k}_NFRAMES={len(m)}")
    print(f"EXP_{k}_MEAN_DN={mean:.3f}")
    print(f"EXP_{k}_FSTD_PCT={fs:.4f}")
    print(f"EXP_{k}_FPP_PCT={fpp:.4f}")
    print(f"EXP_{k}_FS_PCT={mean/4095*100:.3f}")
    print(f"EXP_{k}_SATFRAC={sat:.6f}")
    print(f"EXP_{k}_SHOT_FLOOR_PCT={floor:.4f}")
print(f"FLICKER_SHORT_FSTD_PCT={res['1000'][0]:.4f}")
print(f"FLICKER_SHORT_FPP_PCT={res['1000'][1]:.4f}")
print(f"FLICKER_CHOSEN_CAP008_FSTD_PCT={res['30000'][0]:.4f}")
print(f"FLICKER_CHOSEN_CAP008_FPP_PCT={res['30000'][1]:.4f}")
print(f"FLICKER_CHOSEN_CAP009_FSTD_PCT={res['30000_series'][0]:.4f}")
print(f"FLICKER_CHOSEN_CAP009_FPP_PCT={res['30000_series'][1]:.4f}")
print(f"RATIO_FSTD_1000_OVER_30000_CAP008={res['1000'][0]/res['30000'][0]:.3f}")
print(f"RATIO_FSTD_1000_OVER_30000_CAP009={res['1000'][0]/res['30000_series'][0]:.3f}")
