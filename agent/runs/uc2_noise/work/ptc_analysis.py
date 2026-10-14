import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
d='camera/'
def ld(n):
    a=np.load(d+n).astype(np.float64)
    if a.ndim==2: a=a[None]
    return a
ds=ld('cap002_dark_short_a.npy'); dl=ld('cap003_dark_long_a.npy')
print('SHAPE_DARK_SHORT=',ds.shape); print('SHAPE_DARK_LONG=',dl.shape)
print('NOTE=frame pairs are consecutive frames within a 16-frame stack; no separate A/B or repeat level')
ms=ds.mean(0); vs=ds.var(0,ddof=1)
ml=dl.mean(0)
hot=(ml-ms)>5
print('N_HOT_PIXELS=',int(hot.sum()))
rn_var=np.median(vs)
diff=ds[1:]-ds[:-1]
pv=np.median((diff**2).mean(0)/2)
print('READ_NOISE_DN_MEDVAR=',np.sqrt(rn_var))
print('READ_NOISE_DN_PAIR=',np.sqrt(pv))
rdn=np.sqrt(rn_var)
print('DARK_MEAN_DN=',ms.mean(),'DARK_MEDIAN_DN=',np.median(ms))
print('DARK_CURRENT_DN_PER_S=',np.median(ml-ms)/0.49998)
S=[];V=[]
for i in range(10):
    a=ld('cap%03d_ptc_L%02d.npy'%(11+i,i+1))
    if i==0: print('SHAPE_PTC=',a.shape)
    m=a.mean(0); v=a.var(0,ddof=1); sig=m-ms
    ok=(a.max(0)<4095)&(~hot)&(m<0.8*4095)
    r=np.zeros_like(ok); r[156:356,220:420]=True
    k=ok&r
    S.append(sig[k].mean()); V.append(v[k].mean())
    x=sig[ok]; y=v[ok]
    pos=x>0.5
    x=x[pos]; y=y[pos]
    if x.size<100: continue
    e=np.logspace(np.log10(0.5),np.log10(x.max()),16)
    idx=np.digitize(x,e)
    for b in range(1,16):
        s=idx==b
        if s.sum()>=50:
            S.append(x[s].mean()); V.append(y[s].mean())
S=np.array(S);V=np.array(V)
sel=np.ones(len(S),bool)
for _ in range(10):
    g,c=np.polyfit(S[sel],V[sel],1)
    res=V-(g*S+c); sd=res[sel].std()
    ns=np.abs(res)<3*sd
    if (ns==sel).all(): break
    sel=ns
res=V[sel]-(g*S[sel]+c)
r2=1-res.var()/V[sel].var()
K=1/g
print('N_POINTS_FIT=',int(sel.sum()),'N_POINTS_TOTAL=',len(S))
print('GAIN_DN_PER_E=',g)
print('K_E_PER_DN=',K)
print('FIT_INTERCEPT_DN2=',c)
print('FIT_R2=',r2)
print('READ_NOISE_DN=',rdn)
print('READ_NOISE_E=',K*rdn)
print('READ_NOISE_E_PTC_INTERCEPT=',K*np.sqrt(c) if c>0 else float('nan'))
plt.loglog(S[S>0],V[S>0],'.');xx=np.linspace(0.5,S.max(),50);plt.plot(xx,g*xx+c)
plt.xlabel('signal DN');plt.ylabel('var DN^2');plt.savefig('ptc.png')
