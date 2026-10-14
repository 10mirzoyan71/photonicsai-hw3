import numpy as np, glob, os
FW=9791.0; RN=6.04
files=sorted(glob.glob('bench/experiment_*.npz'))[-3:]
print('FILES='+','.join(files))
yy,xx=np.mgrid[0:64,0:64]
for f in files:
    im=np.load(f)['camera_final'].astype(float)
    k=np.ones(3)/3
    m=np.zeros((64,64))
    for y in range(1,63):
        for x in range(1,63):
            m[y,x]=im[y-1:y+2,x-1:x+2].mean()
    fy,fx=np.unravel_index(np.argmax(m),m.shape)
    r=np.hypot(yy-fy,xx-fx)
    ring=(r>6)&(r<=20)
    n=os.path.basename(f)[:-4]
    print(f'{n}_focus_xy=({fx},{fy})')
    print(f'{n}_focus3x3_mean_e={m[fy,fx]:.1f}')
    print(f'{n}_max_pixel_e={im.max():.1f}')
    print(f'{n}_max_frac_FW={im.max()/FW:.3f}')
    print(f'{n}_pixels_ge_FW={int((im>=FW).sum())}')
    print(f'{n}_bg_mean_e={im[ring].mean():.2f}')
    print(f'{n}_bg_over_readnoise={im[ring].mean()/RN:.2f}')
    print(f'{n}_brightest_ring_px_e={im[ring].max():.1f}')
    print(f'{n}_ring_px={int(ring.sum())}')
# tool values must be filled from tool output
import sys
enh=[float(v) for v in sys.argv[1].split(',')] if len(sys.argv)>1 else []
print('REALIZATIONS=3')
print('IDEAL_CAMERA_VALUE=not reported by tool')
