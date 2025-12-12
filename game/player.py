"""
Класс игрока
"""
from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtCore import Qt


class Player(QGraphicsRectItem):
    """Класс игрока с физикой"""

    PLAYER_WIDTH = 40
    PLAYER_HEIGHT = 50
    MOVE_SPEED = 5
    JUMP_VELOCITY = -12
    MAX_VELOCITY_Y = 15

    def __init__(self, scene):
        super().__init__(0, 0, self.PLAYER_WIDTH, self.PLAYER_HEIGHT)
        self.game_scene = scene

        # Движение теперь напрямую setPos()
        self.velocity_y = 0
        self.is_on_ground = False

        self.health = 100
        self.max_health = 100

        self.is_attacking = False
        self.attack_frame = 0

        self.update_color()
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setPos(50, 400)

    def update_color(self):
        """Обновление цвета игрока"""
        if self.is_attacking:
            self.setBrush(QBrush(QColor(255, 255, 0)))
        elif self.health > 50:
            self.setBrush(QBrush(QColor(0, 128, 255)))
        elif self.health > 25:
            self.setBrush(QBrush(QColor(255, 165, 0)))
        else:
            self.setBrush(QBrush(QColor(255, 0, 0)))

    def update(self):
        """Обновление физики игрока"""
        if self.is_attacking:
            self.attack_frame += 1
            if self.attack_frame > 10:
                self.is_attacking = False
                self.attack_frame = 0
                self.update_color()

        # Применяем гравитацию
        self.velocity_y += self.game_scene.GRAVITY

        if self.velocity_y > self.MAX_VELOCITY_Y:
            self.velocity_y = self.MAX_VELOCITY_Y

        # Только вертикальное движение через velocity_y
        # Горизонтальное движение в move_left() и move_right()
        new_y = self.y() + self.velocity_y
        self.setPos(self.x(), new_y)

        # Проверка коллизий с платформами
        self.is_on_ground = False
        for platform in self.game_scene.platforms:
            if self.collidesWithItem(platform):
                if self.velocity_y > 0:
                    # Приземление на платформу
                    self.setPos(self.x(), platform.y() - self.PLAYER_HEIGHT)
                    self.velocity_y = 0
                    self.is_on_ground = True
                elif self.velocity_y < 0:
                    # Удар головой о платформу
                    self.setPos(self.x(), platform.y() + platform.rect().height())
                    self.velocity_y = 0

        # Проверка границ по X
        if self.x() < 0:
            self.setPos(0, self.y())
        elif self.x() > self.game_scene.SCENE_WIDTH - self.PLAYER_WIDTH:
            self.setPos(self.game_scene.SCENE_WIDTH - self.PLAYER_WIDTH, self.y())

        # Падение за пределы экрана
        if self.y() > self.game_scene.SCENE_HEIGHT:
            self.take_damage(50)
            self.reset_position()

    def move_left(self):
        """Движение влево - ИСПРАВЛЕНО: напрямую двигает персонажа"""
        new_x = self.x() - self.MOVE_SPEED

        # Проверка границ
        if new_x < 0:
            new_x = 0

        self.setPos(new_x, self.y())

    def move_right(self):
        """Движение вправо - ИСПРАВЛЕНО: напрямую двигает персонажа"""
        new_x = self.x() + self.MOVE_SPEED

        # Проверка границ
        if new_x > self.game_scene.SCENE_WIDTH - self.PLAYER_WIDTH:
            new_x = self.game_scene.SCENE_WIDTH - self.PLAYER_WIDTH

        self.setPos(new_x, self.y())

    def stop_horizontal(self):
        """Остановка горизонтального движения - БОЛЬШЕ НЕ НУЖНА"""
        # персонаж останавливается автоматически,
        # когда клавиша не нажата
        pass

    def jump(self):
        """Прыжок"""
        if self.is_on_ground:
            self.velocity_y = self.JUMP_VELOCITY
            self.is_on_ground = False

    def attack_animation(self):
        """Запуск анимации атаки"""
        self.is_attacking = True
        self.attack_frame = 0
        self.update_color()

    def take_damage(self, damage):
        """Получение урона"""
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.update_color()
            # вызываем перезапуск уровня
            self.game_scene.restart_level()
        else:
            self.update_color()

    def reset_position(self):
        """Сброс позиции игрока"""
        self.setPos(50, 400)
        self.velocity_y = 0
