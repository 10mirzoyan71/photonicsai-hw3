import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
L=lambda n: np.load('camera/'+n).astype(float)
files={'dark':('cap003_dark_20us.npy',20),'f20us':('cap004_flat_20us.npy',20),
'f5':('cap005_flat_5000us.npy',5000),'f20':('cap006_flat_20000us.npy',20000),
'f40':('cap009_flat_40000us.npy',40000),'f60':('cap007_flat_60000us.npy',60000)}
d={k:(L(v[0]),v[1]) for k,v in files.items()}
for k,(a,e) in d.items(): print('SHAPE_'+k+'=',a.shape)
def pv(a):
    n=a.shape[0]//2*2
    return np.mean([np.var(a[i]-a[i+1])/2 for i in range(0,n,2)])-1/12
D=d['dark'][0].mean(); Vd=pv(d['dark'][0])
print('dark_mean_DN=%.3f'%D); print('V_dark_DN2=%.4f'%Vd)
lv=['f20us','f5','f20','f40','f60']
S=np.array([d[k][0].mean()-D for k in lv]); V=np.array([pv(d[k][0]) for k in lv]); E=np.array([d[k][1] for k in lv])
for k,s,v in zip(lv,S,V): print('LEVEL_%s_S=%.2f_V=%.3f'%(k,s,v))
m=np.array([k!='f20us' for k in lv])
Sx=np.r_[0,S[m]]; Vx=np.r_[Vd,V[m]]
p,cov=np.polyfit(Sx,Vx,1,cov=True)
slope,icpt=p; se=np.sqrt(cov[0,0])
K=1/slope; Kse=se/slope**2
print('K_e_per_DN=%.4f'%K); print('K_fit_stderr=%.4f'%Kse)
rn_dn=np.sqrt(Vd); print('read_noise_DN=%.4f'%rn_dn); print('read_noise_e=%.3f'%(K*rn_dn))
print('fit_intercept_DN2=%.4f'%icpt); print('intercept_check_ratio=%.3f'%(icpt/Vd))
p2=np.polyfit(S[m],V[m],1); print('K_nodark_fit=%.4f'%(1/p2[0]))
pl=np.polyfit(S[m][:2],V[m][:2],1); ph=np.polyfit(S[m][2:],V[m][2:],1)
print('K_low_half=%.4f K_high_half=%.4f'%(1/pl[0],1/ph[0]))
sat=4095; print('sat_DN=%d'%sat)
FW=K*(sat-D); print('FW_e=%.0f'%FW)
print('FW_limit=ADC (clipping at 4095 DN; no pixel-well knee observed, true pixel FW >= this)')
c=np.sum(S[m]*E[m])/np.sum(E[m]**2); res=100*np.abs(S[m]-c*E[m])/S[m]
print('lin_residual_max_pct=%.3f'%res.max())
print('bits=12')
ll=np.polyfit(np.log(S[m]),np.log(V[m]),1)[0]; print('loglog_slope=%.3f'%ll)
a,b=d['f60'][0][0],d['f60'][0][1]
print('drift_pct_f60_AB=%.3f'%(100*abs(a.mean()-b.mean())/a.mean()))
print('CHECK_linear_V_vs_S=%s'%('PASS' if abs(ll-1)<0.1 else 'FAIL'))
print('CHECK_intercept_20pct=%s'%('PASS' if abs(icpt/Vd-1)<0.2 else 'FAIL'))
print('CHECK_exposure_linearity_2pct=%s'%('PASS' if res.max()<2 else 'FAIL'))
print('CHECK_dark_unclipped=%s'%('PASS' if D>5*rn_dn else 'FAIL'))
print('CHECK_K_halves_consistent=%s'%('PASS' if abs(pl[0]/ph[0]-1)<0.15 else 'FAIL'))
print('CHECK_ADC_limited_FW=FLAG')
print('NOTE=only 4 unsaturated flat levels (plus 20us near-dark), single dark exposure, no drift recapture')
plt.figure();plt.loglog(S[S>0],V[S>0],'o');x=np.linspace(1,S.max(),50);plt.loglog(x,slope*x+icpt);plt.xlabel('S DN');plt.ylabel('V DN2');plt.savefig('ptc.png')
