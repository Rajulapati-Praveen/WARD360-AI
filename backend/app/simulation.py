"""Synthetic sensor generator. No app imports so iot/simulator.py can reuse it.
ALL data produced here is SIMULATED - never real measurements."""
import random

SCENARIOS = ["normal", "tachycardia", "hypoxia", "rising_trend", "missing", "disconnect", "fall"]


class PatientSim:
    def __init__(self, baseline: dict, seed=None):
        self.b = baseline
        self.scenario = "normal"
        self.tick = 0
        self.rng = random.Random(seed)
        self.battery = 100.0

    def set_scenario(self, name: str):
        if name not in SCENARIOS:
            raise ValueError(f"unknown scenario {name}")
        self.scenario, self.tick = name, 0

    def next(self):
        """Returns a reading dict, or None when the device is 'disconnected'."""
        self.tick += 1
        t, r, b, s = self.tick, self.rng, self.b, self.scenario
        self.battery = max(5.0, self.battery - 0.02)
        if s == "disconnect":
            return None
        hr = b["heart_rate"] + r.gauss(0, 2)
        spo2 = min(100.0, b["spo2"] + r.gauss(0, 0.4))
        temp = b["temperature"] + r.gauss(0, 0.05)
        rr = b["resp_rate"] + r.gauss(0, 0.7)
        activity, accel, quality = "resting", 1.0 + abs(r.gauss(0, 0.03)), "good"
        if s == "tachycardia":
            hr += min(t * 6, 50); rr += min(t * 0.5, 6)
        elif s == "hypoxia":
            spo2 -= min(t * 1.5, 10); rr += min(t * 0.4, 5); hr += min(t * 2, 15)
        elif s == "rising_trend":
            hr += min(t * 1.0, 30); temp += min(t * 0.05, 1.8)
        elif s == "missing":
            quality = "poor"
            if r.random() < 0.7: hr = None
            if r.random() < 0.7: spo2 = None
            if r.random() < 0.5: temp = None
            if r.random() < 0.5: rr = None
            if all(v is None for v in (hr, spo2, temp, rr)): quality = "missing"
        elif s == "fall":
            if t == 1:
                accel, activity = 3.4, "fall_impact"
            else:
                activity = "lying"
            if t >= 6:
                self.scenario, self.tick = "normal", 0
        rd = lambda v, n: None if v is None else round(v, n)
        return {"heart_rate": rd(hr, 1), "spo2": rd(spo2, 1), "temperature": rd(temp, 2), "resp_rate": rd(rr, 1),
                "activity": activity, "accel_magnitude": round(accel, 2), "quality": quality,
                "battery": int(self.battery)}
