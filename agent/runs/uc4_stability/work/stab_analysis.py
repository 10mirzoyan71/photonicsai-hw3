import json, numpy as np
d = json.load(open('camera/cap006_stab_series.json'))
print('JSON_TYPE=' + type(d).__name__)
if isinstance(d, dict):
    print('JSON_KEYS=' + ','.join(d.keys()))

def find(obj, names):
    if isinstance(obj, dict):
        for k in names:
            if k in obj and isinstance(obj[k], list) and len(obj[k]) > 3 and not isinstance(obj[k][0], (list, dict)):
                return np.array(obj[k], float), k
        for v in obj.values():
            r = find(v, names)
            if r: return r
    return None

if isinstance(d, list) and isinstance(d[0], dict):
    keys = d[0].keys()
    print('ITEM_KEYS=' + ','.join(keys))
    tk = [k for k in keys if 'time' in k.lower() or k in ('t', 't_s')][0]
    mk = [k for k in keys if 'mean' in k.lower()][0]
    t = np.array([x[tk] for x in d], float); m = np.array([x[mk] for x in d], float)
else:
    rt = find(d, ['t_s', 'times_s', 'time_s', 'times', 't', 'timestamps', 'elapsed_s'])
    rm = find(d, ['mean_dn', 'means_dn', 'means', 'mean', 'frame_means', 'mean_dn_per_frame'])
    t, m = rt[0], rm[0]
    print('TIME_KEY=' + rt[1] + ' MEAN_KEY=' + rm[1])
t = t - t[0]
dst = np.load('camera/cap004_dark_start.npy').astype(float)
den = np.load('camera/cap007_dark_end.npy').astype(float)
Ds, De = dst.mean(), den.mean()
print('DARK_START_DN=%.4f' % Ds); print('DARK_END_DN=%.4f' % De); print('DARK_DRIFT_DN=%.4f' % (De - Ds))
D = 0.5 * (Ds + De)
y = m - D
n = len(y)
p, cov = np.polyfit(t, y, 1, cov=True)
b = p[0]; se = np.sqrt(cov[0, 0])
res = y - np.polyval(p, t)
print('N_FRAMES=%d' % n)
print('DURATION_S=%.3f' % (t[-1] - t[0]))
print('MEAN_CORRECTED_DN=%.4f' % y.mean())
print('SLOPE_DN_PER_S=%.6f' % b)
print('SLOPE_SE=%.6f' % se)
print('SLOPE_SIGMA=%.3f' % (abs(b) / se))
print('DRIFT_DN_PER_MIN=%.4f' % (60 * b))
print('DRIFT_PERCENT_PER_MIN=%.4f' % (100 * 60 * b / y.mean()))
print('DRIFT_PERCENT_PER_MIN_SE=%.4f' % (100 * 60 * se / y.mean()))
print('ENDPOINT_CHANGE_PERCENT=%.4f' % (100 * (y[-3:].mean() - y[:3].mean()) / y[:3].mean()))
print('PTP_PERCENT=%.4f' % (100 * (y.max() - y.min()) / y.mean()))
print('STD_DETRENDED_PERCENT=%.4f' % (100 * res.std(ddof=2) / y.mean()))
g = np.diff(t)
r = g.max() / np.median(g)
print('MAX_GAP_OVER_MEDIAN=%.3f' % r)
print('TIMING_OK=%d' % int(r < 2))
for f in ['cap006_stab', 'cap005_light_on']:
    a = np.load('camera/%s.npy' % f)
    print('%s_MAX_DN=%d SATURATED=%d' % (f, a.max(), (a >= 4095).sum()))
    globals()['s_' + f] = (a >= 4095).sum()
print('SATURATION_OK=%d' % int(s_cap006_stab == 0 and s_cap005_light_on == 0))
print('DARK_STABLE_OK=%d' % int(abs(De - Ds) < 0.1 * abs(60 * b) or abs(De - Ds) < 0.05))
