"""Standalone IoT simulator: sends SIMULATED readings to the backend over HTTP, exactly like real hardware (e.g. ESP32) would.

Usage (backend must be running):
    python simulator.py --device 1 --scenario normal
    python simulator.py --device 1 --scenario hypoxia --interval 2
Scenarios: normal, tachycardia, hypoxia, rising_trend, missing, disconnect, fall
All data is synthetic and is never a real measurement.
"""
import argparse
import importlib.util
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

spec = importlib.util.spec_from_file_location("simulation", Path(__file__).resolve().parent.parent / "backend" / "app" / "simulation.py")
sim_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sim_mod)

ap = argparse.ArgumentParser()
ap.add_argument("--api", default="http://localhost:8000")
ap.add_argument("--key", default="dev-device-key", help="DEVICE_API_KEY from backend/.env")
ap.add_argument("--device", type=int, default=1, help="device id (see Devices page)")
ap.add_argument("--scenario", default="normal", choices=sim_mod.SCENARIOS)
ap.add_argument("--interval", type=float, default=2.0)
ap.add_argument("--count", type=int, default=0, help="0 = run until Ctrl+C")
args = ap.parse_args()

sim = sim_mod.PatientSim({"heart_rate": 75, "spo2": 97, "temperature": 36.8, "resp_rate": 16})
sim.set_scenario(args.scenario)
buffer, n = [], 0  # offline buffer: readings are kept if the server is unreachable, then re-sent
print(f"Simulating device {args.device} ({args.scenario}) -> {args.api}   [SYNTHETIC DATA]")
try:
    while args.count == 0 or n < args.count:
        n += 1
        data = sim.next()
        if data is None:
            print("  (device disconnected - sending nothing)")
        else:
            buffer.append({"device_id": args.device, **data})
        while buffer:
            req = urllib.request.Request(args.api + "/api/ingest", data=json.dumps(buffer[0]).encode(),
                                         headers={"Content-Type": "application/json", "X-Device-Key": args.key}, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=5) as r:
                    out = json.loads(r.read())
                print(f"  sent HR={buffer[0]['heart_rate']} SpO2={buffer[0]['spo2']} -> risk={out['risk']} anomaly={out['anomaly']}")
                buffer.pop(0)
            except (urllib.error.URLError, TimeoutError) as e:
                print(f"  server unreachable ({e}); buffering {len(buffer)} reading(s)")
                break
        time.sleep(args.interval)
except KeyboardInterrupt:
    print("stopped")
