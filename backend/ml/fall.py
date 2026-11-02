"""EXPERIMENTAL fall-event detection from simulated accelerometer magnitude (in g)."""
FALL_G = 2.5


def detect(reading: dict):
    a = reading.get("accel_magnitude")
    if a is not None and a >= FALL_G:
        return {"event": "possible_fall", "accel": a, "experimental": True,
                "message": f"Possible fall detected (impact {a:.1f} g). Experimental detection - please check on the patient."}
    return None
