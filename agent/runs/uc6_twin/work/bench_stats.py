import numpy as np
from scipy.ndimage import uniform_filter
FW=9791.0; RN=6.04
yy,xx=np.mgrid[0:64,0:64]
for n in (4,5,6):
    im=np.load(f"bench/experiment_{n:02d}.npz")["camera_final"].astype(float)
    m=uniform_filter(im,3,mode="constant")
    m[:1]=0;m[-1:]=0;m[:,:1]=0;m[:,-1:]=0
    y,x=np.unravel_index(np.argmax(m),m.shape)
    r=np.hypot(yy-y,xx-x)
    ring=(r>6)&(r<=20)
    full=ring.sum(); tot=np.pi*(20**2-6**2)
    pk=im[y-1:y+2,x-1:x+2].mean(); bg=im[ring].mean(); br=im[ring].max()
    print(f"RUN{n}_focus_xy=({x},{y})")
    print(f"RUN{n}_signal_peak_e={pk:.1f}")
    print(f"RUN{n}_peak_fraction_FW={pk/FW:.3f}")
    print(f"RUN{n}_bg_mean_e={bg:.2f}")
    print(f"RUN{n}_bg_over_readnoise={bg/RN:.2f}")
    print(f"RUN{n}_brightest_ring_px_e={br:.1f}")
    print(f"RUN{n}_brightest_ring_frac_FW={br/FW:.3f}")
    print(f"RUN{n}_ring_px={full}_vs_ideal_area={tot:.0f}_clipped={'YES' if full<0.95*tot else 'NO'}")
for name,v in (("ENH",[28.00,28.50,29.20]),("ENH_farfield",[24.52,21.90,23.53])):
    print(f"{name}_mean={np.mean(v):.3f}")
    print(f"{name}_std_ddof1={np.std(v,ddof=1):.3f}")
print("REALIZATIONS=3 (not 20)")
print("IDEAL_CAMERA_VALUE=not reported by tool")
