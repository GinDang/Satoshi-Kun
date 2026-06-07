# ============================================================
# ws_client.py  —  reconstructed from Python 3.13 bytecode
# WebSocket client giữ phiên license: gửi AUTH token, ping mỗi 30s,
# tự reconnect sau 5s nếu rớt kết nối.
# ============================================================
import json
import threading
import time
import websocket


class WSClient:
    def __init__(self, ws_url, token):
        self.ws_url = ws_url
        self.token = token
        self.ws = None
        self.connected = False
        self.stop_flag = False

    def connect(self):
        print(f"[WS] \u0110ang m\u1edf k\u1ebft n\u1ed1i WebSocket: {self.ws_url}...")
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=self.on_open,
            on_close=self.on_close,
            on_error=self.on_error,
            on_message=self.on_message,
        )
        threading.Thread(target=self._run_forever, daemon=True).start()

    def _run_forever(self):
        while not self.stop_flag:
            try:
                self.ws.run_forever()
            except Exception as e:
                print("[WS] L\u1ed7i run_forever:", e)
            print("[WS] \u274c K\u1ebft n\u1ed1i WebSocket b\u1ecb m\u1ea5t, th\u1eed reconnect sau 5s...")
            time.sleep(5)

    def on_open(self, ws):
        self.connected = True
        print("[WS] \u2705 \u0110\u00e3 k\u1ebft n\u1ed1i WebSocket \u2013 g\u1eedi AUTH token")
        auth_payload = {"type": "auth", "token": self.token}
        ws.send(json.dumps(auth_payload))
        threading.Thread(target=self._ping_loop, daemon=True).start()

    def _ping_loop(self):
        while self.connected and not self.stop_flag:
            try:
                time.sleep(30)
                ping_payload = {"type": "ping"}
                self.ws.send(json.dumps(ping_payload))
                print("[WS] G\u1eedi ping th\u00e0nh c\u00f4ng")
            except Exception as e:
                print("[WS] Ping l\u1ed7i:", e)
                return

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
        except Exception:
            data = message
        print("[WS] Message t\u1eeb server:", data)

    def on_close(self, ws, code, reason):
        self.connected = False
        print(f"[WS] \u274c M\u1ea5t k\u1ebft n\u1ed1i WebSocket: code={code}, reason={reason}")

    def on_error(self, ws, error):
        print("[WS] ERROR:", error)

    def disconnect(self):
        self.stop_flag = True
        if self.ws:
            self.ws.close()
        print("[WS] \u0110\u00e3 \u0111\u00f3ng k\u1ebft n\u1ed1i WebSocket")
