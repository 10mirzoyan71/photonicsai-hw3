import json, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def P(n, v): print(f"{n}={v}")

js = json.load(open('camera/cap005_drift_10ms_series.json'))
P('JSON_TYPE', type(js).__name__)
state = {'means': None, 'ts': None}
def from_items(v):
    ks = list(v[0].keys()); P('ITEM_KEYS', ks)
    mk = [k for k in ks if 'mean' in k.lower()]
    tk = [k for k in ks if 'time' in k.lower() or k.lower() in ('t', 't_s', 'ts')]
    if mk and state['means'] is None: state['means'] = np.array([d[mk[0]] for d in v], float)
    if tk and state['ts'] is None: state['ts'] = np.array([d[tk[0]] for d in v], float)
def find(o):
    if isinstance(o, dict):
        P('JSON_KEYS', list(o.keys()))
        for k, v in o.items():
            kl = k.lower()
            if isinstance(v, list) and len(v) > 50 and all(isinstance(x, (int, float)) for x in v):
                if 'mean' in kl and state['means'] is None: state['means'] = np.array(v, float)
                elif ('time' in kl or kl in ('t', 't_s', 'ts')) and state['ts'] is None: state['ts'] = np.array(v, float)
            elif isinstance(v, list) and v and isinstance(v[0], dict): from_items(v)
            elif isinstance(v, dict): find(v)
    elif isinstance(o, list) and o and isinstance(o[0], dict):
        from_items(o)
find(js)
means, ts = state['means'], state['ts']

fr = np.load('camera/cap005_drift_10ms.npy')
P('DRIFT_NPY_SHAPE', fr.shape)
if means is None:
    means = fr.reshape(fr.shape[0], -1).mean(axis=1).astype(float)
    P('MEANS_SOURCE', 'npy')
else:
    P('MEANS_SOURCE', 'json')
n = len(means)
if ts is None or len(ts) != n:
    ts = np.arange(n, dtype=float); P('TIME_SOURCE', 'assumed_1s_grid')
else:
    P('TIME_SOURCE', 'json')
t = ts - ts[0]

dark = np.load('camera/cap005_dark_after.npy').astype(float)
D = dark.mean()
B = means - D
P('N_FRAMES', n)
P('T_SPAN_S', round(t[-1], 3))
P('DARK_AFTER_DN', round(D, 3))
m = B.mean()
P('MEAN_DN', round(m, 3))
A = np.vstack([t, np.ones(n)]).T
(b, a), *_ = np.linalg.lstsq(A, B, rcond=None)
res = B - (a + b * t)
sres = np.sqrt((res**2).sum() / (n - 2))
sb = sres / np.sqrt(((t - t.mean())**2).sum())
P('SLOPE_DN_PER_MIN', round(b * 60, 4))
P('SLOPE_PCT_PER_MIN', round(b * 60 / m * 100, 4))
P('SLOPE_UNCERT_PCT_PER_MIN', round(sb * 60 / m * 100, 4))
P('TOTAL_CHANGE_PCT', round(b * 120 / m * 100, 4))
P('FIRST_TO_LAST_PCT', round((B[-1] - B[0]) / B[0] * 100, 4))
P('PEAK_TO_PEAK_PCT', round((B.max() - B.min()) / m * 100, 4))
P('STD_OVER_MEAN_PCT', round(B.std(ddof=1) / m * 100, 4))
P('RESIDUAL_STD_PCT', round(sres / m * 100, 4))
P('DRIFT_SIGNIFICANT', bool(abs(b) > 3 * sb))
P('MEAN_FIRST10_DN', round(B[:10].mean(), 3))
P('MEAN_LAST10_DN', round(B[-10:].mean(), 3))
d = np.diff(B)
P('FRACTION_NEGATIVE_STEPS', round((d < 0).mean(), 3))
c2 = np.polyfit(t, B, 2); res2 = B - np.polyval(c2, t)
P('QUAD_RESIDUAL_STD_PCT', round(res2.std(ddof=3) / m * 100, 4))
P('QUAD_COEF_DN_PER_S2', f'{c2[0]:.4e}')
sm = np.convolve(B, np.ones(10) / 10, mode='valid')
P('SMOOTH10_FRACTION_NEGATIVE_STEPS', round((np.diff(sm) < 0).mean(), 3))
for i, s in enumerate(np.array_split(B, 3)):
    P(f'THIRD{i+1}_MEAN_DN', round(s.mean(), 3))
best = None
for j in range(5, n - 5):
    r = np.concatenate([B[:j] - B[:j].mean(), B[j:] - B[j:].mean()])
    s = (r**2).sum()
    if best is None or s < best[0]: best = (s, j)
P('STEP_FIT_RESIDUAL_STD_PCT', round(np.sqrt(best[0] / (n - 2)) / m * 100, 4))
P('STEP_FIT_INDEX', best[1])
dt = np.median(np.diff(t))
F = np.abs(np.fft.rfft(res - res.mean()))
fq = np.fft.rfftfreq(n, dt)
i = 1 + np.argmax(F[1:])
P('FFT_PEAK_FREQ_HZ', round(fq[i], 4))
P('FFT_PEAK_PERIOD_S', round(1 / fq[i], 3))
P('FFT_PEAK_AMP_RATIO_TO_MEDIAN', round(F[i] / np.median(F[1:]), 2))
P('FFT_NYQUIST_HZ', round(fq[-1], 4))
fig, ax = plt.subplots(2, 1, figsize=(8, 6))
ax[0].plot(t, B, '.-'); ax[0].plot(t, a + b * t); ax[0].set_ylabel('B DN')
ax[1].plot(t, res); ax[1].set_ylabel('residual DN'); ax[1].set_xlabel('s')
fig.savefig('drift.png', dpi=100)

for name, f in [('5', 'cap003_scan_5ms'), ('10', 'cap004_scan_10ms'), ('10_baseline', 'cap001_baseline_10ms'), ('15', 'cap002_scan_15ms')]:
    s = np.load(f'camera/{f}.npy').astype(float)
    bm = s.reshape(s.shape[0], -1).mean(axis=1)
    P(f'FLICKER_NFRAMES_{name}ms', len(bm))
    P(f'FLICKER_MEAN_DN_{name}ms', round(bm.mean(), 3))
    P(f'FLICKER_STD_PCT_{name}ms', round(bm.std(ddof=1) / bm.mean() * 100, 4))
