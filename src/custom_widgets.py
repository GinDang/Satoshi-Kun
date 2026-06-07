# ============================================================
# custom_widgets.py  —  reconstructed from Python 3.13 bytecode
# Nút bấm Qt bo góc, đổi màu sáng hơn khi hover.
# ============================================================
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QColor, QCursor
from PySide6.QtCore import Qt


class ModernButton(QPushButton):
    def __init__(self, text, color):
        super().__init__(text)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
                border: none;
                outline: none;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(color, 20)};
                cursor: pointinghand; /* Hi\u1ec3n th\u1ecb h\u00ecnh b\u00e0n tay */
            }}
        """)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def lighten_color(self, color, percent):
        color = QColor(color)
        color.setHsv(color.hue(), color.saturation(), min(255, color.value() + percent))
        return color.name()
