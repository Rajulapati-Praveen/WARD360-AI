import json


class Manager:
    """WebSocket hub. Each client only receives events for patients it may access."""

    def __init__(self):
        self.clients = []  # (websocket, allowed_ids or None)

    def add(self, ws, allowed):
        self.clients.append((ws, allowed))

    def remove(self, ws):
        self.clients = [c for c in self.clients if c[0] is not ws]

    async def broadcast(self, events):
        for ev in events:
            msg = json.dumps(ev)
            for ws, allowed in list(self.clients):
                if allowed is not None and ev.get("patient_id") not in allowed:
                    continue
                try:
                    await ws.send_text(msg)
                except Exception:
                    self.remove(ws)


manager = Manager()
