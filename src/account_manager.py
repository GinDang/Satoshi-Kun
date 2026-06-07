# ============================================================
# account_manager.py  —  reconstructed from Python 3.13 bytecode
# Quản lý phiên license: ping server mỗi 180s để kiểm tra hết hạn,
# tự logout + tắt app khi tài khoản hết hạn; bắt SIGINT/SIGTERM.
# ============================================================
import threading
from datetime import datetime
import sys
import signal
from utils import WEBSITE_URL, notice_and_shutdown
import requests


class AccountStatusManager:
    def __init__(self, username, tool_name, password):
        self.username = username
        self.password = password
        self.tool_name = tool_name
        self.ping_thread = None
        self.stop_ping_event = threading.Event()

    def start_ping_service(self):
        self.stop_ping_event.clear()
        self.ping_thread = threading.Thread(target=self._ping_loop)
        self.ping_thread.daemon = True
        self.ping_thread.start()

    def _ping_loop(self):
        while not self.stop_ping_event.is_set():
            try:
                url = f"{WEBSITE_URL}/api/tool/ping"
                payload = {
                    "username": self.username,
                    "password": self.password,
                    "toolname": self.tool_name,
                    "type": "ping",
                }
                response = requests.post(url, json=payload).json()
                print(response)
                if response["success"] == False:
                    self.update_logout_status()
                    notice_and_shutdown("Th\u00f4ng B\u00e1o!", "T\u00e0i kho\u1ea3n c\u1ee7a b\u1ea1n \u0111\u00e3 h\u1ebft h\u1ea1n")
            except Exception as e:
                self.stop_ping_event.wait(180)
                continue
            self.stop_ping_event.wait(180)

    def stop_ping_service(self):
        self.stop_ping_event.set()
        if self.ping_thread:
            self.ping_thread.join()

    def update_logout_status(self):
        try:
            url = f"{WEBSITE_URL}/api/tool/logout"
            payload = {"username": self.username}
            res = requests.post(url, json=payload).json()
        except Exception as e:
            print(e)


def setup_graceful_shutdown(account_manager):
    def signal_handler(sig, frame):
        print("\nĐang đóng ứng dụng...")
        account_manager.stop_ping_service()
        account_manager.update_logout_status()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
