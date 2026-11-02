"""Trend analysis: moving average, direction, abnormal-trend flag and an EXPERIMENTAL linear forecast."""
import numpy as np
import pandas as pd

NOTE = "Forecast is experimental (simple linear extrapolation). It is not a reliable medical prediction."


def _c(v):
    return None if v is None or pd.isna(v) else round(float(v), 3)


def analyse(ts, values, baseline, sd, window=5, horizon=10, fit_n=20) -> dict:
    s = pd.Series(values, dtype="float64")
    ma = s.rolling(window, min_periods=1).mean()
    valid = ~s.isna().values
    x = np.array(ts, dtype=float)[valid]
    y = s.values[valid]
    hist = [{"ts": float(t), "value": _c(v), "ma": _c(m)} for t, v, m in zip(ts, s.values, ma.values)]
    out = {"enough_data": False, "direction": "unknown", "abnormal": False, "history": hist,
           "forecast": [], "note": NOTE, "baseline": baseline}
    if len(y) < 8:
        return out
    y, x = y[-fit_n:], x[-fit_n:]
    xi = np.arange(len(y))
    slope, icpt = np.polyfit(xi, y, 1)
    change = float(slope * (len(y) - 1))
    pred = slope * xi + icpt
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - float(((y - pred) ** 2).sum()) / ss_tot if ss_tot > 0 else 0.0
    direction = "rising" if change >= 0.75 * sd else "falling" if change <= -0.75 * sd else "stable"
    dt = float(np.median(np.diff(x))) if len(x) > 1 else 1.0
    dt = dt if dt > 0 else 1.0
    last_ma = float(ma[valid].iloc[-1])
    out.update({
        "enough_data": True, "direction": direction, "change_over_window": round(change, 3),
        "slope_per_reading": round(float(slope), 4), "r2": round(r2, 3),
        "abnormal": bool(abs(change) >= 1.5 * sd and r2 >= 0.5),
        "last_moving_average": round(last_ma, 3), "baseline_deviation": round(last_ma - baseline, 3),
        "forecast": [{"ts": float(x[-1] + k * dt), "value": round(float(slope * (len(y) - 1 + k) + icpt), 3)}
                     for k in range(1, horizon + 1)],
    })
    return out
