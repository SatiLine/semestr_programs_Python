import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from database.db_manager import DatabaseManager


def main():
    """Инициализация и запуск приложения"""
    app = QApplication(sys.argv)
    app.setApplicationName("Platformer Game")

    # Инициализация базы данных
    db = DatabaseManager()
    db.init_database()

    # Создание и отображение главного окна
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
