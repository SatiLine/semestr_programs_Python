"""
Окно таблицы рекордов с полной статистикой
"""
from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem
from PyQt6.QtCore import QFile, Qt
from PyQt6 import uic
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


class LeaderboardWindow(QMainWindow):
    """Класс окна таблицы рекордов"""

    def __init__(self):
        super().__init__()
        self.load_ui()
        self.db = DatabaseManager()
        self.load_leaderboard()

    def load_ui(self):
        """Загрузка UI из файла QtDesigner"""
        # ИСПРАВЛЕНО: правильный путь для PyInstaller
        ui_path = resource_path("ui/leaderboard.ui")
        ui_file = QFile(ui_path)
        ui_file.open(QFile.OpenModeFlag.ReadOnly)
        uic.loadUi(ui_file, self)
        ui_file.close()

    def load_leaderboard(self):
        """Загрузка таблицы рекордов с ПОЛНОЙ статистикой"""
        scores = self.db.get_top_scores(10)

        self.table_leaderboard.setColumnCount(8)
        self.table_leaderboard.setHorizontalHeaderLabels([
            "Место", "Имя", "Счёт", "Уровень", "Время",
            "Монет", "Убийств", "Смертей"
        ])

        self.table_leaderboard.setRowCount(len(scores))

        for row, (player_id, name, score, level, play_time, created_at) in enumerate(scores):
            self.table_leaderboard.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table_leaderboard.setItem(row, 1, QTableWidgetItem(name))
            self.table_leaderboard.setItem(row, 2, QTableWidgetItem(str(score)))
            self.table_leaderboard.setItem(row, 3, QTableWidgetItem(str(level)))

            minutes = play_time // 60
            seconds = play_time % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            self.table_leaderboard.setItem(row, 4, QTableWidgetItem(time_str))

            player_stats = self.db.get_player_stats(name)
            if player_stats:
                deaths, coins, kills, games, total_time = player_stats
                self.table_leaderboard.setItem(row, 5, QTableWidgetItem(str(coins)))
                self.table_leaderboard.setItem(row, 6, QTableWidgetItem(str(kills)))
                self.table_leaderboard.setItem(row, 7, QTableWidgetItem(str(deaths)))
            else:
                self.table_leaderboard.setItem(row, 5, QTableWidgetItem("0"))
                self.table_leaderboard.setItem(row, 6, QTableWidgetItem("0"))
                self.table_leaderboard.setItem(row, 7, QTableWidgetItem("0"))

        for row in range(len(scores)):
            for col in range(8):
                item = self.table_leaderboard.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        self.table_leaderboard.resizeColumnsToContents()
