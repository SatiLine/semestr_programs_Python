"""
Главное окно приложения
"""
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtCore import QFile
from PyQt6 import uic
from ui.game_window import GameWindow
from ui.leaderboard_window import LeaderboardWindow
import sys
import os


def resource_path(relative_path):
    """Получить абсолютный путь к ресурсу (работает с PyInstaller)"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class MainWindow(QMainWindow):
    """Класс главного окна с меню"""

    def __init__(self):
        super().__init__()
        self.load_ui()
        self.setup_connections()
        self.game_window = None
        self.leaderboard_window = None

    def load_ui(self):
        """Загрузка UI из файла QtDesigner"""
        # ИСПРАВЛЕНО: правильный путь для PyInstaller
        ui_path = resource_path("ui/main_menu.ui")
        ui_file = QFile(ui_path)
        ui_file.open(QFile.OpenModeFlag.ReadOnly)
        uic.loadUi(ui_file, self)
        ui_file.close()

    def setup_connections(self):
        """Настройка связей сигналов и слотов"""
        self.btn_new_game.clicked.connect(self.start_new_game)
        self.btn_leaderboard.clicked.connect(self.show_leaderboard)
        self.btn_exit.clicked.connect(self.close)

    def start_new_game(self):
        """Запуск новой игры"""
        self.game_window = GameWindow(main_window=self)
        self.game_window.show()
        self.hide()

    def show_leaderboard(self):
        """Отображение таблицы рекордов"""
        self.leaderboard_window = LeaderboardWindow()
        self.leaderboard_window.show()
