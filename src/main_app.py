# ============================================================
# main_app.py  —  reconstructed from Python 3.13 bytecode
# Cửa sổ chính (QMainWindow + QStackedWidget): trang Login + trang
# điều khiển bot. Hotkey toàn cục ↑ bắt đầu / ↓ dừng. Hiển thị
# thời hạn license, kiểm tra phiên bản mới, logout khi đóng.
# ============================================================
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QStackedWidget, QMainWindow,
)
from PySide6.QtGui import QPixmap, QIcon, QAction, QFont
from PySide6.QtCore import Qt, QMetaObject, QEvent, QTimer
from custom_widgets import ModernButton
from utils import (
    WEBSITE_URL, resource_path, Tool_Name, Tool_Version,
    notice_and_shutdown, get_current_time,
)
from tool_module import ToolBot
from datetime import datetime
import tool_module
import keyboard
import requests
import time
import threading
import os

PROCESS_LIST = ["explorer"]


class MainPage(QWidget):
    def __init__(self, tool_bot, count_device_remain, expiration_time):
        super().__init__()
        self.logined = False
        tool_module.comm.update_signal.connect(self.stop_tool)
        self.count_device_remain = count_device_remain
        self.expiration_time = expiration_time
        self.tool_bot = tool_bot
        self.is_tool = False
        self.layout = QVBoxLayout(self)
        self.setStyleSheet("background-color: #121212; color: white;")

        self.logo = QLabel()
        pixmap = QPixmap(resource_path("resources\\logo.png"))
        self.logo.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setAttribute(Qt.WA_TranslucentBackground)
        self.logo.setStyleSheet("background: rgba(0, 0, 0, 0);")

        self.tool_name_label = QLabel("3 Ngh\u1ec1 G\u1ed7/\u0110\u00e1/C\u00f4ng Tr\u01b0\u1eddng")
        self.tool_name_label.setAlignment(Qt.AlignCenter)
        self.tool_name_label.setFont(QFont("Arial", 14, QFont.Medium))
        self.tool_name_label.setAttribute(Qt.WA_TranslucentBackground)

        self.note = QLabel("H\u00e3y t\u1eaft HUD (Shift + L) \u0111\u1ec3 ho\u1ea1t \u0111\u1ed9ng hi\u1ec7u qu\u1ea3")
        self.note.setAlignment(Qt.AlignCenter)
        self.note.setStyleSheet("font-size: 13px; color: white;")
        self.note.setAttribute(Qt.WA_TranslucentBackground)

        self.expiration_label = QLabel("")
        self.expiration_label.setAlignment(Qt.AlignCenter)
        self.expiration_label.setFont(QFont("Segoe UI", 12, QFont.Medium))
        self.expiration_label.setStyleSheet("color: green;")
        self.expiration_label.setAttribute(Qt.WA_TranslucentBackground)

        self.shortcut_label = QLabel("Ph\u00edm t\u1eaft: Nh\u1ea5n \u2191 \u0111\u1ec3 b\u1eaft \u0111\u1ea7u, \u2193 \u0111\u1ec3 d\u1eebng")
        self.shortcut_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.shortcut_label.setStyleSheet("font-size: 12px; color: gray;")
        self.shortcut_label.setAttribute(Qt.WA_TranslucentBackground)

        main_button_layout = QHBoxLayout()
        self.start_button = ModernButton("B\u1eaft \u0111\u1ea7u", "#33383D")
        self.pause_button = ModernButton("T\u1ea1m d\u1eebng", "#33383D")
        main_button_layout.addWidget(self.start_button)
        main_button_layout.addWidget(self.pause_button)

        self.discord_contact = QLabel()
        self.discord_contact.setAlignment(Qt.AlignCenter)
        self.discord_contact.setTextFormat(Qt.RichText)
        self.discord_contact.setOpenExternalLinks(False)
        self.discord_contact.setAttribute(Qt.WA_TranslucentBackground)
        discord_logo_path = resource_path("resources\\discord.png")
        if discord_logo_path:
            pixmap = QPixmap(discord_logo_path)
            pixmap = pixmap.scaled(18, 18, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.discord_contact.setPixmap(pixmap)
            self.discord_contact.setText(
                f'<a href="discord"><img src="{discord_logo_path}" width="18" height="18" '
                'style="vertical-align:middle;"> <span style="color:#03A9F4; font-size:12px; '
                'text-decoration:none;">Discord</span></a>'
            )
        else:
            self.discord_contact.setText(
                '<a href="discord"><span style="color:#03A9F4; font-size:16px; '
                'text-decoration:none;">Discord</span></a>'
            )
        self.discord_contact.linkActivated.connect(
            lambda link: os.startfile("https://discord.gg/6CJTEPaB4s") if link == "discord" else None
        )

        self.website_label = QLabel()
        self.website_label.setTextFormat(Qt.RichText)
        self.website_label.setAlignment(Qt.AlignCenter)
        self.website_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.website_label.setOpenExternalLinks(True)
        self.website_label.setCursor(Qt.PointingHandCursor)
        self.website_label.setText(
            '<html><head><style>a{ text-decoration:none; color:#3498db; font-weight:600; '
            'font-size:13px;}a:hover{ color:#e74c3c; }</style></head><body><a href="'
            + WEBSITE_URL + '">Website qu\u1ea3n l\u00fd</a></body></html>'
        )
        self.website_label.setStyleSheet("QLabel { background: transparent; }")

        self.version_layout = QVBoxLayout()
        self.version_layout.addStretch()
        self.update_notice_label = QLabel()
        self.update_notice_label.setStyleSheet("color: #ff8800; font-size: 12px;")
        self.update_notice_label.setAlignment(Qt.AlignCenter)
        self.update_notice_label.setAttribute(Qt.WA_TranslucentBackground)
        self.update_notice_label.setText("")
        self.version_layout.addWidget(self.update_notice_label)

        self.layout.addWidget(self.logo)
        self.layout.addStretch()
        self.layout.addWidget(self.tool_name_label)
        self.layout.addStretch()
        self.layout.addWidget(self.expiration_label)
        self.layout.addWidget(self.note)
        self.layout.addStretch()
        self.layout.addLayout(main_button_layout)
        self.layout.addWidget(self.shortcut_label)
        self.layout.addStretch()
        self.layout.addWidget(self.discord_contact)
        self.layout.addStretch()
        self.layout.addWidget(self.website_label)
        self.layout.addLayout(self.version_layout)
        self.setLayout(self.layout)

        threading.Thread(target=self.shortcut, daemon=True).start()
        self.pause_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_tool)
        self.pause_button.clicked.connect(self.stop_tool)

    def update_version_info(self, response):
        latest_version = response.get("lastestVersion")
        link_download = response.get("linkDownload")
        print("Latest version from server:", latest_version)
        if latest_version:
            if Tool_Version != latest_version and link_download:
                self.update_notice_label.setText(
                    f'C\u00f3 phi\u00ean b\u1ea3n m\u1edbi! T\u1ea3i file <a href="{link_download}">T\u1ea1i \u0111\u00e2y</a>'
                )
                self.update_notice_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
                self.update_notice_label.setOpenExternalLinks(True)
                return
            self.update_notice_label.setText("")

    def shortcut(self):
        while True:
            if self.logined:
                keyboard.on_press_key("up", lambda _: self.update_ui_safe(self.start_tool))
                keyboard.on_press_key("down", lambda _: self.update_ui_safe(self.stop_tool))
                return
            time.sleep(2)

    def update_ui_safe(self, method):
        QMetaObject.invokeMethod(self, method.__name__, Qt.QueuedConnection)

    # Lưu ý: có 2 định nghĩa stop_tool; bản sau ghi đè (theo bytecode gốc).
    def _stop_tool_simple(self):
        self.start_button.setText("Start")
        self.start_button.setEnabled(True)

    def start_tool(self):
        if not self.is_tool:
            try:
                self.tool_bot.start_tool_thread()
                self.start_button.setText("\u0110ang ch\u1ea1y")
                self.start_button.setStyleSheet("""
                    ModernButton {
                        background-color: #4CAF50;
                        color: white;
                        border-radius: 10px;
                        padding: 12px;
                        font-weight: bold;
                    }
                """)
                self.pause_button.setEnabled(True)
                self.is_tool = True
            except Exception as e:
                print(e)

    def stop_tool(self):
        if self.is_tool:
            try:
                print("stop")
                self.tool_bot.cleanup()
                self.start_button.setText("B\u1eaft \u0111\u1ea7u")
                self.start_button.setStyleSheet("""
                    ModernButton {
                        background-color: #33383D;
                        color: white;
                        border-radius: 10px;
                        padding: 12px;
                    }
                """)
                self.pause_button.setEnabled(False)
                self.is_tool = False
            except Exception as e:
                print(e)


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.username = None
        self.count_device_remain = None
        self.expiration_time = 0
        self.setWindowIcon(QIcon(resource_path("resources\\icon.ico")))
        self.setStyleSheet("background-color: #1e1e1e; color: white; border-radius: 15px;")
        self.setFixedSize(350, 400)
        from login import LoginPage
        self.tool_bot = ToolBot()
        if self.count_device_remain is None:
            self.count_device_remain = 0
        self.stacked_widget = QStackedWidget()
        self.login_page = LoginPage(self, self.stacked_widget)
        self.main_page = MainPage(self.tool_bot, self.count_device_remain, self.expiration_time)
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.main_page)
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.stacked_widget)
        self.setCentralWidget(central_widget)

    def update_username(self, username, password):
        self.username = username
        self.password = password

    def update_device_remain(self, count_device_remain):
        self.count_device_remain = count_device_remain
        self.main_page.update_count_device_remain(count_device_remain)

    def update_expiration_time(self, expiration_time):
        self.expiration_time = expiration_time

        def update_expiration_label():
            try:
                if self.expiration_time == "":
                    self.main_page.expiration_label.setText("Th\u1eddi h\u1ea1n: V\u0129nh vi\u1ec5n")
                    return
                if isinstance(self.expiration_time, str):
                    exp_dt = datetime.strptime(self.expiration_time, "%Y-%m-%d %H:%M")
                elif isinstance(self.expiration_time, datetime):
                    exp_dt = self.expiration_time
                else:
                    raise ValueError("expiration_time is not a valid type")
                now = get_current_time()
                delta = exp_dt - now
                total_minutes = int(delta.total_seconds() // 60)
                if total_minutes <= 0:
                    self.main_page.expiration_label.setText("Th\u1eddi h\u1ea1n: \u0110\u00e3 h\u1ebft h\u1ea1n")
                    notice_and_shutdown("Th\u00f4ng B\u00e1o!", "T\u00e0i kho\u1ea3n c\u1ee7a b\u1ea1n \u0111\u00e3 h\u1ebft h\u1ea1n. Li\u00ean h\u1ec7 admin \u0111\u1ec3 gia h\u1ea1n!")
                    return
                days = total_minutes // 1440
                hours = total_minutes % 1440 // 60
                minutes = total_minutes % 60
                self.main_page.expiration_label.setText(f"Th\u1eddi h\u1ea1n: {days}d {hours}h {minutes}m")
            except Exception as e:
                print("Error updating expiration label: " + str(e))
                self.main_page.expiration_label.setText("Th\u1eddi h\u1ea1n: Kh\u00f4ng x\u00e1c \u0111\u1ecbnh")

        if hasattr(self, "_expiration_timer") and self._expiration_timer is not None:
            self._expiration_timer.stop()
        self._expiration_timer = QTimer(self)
        self._expiration_timer.timeout.connect(update_expiration_label)
        self._expiration_timer.start(60000)
        update_expiration_label()

    def closeEvent(self, event):
        self.send_logout()
        event.accept()

    def send_logout(self):
        if not self.username:
            return
        try:
            url = f"{WEBSITE_URL}/api/tool/logout"
            payload = {"username": self.username}
            res = requests.post(url, json=payload).json()
            print("Logout response:", res)
        except Exception as e:
            print("Logout error:", e)
            print(e)
