"""
Класс врага
"""
from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtCore import Qt


class Enemy(QGraphicsRectItem):
    """Класс врага с AI"""

    ENEMY_WIDTH = 35
    ENEMY_HEIGHT = 35
    MOVE_SPEED = 2
    PATROL_DISTANCE = 100

    def __init__(self, x, y, scene):
        super().__init__(0, 0, self.ENEMY_WIDTH, self.ENEMY_HEIGHT)
        self.game_scene = scene

        self.setBrush(QBrush(QColor(255, 0, 0)))
        self.setPen(QPen(Qt.GlobalColor.black, 2))

        self.setPos(x, y)
        self.start_x = x
        self.direction = 1

    def update(self):
        """Обновление AI врага"""
        self.setPos(self.x() + self.MOVE_SPEED * self.direction, self.y())

        if abs(self.x() - self.start_x) > self.PATROL_DISTANCE:
            self.direction *= -1

        self.setPos(self.x(), self.y() + self.game_scene.GRAVITY)

        for platform in self.game_scene.platforms:
            if self.collidesWithItem(platform):
                self.setPos(self.x(), platform.y() - self.ENEMY_HEIGHT)
                break
