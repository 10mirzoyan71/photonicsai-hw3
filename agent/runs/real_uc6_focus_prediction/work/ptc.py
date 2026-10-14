import numpy as np
d='camera/'
def load(n): return np.load(d+n).astype(float)
def stats(a):
    if a.shape[0]<2: return a.mean(),float('nan')
    df=a[1:]-a[:-1]
    return a.mean(), float(np.mean([x.var()/2 for x in df]))
dk=load('cap002_dark_min.npy'); dm,dv=stats(dk)
dl=load('cap003_dark_long.npy'); dlm,dlv=stats(dl)
print('DARK_DN=%.3f'%dm); print('DARK_VAR_DN2=%.4f'%dv); print('DARK_LONG_MEAN_DN=%.3f'%dlm); print('DARK_LONG_VAR_DN2=%.4f'%dlv)
files={3:'cap007_flat_3ms.npy',6:'cap009_flat_6ms.npy',10:'cap006_flat_10ms.npy',20:'cap005_flat_test_20ms.npy',23:'cap008_flat_23ms.npy',100:'cap004_flat_test_100ms.npy'}
res={}
for k,f in files.items():
    m,v=stats(load(f)); res[k]=(m,v); print('FLAT_%dms_MEAN_DN=%.2f VAR_DN2=%.2f'%(k,m,v))
fit=[3,6,10,20]
x=np.array([res[k][0]-dm for k in fit]); y=np.array([res[k][1] for k in fit])
def lin(x,y):
    s,i=np.polyfit(x,y,1); return s,i
s,i=lin(x,y); r2=1-np.sum((y-(s*x+i))**2)/np.sum((y-y.mean())**2)
K=1/s
print('SLOPE=%.5f'%s); print('INTERCEPT=%.3f'%i)
print('BITS=12'); print('K_E_PER_DN=%.4f'%K)
print('READ_NOISE_E=%.3f'%(K*np.sqrt(dv)))
print('READ_NOISE_E_PTC=%.3f'%(K*np.sqrt(max(i,0))))
print('DN_SAT=4093'); print('FULL_WELL_E=%.0f'%(K*(4093-dm))); print('FULL_WELL_ADC_LIMITED=true')
print('PTC_LINEAR_R2=%.5f'%r2); print('N_POINTS_FIT=%d'%len(fit))
sl=lin(x[:2],y[:2])[0]; su=lin(x[2:],y[2:])[0]
print('CHECK_K_LOWER_HALF=%.4f'%(1/sl)); print('CHECK_K_UPPER_HALF=%.4f'%(1/su))
print('NOTE=coarse 4-point PTC, uncontrolled source, no black-level/auto-feature queries')
