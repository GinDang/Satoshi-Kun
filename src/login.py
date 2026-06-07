# ============================================================
# login.py  —  reconstructed from Python 3.13 bytecode
# Màn đăng nhập Qt: gửi username/password + HWID + IP tới
# /api/tool/ping (type=login). Nếu thành công: mở WebSocket giữ
# phiên (wsUrl/wsToken/licenseId), khởi động AccountStatusManager.
# ============================================================
import os
import json
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QCheckBox,
    QSpacerItem, QSizePolicy, QApplication, QHBoxLayout, QPushButton,
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import requests
from ws_client import WSClient
from utils import (
    WEBSITE_URL, get_system_uuid, get_location, Tool_Name, Tool_Version,
    set_current_user, load_login, save_login, get_current_time, resource_path,
)
from account_manager import AccountStatusManager, setup_graceful_shutdown
from PySide6.QtGui import QPixmap


class LoginPage(QWidget):
    def __init__(self, main_app, stacked_widget):
        super().__init__()
        self.now = get_current_time()
        self.main_app = main_app
        self.stacked_widget = stacked_widget
        layout = QVBoxLayout()
        self.setStyleSheet("background-color: #1e1e1e; border-radius: 15px;")

        self.label_title = QLabel("\u0110\u0103ng nh\u1eadp")
        self.label_title.setFont(QFont("Arial", 22, QFont.Bold))
        self.label_title.setStyleSheet("color: #ffffff;")
        self.label_title.setAlignment(Qt.AlignCenter)

        self.username = QLineEdit()
        self.username.setPlaceholderText("T\u00ean \u0111\u0103ng nh\u1eadp")
        self.username.setStyleSheet(self.input_style())

        self.password = QLineEdit()
        self.password.setPlaceholderText("M\u1eadt kh\u1ea9u")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setStyleSheet(self.input_style())

        checkbox_layout = QHBoxLayout()
        self.remember_me = QCheckBox("L\u01b0u m\u1eadt kh\u1ea9u")
        self.remember_me.setStyleSheet("color: white; font-size: 14px;")
        self.show_password = QCheckBox("Hi\u1ec7n m\u1eadt kh\u1ea9u")
        self.show_password.setStyleSheet("color: white; font-size: 14px;")
        self.show_password.stateChanged.connect(self.toggle_password)
        checkbox_layout.addWidget(self.remember_me)
        checkbox_layout.addStretch()
        checkbox_layout.addWidget(self.show_password, alignment=Qt.AlignRight)

        saved_username, saved_password, remember = load_login()
        self.username.setText(saved_username)
        self.password.setText(saved_password)
        self.remember_me.setChecked(remember)

        self.login_button = QPushButton("\u0110\u0103ng nh\u1eadp")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setStyleSheet(
            "background-color: #4CAF50; color: white; font-size: 16px; padding: 10px; border-radius: 5px;"
        )
        self.login_button.clicked.connect(self.handle_login)

        self.discord_contact = QLabel()
        self.discord_contact.setAlignment(Qt.AlignCenter)
        self.discord_contact.setTextFormat(Qt.RichText)
        self.discord_contact.setOpenExternalLinks(False)
        discord_logo_path = resource_path("resources\\discord.png")
        if discord_logo_path:
            pixmap = QPixmap(discord_logo_path)
            pixmap = pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.discord_contact.setPixmap(pixmap)
            self.discord_contact.setText(
                f'<a href="discord"><img src="{discord_logo_path}" width="21" height="21" '
                'style="vertical-align:middle;"> <span style="color:#03A9F4; font-size:16px; '
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

        self.message_label = QLabel("")
        self.message_label.setStyleSheet("color: red; font-size: 14px;")
        self.message_label.setAlignment(Qt.AlignCenter)

        self.website_label = QLabel()
        self.website_label.setTextFormat(Qt.RichText)
        self.website_label.setAlignment(Qt.AlignCenter)
        self.website_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.website_label.setOpenExternalLinks(True)
        self.website_label.setCursor(Qt.PointingHandCursor)
        self.website_label.setText(
            '<html><head><style>a{ text-decoration:none; color:#3498db; font-weight:600; '
            'font-size:14px;}a:hover{ color:#e74c3c; }</style></head><body><p>\u0110\u0103ng k\u00fd s\u1eed d\u1ee5ng '
            '<a href="' + WEBSITE_URL + '">t\u1ea1i \u0111\u00e2y</a></p></body></html>'
        )

        version_layout = QHBoxLayout()
        version_layout.addStretch()
        version_label = QLabel(f"Phi\u00ean b\u1ea3n hi\u1ec7n t\u1ea1i: {Tool_Version}")
        version_label.setStyleSheet("color: #888888; font-size: 10px;")
        version_label.setAlignment(Qt.AlignCenter)
        version_layout.addWidget(version_label)

        spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)

        layout.addWidget(self.label_title)
        layout.addItem(spacer)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addLayout(checkbox_layout)
        layout.addItem(spacer)
        layout.addWidget(self.login_button)
        layout.addWidget(self.discord_contact)
        layout.addWidget(self.message_label)
        layout.addWidget(self.website_label)
        layout.addLayout(version_layout)
        self.setLayout(layout)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.handle_login()

    def toggle_password(self):
        if self.show_password.isChecked():
            self.password.setEchoMode(QLineEdit.Normal)
        else:
            self.password.setEchoMode(QLineEdit.Password)

    def input_style(self):
        return """
        background-color: #2c2f33;
        color: white;
        border-radius: 10px;
        padding: 12px;
        font-size: 16px;
        border: 1px solid #4CAF50;
        """

    def go_to_register(self):
        self.stacked_widget.setCurrentIndex(1)

    def process_tool_data(self, tool_data: str):
        if not tool_data:
            return []
        tool_list = [tool.strip() for tool in tool_data.split(",")]
        return tool_list

    def handle_login(self):
        try:
            print("[LOGIN] B\u1eaft \u0111\u1ea7u \u0111\u0103ng nh\u1eadp...")
            username = self.username.text()
            password = self.password.text()
            remember = self.remember_me.isChecked()
            hwid = get_system_uuid()
            ip = get_location()
            self.login_button.setText("\u0110ang \u0111\u0103ng nh\u1eadp...")
            QApplication.processEvents()
            if not username or not password:
                self.message_label.setText("Vui l\u00f2ng nh\u1eadp t\u00ean \u0111\u0103ng nh\u1eadp!")
                print("[LOGIN] \u274c Thi\u1ebfu username ho\u1eb7c password")
                return
            print("[LOGIN] G\u1eedi request API login...")
            payload = {
                "username": username,
                "password": password,
                "toolname": Tool_Name,
                "hwid": hwid,
                "type": "login",
                "ip": ip,
            }
            response = requests.post(f"{WEBSITE_URL}/api/tool/ping", json=payload).json()
            print("[LOGIN] Ph\u1ea3n h\u1ed3i API:", response)
            if not response.get("success"):
                print("[LOGIN] \u274c Login th\u1ea5t b\u1ea1i:", response.get("message"))
                self.message_label.setText(response.get("message"))
                self.login_button.setText("\u0110\u0103ng nh\u1eadp")
                return
            print("[LOGIN] \u2705 Login th\u00e0nh c\u00f4ng")
            if remember:
                save_login(username, password, True)
            else:
                save_login("", "", False)
            ws_url = response.get("wsUrl")
            ws_token = response.get("wsToken")
            if not ws_token and ws_url and "licenseId=" in ws_url:
                ws_token = ws_url.split("licenseId=")[-1]
            if ws_url:
                print(f"[WS] \u2705 Nh\u1eadn wsUrl t\u1eeb server: {ws_url}")
                self.ws = WSClient(ws_url, ws_token)
                try:
                    self.ws.connect()
                    print("[WS] \u2705 K\u1ebft n\u1ed1i WebSocket th\u00e0nh c\u00f4ng")
                except Exception as e:
                    print("[WS] \u274c L\u1ed7i khi k\u1ebft n\u1ed1i WebSocket:", e)
                    print("[WS] S\u1ebd fallback d\u00f9ng ping API c\u0169")
            else:
                print("[WS] \u274c Kh\u00f4ng c\u00f3 wsUrl, d\u00f9ng ping API c\u0169")
            self.account_manager = AccountStatusManager(username, Tool_Name, password)
            self.main_app.main_page.update_version_info(response)
            self.main_app.main_page.logined = True
            self.account_manager.start_ping_service()
            setup_graceful_shutdown(self.account_manager)
            self.parent().setCurrentIndex(1)
            self.parentWidget().parentWidget().setFixedSize(350, 400)
        except Exception as e:
            print("[LOGIN] L\u1ed7i h\u1ec7 th\u1ed1ng:", e)
            self.message_label.setText("L\u1ed7i h\u1ec7 th\u1ed1ng! Vui l\u00f2ng th\u1eed l\u1ea1i.")
            self.login_button.setText("\u0110\u0103ng nh\u1eadp")
