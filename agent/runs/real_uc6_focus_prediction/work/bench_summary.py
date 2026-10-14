import numpy as np
enh=[10.999983536677451,10.845282660853778,10.671304408049242]
std=[0.07003116483424246,0.0741066488392506,0.023916807952985706]
sat=[0,0,0]
B=1500.0;FW=24766.0;rn=5.783
m=np.mean(enh);s=np.std(enh,ddof=1)
peak=m*B
print('BENCH_SIGNAL_B_E=%g'%B)
print('ENH_RUNS=%s'%enh)
print('ENH_STD_WITHIN_RUN=%s'%std)
print('SATURATED_PIXELS_FINAL=%s'%sat)
print('BENCH_PEAK_E_ESTIMATE_ETA_X_B=%.1f'%peak)
print('BENCH_PEAK_FRAC_FW=%.4f'%(peak/FW))
print('ETA_IDEAL=%.2f'%(np.pi/4*63+1))
print('ETA_SIM_MEAN=%.3f'%m)
print('ETA_SIM_STD=%.3f'%s)
print('SATURATION_FLAG=%s'%(any(sat) or peak>FW))
snr=B/np.sqrt(B+rn**2)
print('B_SNR_CHECK=%.2f'%snr)
print('B_SNR_GE_10=%s'%(snr>=10))
