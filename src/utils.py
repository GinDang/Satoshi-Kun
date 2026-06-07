# ============================================================
# utils.py  —  reconstructed from Python 3.13 bytecode
# Hằng số cấu hình, hạ tầng license (MongoDB/Fernet), HWID,
# vị trí IP, giờ chuẩn, hash mật khẩu, hộp thoại + tắt máy.
# ============================================================
import os
import sys
import win32com.client
import requests
import ctypes
import threading
import time
import hashlib
import json
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()

Tool_Name = "gta5vn-3-nghe"
Tool_Version = "1.0.1"

WEBSITE_URL = "https://www.cyphersoft.store"

CURRENT_USER = {"Username": None, "DeviceChangesToday": 0}


def set_current_user(username, device_changes_today):
    CURRENT_USER["Username"] = username
    CURRENT_USER["DeviceChangesToday"] = device_changes_today


def get_current_username():
    return CURRENT_USER["Username"]


def get_current_user_device_changes():
    return CURRENT_USER["DeviceChangesToday"]


def clear_current_user():
    global CURRENT_USER
    CURRENT_USER = {"Username": None, "DeviceChangesToday": 0}


def config_path_AppData(filename):
    base_dir = os.path.join(os.getenv("APPDATA"), "Panda")
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, filename)


def save_login(username, password, remember):
    config_file = config_path_AppData("config.json")
    with open(config_file, "w") as file:
        json.dump({"username": username, "password": password, "remember": remember}, file)


def load_login():
    config_file = config_path_AppData("config.json")
    if not os.path.exists(config_file):
        return ("", "", False)
    try:
        with open(config_file, "r") as file:
            content = file.read().strip()
            if not content:
                return ("", "", False)
            data = json.loads(content)
            return (
                data.get("username", ""),
                data.get("password", ""),
                data.get("remember", False),
            )
    except json.JSONDecodeError:
        return ("", "", False)


def hash_password_sha256(password: str, salt: str = "gtav_autobot") -> str:
    return hashlib.sha256((salt + password).encode()).hexdigest()


def check_password_sha256(password: str, hashed_password: str, salt: str = "gtav_autobot") -> bool:
    return hash_password_sha256(password, salt) == hashed_password


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def get_system_uuid():
    wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    svc = wmi.ConnectServer(".", "root\\cimv2")
    query = "SELECT UUID FROM Win32_ComputerSystemProduct"
    result = svc.ExecQuery(query)
    for item in result:
        return item.UUID


def get_location():
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        data = response.json()
        if data.get("status") == "success":
            city = data.get("city", "Unknown")
            country = data.get("country", "Unknown")
            ip = data.get("query", "Unknown")
            return f"{city}, {country} (IP: {ip})"
        return "Unknown Location"
    except Exception as e:
        print("Location error:", e)
        return "Unknown Location"


def show_message(title, text, style=0, timeout=10):
    MB_TOPMOST = 262144
    MB_SETFOREGROUND = 65536
    ctypes.windll.user32.MessageBoxTimeoutW(
        0, text, title, style | MB_TOPMOST | MB_SETFOREGROUND, 0, timeout * 1000
    )


def force_shutdown():
    try:
        time.sleep(10)
        os._exit(0)
    except Exception as e:
        print(f"Shutdown error: {e}")


def notice_and_shutdown(title, text):
    threading.Thread(target=force_shutdown, daemon=True).start()
    # Lưu ý: bytecode gốc gọi show_message(...) trực tiếp trong target
    threading.Thread(target=show_message(title, text, 16), daemon=True).start()


def get_current_time():
    try:
        response = requests.get(
            "https://timeapi.io/api/Time/current/zone?timeZone=Asia/Ho_Chi_Minh",
            timeout=5,
        )
        if response.status_code == 200:
            data = response.json()
            return datetime.strptime(
                f"{data['year']}-{data['month']:02d}-{data['day']:02d} "
                f"{data['hour']:02d}:{data['minute']:02d}",
                "%Y-%m-%d %H:%M",
            )
        return datetime.now()
    except Exception:
        return datetime.now()
