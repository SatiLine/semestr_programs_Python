"""
Игровое окно
"""
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QInputDialog
from PyQt6.QtCore import QFile, QTimer, Qt
from PyQt6 import uic
from game.game_scene import GameScene
from database.db_manager import DatabaseManager
import sys
import os


def resource_path(relative_path):
    """Получить абсолютный путь к ресурсу (работает с PyInstaller)"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class GameWindow(QMainWindow):
    """Класс игрового окна"""

    FPS = 60
    FRAME_TIME = 1000 // FPS

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.load_ui()

        self.db = DatabaseManager()

        # Игровые переменные
        self.score = 0
        self.level = 1
        self.lives = 3
        self.game_time = 0
        self.is_paused = False

        # НОВОЕ: Имя текущего игрока
        self.current_player = "Игрок1"

        # Счётчики для статистики
        self.coins_collected = 0
        self.enemies_killed = 0

        self.game_scene = GameScene(self)
        self.graphics_view.setScene(self.game_scene)

        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_game)

        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)

        self.start_game()

    def load_ui(self):
        """Загрузка UI из файла QtDesigner"""
        # ИСПРАВЛЕНО: правильный путь для PyInstaller
        ui_path = resource_path("ui/game_window.ui")
        ui_file = QFile(ui_path)
        ui_file.open(QFile.OpenModeFlag.ReadOnly)
        uic.loadUi(ui_file, self)
        ui_file.close()

    def start_game(self):
        """Запуск игры"""
        # Спрашиваем имя игрока
        name, ok = QInputDialog.getText(
            self,
            "Новая игра",
            "Введите ваше имя:"
        )

        if ok and name:
            self.current_player = name
        else:
            self.current_player = "Гость"

        # Инициализируем статистику игрока
        self.db.init_player_stats(self.current_player)

        # Увеличиваем счётчик игр
        self.db.increment_games_played(self.current_player)

        # Передаём имя в сцену
        self.game_scene.current_player = self.current_player

        self.game_timer.start(self.FRAME_TIME)
        self.clock_timer.start(1000)
        self.update_ui()

    def update_game(self):
        """Обновление игровой логики"""
        if not self.is_paused:
            self.game_scene.update_scene()

    def update_clock(self):
        """Обновление игрового времени"""
        if not self.is_paused:
            self.game_time += 1
            self.update_ui()

    def update_ui(self):
        """Обновление интерфейса"""
        self.label_score.setText(f"Счёт: {self.score}")
        self.label_level.setText(f"Уровень: {self.level}")
        self.label_lives.setText(f"Жизни: {self.lives}")

        minutes = self.game_time // 60
        seconds = self.game_time % 60
        self.label_time.setText(f"Время: {minutes:02d}:{seconds:02d}")

        self.progress_health.setValue(self.game_scene.player.health)

    def add_score(self, points):
        """Добавление очков"""
        self.score += points
        self.update_ui()

    def add_coin_collected(self):
        """Счётчик собранных монет"""
        self.coins_collected += 1
        self.db.add_coin(self.current_player, 1)

    def add_enemy_killed(self):
        """Счётчик убитых врагов"""
        self.enemies_killed += 1
        self.db.add_kill(self.current_player, 1)

    def lose_life(self):
        """Потеря жизни"""
        self.lives -= 1
        self.update_ui()

        if self.lives <= 0:
            self.game_over()

    def save_progress(self):
        """Сохранение прогресса игры"""
        # Сохраняем результат
        self.db.add_player_score(
            self.current_player,
            self.score,
            self.level,
            self.game_time
        )

        # Сохраняем время игры
        self.db.add_playtime(self.current_player, self.game_time)

        QMessageBox.information(
            self,
            "Сохранено",
            f"Результат сохранён!\nСчёт: {self.score}\nУровень: {self.level}"
        )

    def game_over(self):
        """Окончание игры"""
        self.game_timer.stop()
        self.clock_timer.stop()

        self.save_progress()

        self.close()
        if self.main_window:
            self.main_window.show()

    def level_complete(self):
        """Завершение уровня"""
        self.level += 1
        self.db.increment_level_completions(self.level - 1)

        QMessageBox.information(
            self,
            "Уровень пройден!",
            f"Поздравляем!\nПереход на уровень {self.level}"
        )

        self.game_scene.load_level(self.level)
        self.update_ui()

    def pause_game(self):
        """Пауза/возобновление игры"""
        self.is_paused = not self.is_paused

        if self.is_paused:
            QMessageBox.information(
                self,
                "Пауза",
                "Игра на паузе\nНажмите Enter для продолжения"
            )

    def exit_to_menu(self):
        """Выход в главное меню"""
        reply = QMessageBox.question(
            self,
            "Выход в меню",
            "Вернуться в главное меню?\nСохранить прогресс перед выходом?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No |
            QMessageBox.StandardButton.Cancel
        )

        if reply == QMessageBox.StandardButton.Cancel:
            return

        self.game_timer.stop()
        self.clock_timer.stop()

        if reply == QMessageBox.StandardButton.Yes:
            self.save_progress()

        self.close()
        if self.main_window:
            self.main_window.show()

    def keyPressEvent(self, event):
        """Обработка нажатий клавиатуры"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.pause_game()
        elif event.key() == Qt.Key.Key_Escape:
            self.exit_to_menu()
        else:
            self.game_scene.handle_key_press(event)

    def keyReleaseEvent(self, event):
        """Обработка отпускания клавиш"""
        self.game_scene.handle_key_release(event)

    def mousePressEvent(self, event):
        """Обработка нажатий мыши"""
        self.game_scene.handle_mouse_press(event)
