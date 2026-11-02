"""Interpretable risk-assessment engine (rule-based, transparent).

The point values below are DEMO settings based on deviation from each patient's own baseline.
They are NOT medically validated thresholds and this engine does not diagnose any condition.
"""
from .anomaly import FEATURES, LABELS, UNITS

ACTIVE_OK = {"resting", "sleeping", "lying"}
ACTIONS = {
    "normal": "No action needed. Routine observation continues.",
    "warning": "Check on the patient, confirm the sensor is worn correctly and re-check in a few minutes. Contact a healthcare professional if you are concerned.",
    "critical": "Check on the patient now. If they seem unwell, contact a healthcare professional or local emergency services.",
    "unknown": "Check that the device is worn, charged and connected.",
}


def _points(az: float) -> int:
    return 3 if az >= 5 else 2 if az >= 3 else 1 if az >= 2 else 0


def _dev(f, z):
    """Directional deviation: SpO2 only matters when LOW."""
    return max(0.0, -z) if f == "spo2" else abs(z)


def assess(recent: list, baseline: dict, sds: dict) -> dict:
    cur = recent[-1]
    base = {"disclaimer": "Decision support only. Not a diagnosis. Demo scoring, not clinically validated."}
    vals = [cur.get(f) for f in FEATURES]
    if cur.get("quality") == "missing" or all(v is None for v in vals):
        return {**base, "level": "unknown", "score": 0, "confidence": "low", "contributions": [],
                "reasons": ["No valid sensor measurements in the latest reading."], "action": ACTIONS["unknown"]}

    window = recent[-5:]
    completeness = sum(1 for r in window for f in FEATURES if r.get(f) is not None) / (len(window) * len(FEATURES))
    confidence = "high" if completeness >= 0.8 else "medium" if completeness >= 0.5 else "low"

    contribs, score = [], 0
    for f in FEATURES:
        v = cur.get(f)
        if v is None:
            continue
        z = (v - baseline[f]) / sds[f]
        if f in ("heart_rate", "resp_rate") and z > 0 and cur.get("activity") not in ACTIVE_OK:
            continue  # raised HR/RR is expected during activity
        pts = _points(_dev(f, z))
        persist = 0
        for r in window:
            if r.get(f) is None:
                continue
            zi = (r[f] - baseline[f]) / sds[f]
            if _dev(f, zi) >= 2 and (zi > 0) == (z > 0):
                persist += 1
        if pts and persist >= 3:
            pts += 1
        if pts:
            t = f"{LABELS[f]} {v:.1f} {UNITS[f]} ({z:+.1f} SD from baseline {baseline[f]})"
            if persist >= 2:
                t += f"; unusual in {persist} of the last {len(window)} readings"
            contribs.append({"feature": f, "value": v, "baseline": baseline[f], "z": round(z, 2), "points": pts, "text": t})
            score += pts

    level = "critical" if score >= 4 else "warning" if score >= 2 else "normal"
    reasons = [c["text"] for c in contribs] or ["All measurements are close to this patient's personal baseline."]
    if confidence == "low":
        reasons.append("Limited recent data - assessment confidence is low.")
    return {**base, "level": level, "score": score, "confidence": confidence,
            "contributions": contribs, "reasons": reasons, "action": ACTIONS[level]}
