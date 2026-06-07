# ============================================================
# tool_module.py  —  reconstructed from Python 3.13 bytecode
# LÕI BOT tự động chơi game:
#   - mss: chụp vùng màn hình trung tâm
#   - OpenCV: xử lý ảnh + so khớp mẫu (templates/chatcay.png)
#   - pytesseract OCR: đọc 1 ký tự (whitelist E/F/Y) trong minigame
#   - press_key / pynput: mô phỏng nhấn phím giống người
# Kịch bản: giữ Shift+W (di chuyển) + nhấn E (tương tác) + gõ ký tự OCR.
# ============================================================
import cv2
import numpy as np
import pyautogui
import os
import time
import threading
import mss
import pytesseract
from pynput.keyboard import Controller, Key
import keyboard
from utils import show_message, resource_path
from PySide6.QtCore import QObject, Signal
import random
import press_key


class Communicator(QObject):
    update_signal = Signal()


comm = Communicator()


class ToolBot:
    def __init__(self):
        self.is_running = False
        self.keyboard = Controller()
        pytesseract.pytesseract.tesseract_cmd = resource_path("Tesseract-OCR/tesseract.exe")
        self.threads = []
        pyautogui.FAILSAFE = False

    def capture_screen(self, size=1):
        with mss.mss() as sct:
            monitor = sct.monitors[screen_id]
            center_x = monitor["left"] + monitor["width"] // 2
            center_y = monitor["top"] + monitor["height"] // 2
            region = {
                "top": center_y + 10,
                "left": center_x - size // 2,
                "width": size,
                "height": size,
            }
            screenshot = np.array(sct.grab(region))
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        return thresh

    def capture_screen_for_cut(self, screen_id=1, region_width=250, region_height=70):
        with mss.mss() as sct:
            monitors = sct.monitors
            if screen_id >= len(monitors):
                print(f"\u26a0 Kh\u00f4ng t\u00ecm th\u1ea5y m\u00e0n h\u00ecnh {screen_id}, m\u1eb7c \u0111\u1ecbnh v\u1ec1 m\u00e0n h\u00ecnh ch\u00ednh.")
                screen_id = 0
            screen = monitors[screen_id]
            left = screen["left"] + 10
            top = screen["top"] + 10
            screenshot = sct.grab({"left": left, "top": top, "width": region_width, "height": region_height})
            img = np.array(screenshot)[:, :, :3]
            return img

    def extract_char(self, image):
        custom_config = "--oem 3 --psm 7 -c tessedit_char_whitelist=EFY"
        details = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)
        max_confidence, char = -1, None
        for i in range(len(details["text"])):
            word = details["text"][i].strip()
            confidence = int(details["conf"][i])
            if word.isalpha() and len(word) == 1 and confidence > 50:
                if confidence > max_confidence:
                    char, max_confidence = word, confidence
        return char

    def hold_shift_w(self):
        keyboard.press("w")
        self.keyboard.press(Key.shift)

    def release_shift_w(self):
        keyboard.release("w")
        self.keyboard.release(Key.space)

    def type_detected_char(self, char):
        if char:
            lowercase_char = char.lower()
            amount_type = random.randint(5, 10)
            for _ in range(amount_type):
                press_key(lowercase_char)

    def start_tool(self):
        self.is_running = True
        print("Tool Starting.")
        moving = False
        cut_template = cv2.imread(resource_path("templates/chatcay.png"))
        keyboard.press("w")
        time.sleep(0.2)
        self.keyboard.press(Key.shift)
        while self.is_running:
            if not self.is_running:
                return
            screenshot = self.capture_screen(40)
            screenshot_for_E = self.capture_screen_for_cut()
            result = cv2.matchTemplate(screenshot_for_E, cut_template, cv2.TM_CCOEFF_NORMED)
            threshold = 0.8
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if screenshot is not None:
                detected_char = self.extract_char(screenshot)
                if max_val >= threshold:
                    if moving:
                        self.release_shift_w()
                        moving = False
                    time_random = random.uniform(0.08, 0.15)
                    keyboard.press("e")
                    time.sleep(time_random)
                    keyboard.release("e")
                    time.sleep(0.2)
                if detected_char:
                    if moving:
                        self.release_shift_w()
                        moving = False
                    self.type_detected_char(detected_char)
                else:
                    if not moving:
                        self.hold_shift_w()
                        moving = True
            time.sleep(0.05)

    def stop_tool(self):
        self.is_running = False
        print("Tool stopped.")
        keyboard.release("w")
        self.keyboard.release(Key.shift)

    def start_tool_thread(self):
        self.stop_all_threads()
        self.is_running = True
        tool_thread = threading.Thread(target=self.start_tool, daemon=True)
        self.threads = [tool_thread]
        for thread in self.threads:
            thread.start()

    main_page_instance = None
    comm = None

    def stop_all_threads(self):
        self.is_running = False
        print("D\u1eebnggggggg")
        keyboard.release("w")
        self.keyboard.release(Key.shift)
        for thread in self.threads:
            try:
                thread.join(timeout=2)
            except Exception as e:
                print(f"Error stopping thread: {e}")
        if self.comm:
            self.comm.stop_signal.emit()
        self.threads.clear()

    def cleanup(self):
        try:
            self.stop_all_threads()
            print("\u0110\u00e3 d\u1ecdn d\u1eb9p t\u00e0i nguy\u00ean")
        except Exception as e:
            print(f"L\u1ed7i trong qu\u00e1 tr\u00ecnh d\u1ecdn d\u1eb9p: {e}")
            threading.Thread(target=self.start_tool, daemon=True).start()
