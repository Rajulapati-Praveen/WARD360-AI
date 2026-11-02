"""Anomaly detection: personal-baseline z-scores + Isolation Forest.

model_score is the Isolation Forest decision value (lower = more unusual).
It is a model score, NOT a clinical probability.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

FEATURES = ["heart_rate", "spo2", "temperature", "resp_rate"]
DEFAULT_SD = {"heart_rate": 8.0, "spo2": 1.5, "temperature": 0.3, "resp_rate": 2.5}
LABELS = {"heart_rate": "Heart rate", "spo2": "SpO2", "temperature": "Body temperature", "resp_rate": "Respiratory rate"}
UNITS = {"heart_rate": "bpm", "spo2": "%", "temperature": "C", "resp_rate": "/min"}
MIN_TRAIN = 50
_models: dict = {}


def personal_sds(hist) -> dict:
    """Per-patient spread. Learned from history when enough data, else defaults (bounded)."""
    sds = {}
    for f in FEATURES:
        d = DEFAULT_SD[f]
        s = hist[f].dropna() if hist is not None and len(hist) and f in hist else []
        sds[f] = float(np.clip(np.std(s), 0.5 * d, 1.5 * d)) if len(s) >= 30 else d
    return sds


def zscores(reading: dict, baseline: dict, sds: dict) -> dict:
    return {f: (reading[f] - baseline[f]) / sds[f] for f in FEATURES if reading.get(f) is not None}


def _model(pid, X):
    cached = _models.get(pid)
    if cached is None or cached[0] >= 200:
        m = IsolationForest(n_estimators=100, contamination=0.01, random_state=42).fit(X.values)
        _models[pid] = (0, m)
    n, m = _models[pid]
    _models[pid] = (n + 1, m)
    return m


def detect(reading: dict, hist, baseline: dict, patient_id: int) -> dict:
    sds = personal_sds(hist)
    z = zscores(reading, baseline, sds)
    out = {"is_anomaly": False, "feature": None, "z_scores": z, "model_score": None,
           "iso_flag": False, "stat_flag": False, "sds": sds,
           "explanation": "No valid measurements in this reading.",
           "note": "model_score is an Isolation Forest score, not a clinical probability."}
    if not z:
        return out
    feat = max(z, key=lambda k: abs(z[k]))
    out["feature"] = feat
    out["stat_flag"] = abs(z[feat]) >= 3

    X = hist[FEATURES].dropna() if hist is not None and len(hist) else pd.DataFrame(columns=FEATURES)
    if len(X) >= MIN_TRAIN and all(reading.get(f) is not None for f in FEATURES):
        m = _model(patient_id, X)
        vec = np.array([[reading[f] for f in FEATURES]])
        out["model_score"] = round(float(m.decision_function(vec)[0]), 4)
        out["iso_flag"] = bool(m.predict(vec)[0] == -1)

    # Statistical flag alone, or Isolation Forest flag confirmed by a >=2 SD deviation.
    out["is_anomaly"] = out["stat_flag"] or (out["iso_flag"] and abs(z[feat]) >= 2)
    v, b = reading[feat], baseline[feat]
    text = f"{LABELS[feat]} {v:.1f} {UNITS[feat]} is {z[feat]:+.1f} SD from this patient's personal baseline ({b})."
    if out["iso_flag"]:
        text += " Isolation Forest also rates the combination of measurements as unusual for this patient."
    elif out["is_anomaly"] is False:
        text = "Measurements are within this patient's usual range. " + text
    out["explanation"] = text
    return out
