import numpy as np
from scipy.optimize import curve_fit
from scipy.ndimage import gaussian_filter
S=np.load('camera/cap004_signal_225us.npy').astype(float)
D=np.load('camera/cap005_dark_225us.npy').astype(float)
print('SHAPE_SIG=',S.shape,'SHAPE_DARK=',D.shape)
MAX=S.max();NSAT=int((S>=4095).sum())
print('MAX_DN=%g'%MAX);print('NSAT=%d'%NSAT);print('MAX_FRAC=%.4f'%(MAX/4095))
dm=D.mean(0);dv=D.var(0,ddof=1)
print('DARK_MEAN=%.3f'%dm.mean());print('DARK_VAR=%.4f'%dv.mean())
X=S-dm
mf=X.mean(0)
H,W=mf.shape
sm=gaussian_filter(mf,20)
w=np.clip(sm,0,None);yy,xx=np.mgrid[:H,:W]
cx=(w*xx).sum()/w.sum();cy=(w*yy).sum()/w.sum()
print('CENTROID_X=%.1f CENTROID_Y=%.1f'%(cx,cy))
N=128
x0=int(np.clip(round(cx-N/2),0,W-N));y0=int(np.clip(round(cy-N/2),0,H-N))
print('ROI_X0=%d'%x0);print('ROI_Y0=%d'%y0);print('ROI_N=%d'%N)
r=(slice(y0,y0+N),slice(x0,x0+N))
print('SAT_IN_ROI=%d'%int((S[:,r[0],r[1]]>=4095).sum()))
sr=gaussian_filter(mf,8)[r]
c=sr[N//2-8:N//2+8,N//2-8:N//2+8].mean()
ed=np.mean([sr[:8].mean(),sr[-8:].mean(),sr[:,:8].mean(),sr[:,-8:].mean()])
env=abs(c-ed)/c
print('ENVELOPE_VAR=%.3f'%env)
R=X[:,r[0],r[1]].copy()
if env>0.10:
    env_s=gaussian_filter(mf,25)[r];R=R/env_s*env_s.mean();print('ENVELOPE_FLATTENED=yes')
else:print('ENVELOPE_FLATTENED=no')
C=R.std((1,2))/R.mean((1,2))
print('CONTRAST_MEAN=%.4f'%C.mean());print('CONTRAST_STD=%.4f'%C.std(ddof=1))
# photon transfer
sv=S.var(0,ddof=1)-dv.mean(); mm=X.mean(0)
msk=(mm>5)&(mm<2000)
sl=np.polyfit(mm[msk],sv[msk],1)
print('PTC_SLOPE=%.4f'%sl[0])
K=1/sl[0] if sl[0]>0 else np.nan
print('K_EST=%.4f'%K)
# note: speckle changes between frames? check
vd=dv.mean()
for f in [0]:pass
m=R.mean((1,2));v=R.var((1,2))
if np.isfinite(K) and sl[0]>0:
    cc=np.sqrt(np.clip(v-vd-m*sl[0],0,None))/m
    print('CONTRAST_CORR=%.4f'%cc.mean())
else:print('CONTRAST_CORR=not applied')
def ac(a):
    a=a-a.mean();n=a.shape[0]
    F=np.fft.fft2(a,s=(2*n,2*n));p=np.fft.ifft2(np.abs(F)**2).real
    cnt=np.fft.ifft2(np.abs(np.fft.fft2(np.ones((n,n)),s=(2*n,2*n)))**2).real
    p=p/cnt;return p/ p[0,0]
g=lambda l,A,s:A*np.exp(-l**2/(2*s**2))
def fw(l,y):
    m=l>=1
    try:
        p,_=curve_fit(g,l[m],y[m],p0=[0.5,1.5]);return 2*np.sqrt(2*np.log(2))*abs(p[1])
    except Exception:return np.nan
L=np.arange(0,12.)
def frame_fw(A):
    fx=fw(L,A[0,:12]);fy=fw(L,A[:12,0])
    yy,xx=np.mgrid[:2*N,:2*N];rr=np.hypot(np.minimum(yy,2*N-yy),np.minimum(xx,2*N-xx))
    ri=np.round(rr).astype(int);pr=np.bincount(ri.ravel(),A.ravel())/np.bincount(ri.ravel())
    return fx,fy,fw(L,pr[:12])
As=[ac(f) for f in R];Am=np.mean(As,0)
fx,fy,fr=frame_fw(Am)
print('GRAIN_FWHM_X_PX=%.3f'%fx);print('GRAIN_FWHM_Y_PX=%.3f'%fy);print('GRAIN_FWHM_RADIAL_PX=%.3f'%fr)
per=np.array([frame_fw(a)[2] for a in As])
print('GRAIN_STD_PX=%.3f'%np.nanstd(per,ddof=1))
print('ACF_LAG0..4_X=',np.round(Am[0,:5],3))
print('PIXEL_PITCH=unknown')
print('PASS_NO_SAT=',NSAT==0 and MAX/4095<0.8)
print('PASS_C_LE_1=',C.mean()<=1.05)
print('PASS_GRAIN_GT_2PX=',fr>2)
print('PASS_XY_RATIO=',0.8<fx/fy<1.25,'ratio=%.3f'%(fx/fy))
