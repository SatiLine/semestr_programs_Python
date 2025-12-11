"""
Класс меча для атаки
"""
from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtCore import Qt


class Sword(QGraphicsRectItem):
    """Класс меча (анимация атаки)"""

    SWORD_WIDTH = 50
    SWORD_HEIGHT = 10
    ATTACK_DURATION = 10

    def __init__(self, x, y, direction_right):
        super().__init__(0, 0, self.SWORD_WIDTH, self.SWORD_HEIGHT)

        self.setBrush(QBrush(QColor(192, 192, 192)))
        self.setPen(QPen(Qt.GlobalColor.black, 2))

        self.direction_right = direction_right

        if direction_right:
            self.setPos(x + 40, y + 20)
        else:
            self.setPos(x - 50, y + 20)

        self.frame_count = 0

    def update(self):
        """Обновление анимации меча"""
        self.frame_count += 1
        return self.frame_count < self.ATTACK_DURATION

    def is_active(self):
        """Проверка активности меча"""
        return self.frame_count < self.ATTACK_DURATION
