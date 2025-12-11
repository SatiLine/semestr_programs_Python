"""
Класс монеты
"""
from PyQt6.QtWidgets import QGraphicsEllipseItem
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtCore import Qt


class Coin(QGraphicsEllipseItem):
    """Класс монеты для сбора"""

    COIN_SIZE = 20

    def __init__(self, x, y):
        super().__init__(0, 0, self.COIN_SIZE, self.COIN_SIZE)
        self.setBrush(QBrush(QColor(255, 215, 0)))
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setPos(x, y)

