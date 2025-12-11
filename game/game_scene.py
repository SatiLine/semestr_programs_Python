"""
Игровая сцена
"""
from PyQt6.QtWidgets import QGraphicsScene, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor
from game.player import Player
from game.platform import Platform
from game.enemy import Enemy
from game.coin import Coin
from game.sword import Sword
from database.db_manager import DatabaseManager


class GameScene(QGraphicsScene):
    """Класс игровой сцены"""

    SCENE_WIDTH = 800
    SCENE_HEIGHT = 600
    GRAVITY = 0.5

    def __init__(self, game_window):
        super().__init__(0, 0, self.SCENE_WIDTH, self.SCENE_HEIGHT)
        self.game_window = game_window
        self.setBackgroundBrush(QBrush(QColor(135, 206, 235)))

        self.platforms = []
        self.enemies = []
        self.coins = []
        self.swords = []

        self.player = Player(self)
        self.addItem(self.player)

        self.current_level = 1
        self.load_level(1)

        self.keys_pressed = set()
        self.attack_cooldown = 0
        self.ATTACK_COOLDOWN_TIME = 20

        # Имя игрока (устанавливается из game_window)
        self.current_player = "Игрок1"

        self.db = DatabaseManager()

    def load_level(self, level_number):
        """Загрузка уровня"""
        self.current_level = level_number

        # Очищаем сцену
        for platform in self.platforms:
            self.removeItem(platform)
        for enemy in self.enemies:
            self.removeItem(enemy)
        for coin in self.coins:
            self.removeItem(coin)
        for sword in self.swords:
            self.removeItem(sword)

        self.platforms.clear()
        self.enemies.clear()
        self.coins.clear()
        self.swords.clear()

        # Сбрасываем игрока
        self.player.setPos(50, 400)
        self.player.velocity_x = 0
        self.player.velocity_y = 0
        self.player.health = 100
        self.player.update_color()

        # Создаём уровень
        ground = Platform(0, 550, 800, 50)
        self.platforms.append(ground)
        self.addItem(ground)

        platform_data = [
            (150, 450, 120, 20), (320, 380, 120, 20), (500, 310, 120, 20),
            (650, 240, 120, 20), (200, 250, 100, 20), (400, 180, 150, 20),
        ]

        for x, y, width, height in platform_data:
            platform = Platform(x, y, width, height)
            self.platforms.append(platform)
            self.addItem(platform)

        enemy_positions = [(300, 330), (550, 260), (450, 130)]
        for x, y in enemy_positions:
            enemy = Enemy(x, y, self)
            self.enemies.append(enemy)
            self.addItem(enemy)

        coin_positions = [
            (180, 400), (350, 330), (530, 260),
            (680, 190), (230, 200), (430, 130)
        ]
        for x, y in coin_positions:
            coin = Coin(x, y)
            self.coins.append(coin)
            self.addItem(coin)

    def restart_level(self):
        """Перезапуск текущего уровня при смерти"""
        QMessageBox.warning(
            None,
            "Смерть!",
            f"Здоровье = 0\nУровень {self.current_level} начинается заново"
        )

        # Добавляем смерть в статистику
        self.db.add_death(self.current_player)

        self.game_window.lose_life()
        self.load_level(self.current_level)

    def update_scene(self):
        """Обновление игровой логики"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # УПРАВЛЕНИЕ A D
        if Qt.Key.Key_A in self.keys_pressed:
            self.player.move_left()
        if Qt.Key.Key_D in self.keys_pressed:
            self.player.move_right()

        self.player.update()

        for enemy in self.enemies[:]:
            enemy.update()
            if self.player.collidesWithItem(enemy):
                self.player.take_damage(10)
                if self.player.x() < enemy.x():
                    self.player.setPos(self.player.x() - 30, self.player.y())
                else:
                    self.player.setPos(self.player.x() + 30, self.player.y())

        for sword in self.swords[:]:
            if not sword.update():
                self.removeItem(sword)
                self.swords.remove(sword)
                continue

            for enemy in self.enemies[:]:
                if sword.collidesWithItem(enemy):
                    self.removeItem(enemy)
                    self.enemies.remove(enemy)
                    self.game_window.add_score(50)

                    # Добавляем убийство в статистику
                    self.game_window.add_enemy_killed()

                    break

        for coin in self.coins[:]:
            if self.player.collidesWithItem(coin):
                self.removeItem(coin)
                self.coins.remove(coin)
                self.game_window.add_score(10)

                # Добавляем монету в статистику
                self.game_window.add_coin_collected()

        if len(self.coins) == 0 and len(self.enemies) == 0:
            self.game_window.level_complete()

    def handle_key_press(self, event):
        """Обработка нажатия клавиш"""
        self.keys_pressed.add(event.key())

        if event.key() == Qt.Key.Key_Space:
            self.player.jump()

    def handle_key_release(self, event):
        """Обработка отпускания клавиш"""
        key = event.key()
        self.keys_pressed.discard(key)

        # Останавливаем движение при отпускании A/D
        if key == Qt.Key.Key_A or key == Qt.Key.Key_D:
            self.player.stop_horizontal()

    def handle_mouse_press(self, event):
        """Обработка нажатия мыши"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.sword_attack()

    def sword_attack(self):
        """Выполнение атаки мечом"""
        if self.attack_cooldown > 0:
            return

        direction_right = not (Qt.Key.Key_A in self.keys_pressed)

        sword = Sword(self.player.x(), self.player.y(), direction_right)
        self.swords.append(sword)
        self.addItem(sword)

        self.attack_cooldown = self.ATTACK_COOLDOWN_TIME
        self.player.attack_animation()
