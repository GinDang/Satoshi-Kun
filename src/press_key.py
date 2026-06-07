# ============================================================
# press_key.py  —  reconstructed from Python 3.13 bytecode
# App: gta5vn-3-nghe v1.0.1 (CypherSoft)
# Mô phỏng nhấn phím cấp thấp qua WinAPI keybd_event, có timing
# "giống người" để tránh bị phát hiện là macro.
# ============================================================
import ctypes
import random
import time
from typing import Optional, Tuple

KEYEVENTF_KEYUP = 2

# Bảng mã phím ảo (Virtual-Key Codes) của Windows
VK_CODES = {
    'enter': 13, 'tab': 9, 'esc': 27, 'backspace': 8, 'space': 32,
    'shift': 16, 'ctrl': 17, 'alt': 18, 'caps': 20,
    'up': 38, 'down': 40, 'left': 37, 'right': 39,
}


def _key_to_vk(key: str) -> int:
    k = key.lower()
    if k in VK_CODES:
        return VK_CODES[k]
    if len(key) == 1:
        return ord(key.upper())
    raise ValueError(f"Unknown key: {key}")


def _press_vk_keybd(vk: int):
    ctypes.windll.user32.keybd_event(vk, 0, 0, 0)


def _release_vk_keybd(vk: int):
    ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)


def press_key(key: str, seed: Optional[int] = None):
    if seed is not None:
        random.seed(seed)
    hold = random.uniform(0.077, 0.106)   # giữ phím ngẫu nhiên ~80-106ms
    pre = random.uniform(0.082, 0.131)    # trễ trước khi nhấn ~82-131ms
    time.sleep(pre)
    vk = _key_to_vk(key)
    _press_vk_keybd(vk)
    time.sleep(hold)
    _release_vk_keybd(vk)


def hold_key(key: str):
    vk = _key_to_vk(key)
    _press_vk_keybd(vk)


def release_key(key: str):
    vk = _key_to_vk(key)
    _release_vk_keybd(vk)
