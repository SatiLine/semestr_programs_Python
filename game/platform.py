"""
Класс платформы
"""
from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtCore import Qt


class Platform(QGraphicsRectItem):
    """Класс платформы"""

    def __init__(self, x, y, width, height):
        super().__init__(0, 0, width, height)
        self.setBrush(QBrush(QColor(101, 67, 33)))
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setPos(x, y)

