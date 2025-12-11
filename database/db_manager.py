"""
Менеджер базы данных
"""
import sqlite3
from datetime import datetime


class DatabaseManager:
    """Класс для работы с базой данных SQLite"""

    DB_NAME = "game_data.db"

    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        """Подключение к базе данных"""
        self.connection = sqlite3.connect(self.DB_NAME)
        self.cursor = self.connection.cursor()

    def disconnect(self):
        """Отключение от базы данных"""
        if self.connection:
            self.connection.close()

    def init_database(self):
        """Инициализация базы данных"""
        self.connect()

        # Таблица 1: Результаты игроков
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                score INTEGER NOT NULL,
                level INTEGER NOT NULL,
                play_time INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Таблица 2: Статистика уровней
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS level_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level_number INTEGER NOT NULL UNIQUE,
                completed_times INTEGER DEFAULT 0,
                best_time INTEGER DEFAULT 9999
            )
        """)

        # Таблица 3: Детальная статистика игрока
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL UNIQUE,
                total_deaths INTEGER DEFAULT 0,
                total_coins_collected INTEGER DEFAULT 0,
                total_enemies_killed INTEGER DEFAULT 0,
                total_games_played INTEGER DEFAULT 0,
                total_playtime INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Заполняем начальные данные для уровней
        for level_num in [1, 2, 3]:
            self.cursor.execute("""
                INSERT OR IGNORE INTO level_stats (level_number)
                VALUES (?)
            """, (level_num,))

        self.connection.commit()
        self.disconnect()

    def add_player_score(self, name, score, level, play_time):
        """Добавление результата игрока"""
        self.connect()

        self.cursor.execute("""
            INSERT INTO players (name, score, level, play_time)
            VALUES (?, ?, ?, ?)
        """, (name, score, level, play_time))

        self.connection.commit()
        self.disconnect()

    def get_top_scores(self, limit=10):
        """Получение топ результатов"""
        self.connect()

        self.cursor.execute("""
            SELECT id, name, score, level, play_time, created_at
            FROM players
            ORDER BY score DESC, play_time ASC
            LIMIT ?
        """, (limit,))

        results = self.cursor.fetchall()
        self.disconnect()

        return results

    def increment_level_completions(self, level_number):
        """Увеличение счётчика прохождений уровня"""
        self.connect()

        self.cursor.execute("""
            UPDATE level_stats
            SET completed_times = completed_times + 1
            WHERE level_number = ?
        """, (level_number,))

        self.connection.commit()
        self.disconnect()

    def update_level_best_time(self, level_number, time):
        """Обновление лучшего времени уровня"""
        self.connect()

        self.cursor.execute("""
            UPDATE level_stats
            SET best_time = MIN(best_time, ?)
            WHERE level_number = ?
        """, (time, level_number))

        self.connection.commit()
        self.disconnect()

    def get_level_stats(self, level_number):
        """Получение статистики уровня"""
        self.connect()

        self.cursor.execute("""
            SELECT completed_times, best_time
            FROM level_stats
            WHERE level_number = ?
        """, (level_number,))

        result = self.cursor.fetchone()
        self.disconnect()

        return result

    def get_all_level_stats(self):
        """Получение статистики всех уровней"""
        self.connect()

        self.cursor.execute("""
            SELECT level_number, completed_times, best_time
            FROM level_stats
            ORDER BY level_number
        """)

        results = self.cursor.fetchall()
        self.disconnect()

        return results

    # ========================================================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С ДЕТАЛЬНОЙ СТАТИСТИКОЙ ИГРОКА
    # ========================================================================

    def init_player_stats(self, player_name):
        """Инициализация статистики для нового игрока"""
        self.connect()

        self.cursor.execute("""
            INSERT OR IGNORE INTO player_stats (player_name)
            VALUES (?)
        """, (player_name,))

        self.connection.commit()
        self.disconnect()

    def add_death(self, player_name):
        """Добавление смерти игроку"""
        self.connect()

        self.cursor.execute("""
            INSERT OR IGNORE INTO player_stats (player_name)
            VALUES (?)
        """, (player_name,))

        self.cursor.execute("""
            UPDATE player_stats
            SET total_deaths = total_deaths + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE player_name = ?
        """, (player_name,))

        self.connection.commit()
        self.disconnect()

    def add_coin(self, player_name, count=1):
        """Добавление собранных монет"""
        self.connect()

        self.cursor.execute("""
            INSERT OR IGNORE INTO player_stats (player_name)
            VALUES (?)
        """, (player_name,))

        self.cursor.execute("""
            UPDATE player_stats
            SET total_coins_collected = total_coins_collected + ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE player_name = ?
        """, (count, player_name))

        self.connection.commit()
        self.disconnect()

    def add_kill(self, player_name, count=1):
        """Добавление убитых врагов"""
        self.connect()

        self.cursor.execute("""
            INSERT OR IGNORE INTO player_stats (player_name)
            VALUES (?)
        """, (player_name,))

        self.cursor.execute("""
            UPDATE player_stats
            SET total_enemies_killed = total_enemies_killed + ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE player_name = ?
        """, (count, player_name))

        self.connection.commit()
        self.disconnect()

    def increment_games_played(self, player_name):
        """Увеличение счётчика сыгранных игр"""
        self.connect()

        self.cursor.execute("""
            INSERT OR IGNORE INTO player_stats (player_name)
            VALUES (?)
        """, (player_name,))

        self.cursor.execute("""
            UPDATE player_stats
            SET total_games_played = total_games_played + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE player_name = ?
        """, (player_name,))

        self.connection.commit()
        self.disconnect()

    def add_playtime(self, player_name, seconds):
        """Добавление времени игры"""
        self.connect()

        self.cursor.execute("""
            INSERT OR IGNORE INTO player_stats (player_name)
            VALUES (?)
        """, (player_name,))

        self.cursor.execute("""
            UPDATE player_stats
            SET total_playtime = total_playtime + ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE player_name = ?
        """, (seconds, player_name))

        self.connection.commit()
        self.disconnect()

    def get_player_stats(self, player_name):
        """Получение статистики конкретного игрока"""
        self.connect()

        self.cursor.execute("""
            SELECT total_deaths, total_coins_collected, total_enemies_killed,
                   total_games_played, total_playtime
            FROM player_stats
            WHERE player_name = ?
        """, (player_name,))

        result = self.cursor.fetchone()
        self.disconnect()

        return result if result else (0, 0, 0, 0, 0)

    def get_all_players_stats(self):
        """Получение статистики всех игроков"""
        self.connect()

        self.cursor.execute("""
            SELECT player_name, total_deaths, total_coins_collected,
                   total_enemies_killed, total_games_played, total_playtime
            FROM player_stats
            ORDER BY total_games_played DESC
        """)

        results = self.cursor.fetchall()
        self.disconnect()

        return results

    def clear_all_stats(self):
        """Очистка всей статистики"""
        self.connect()

        self.cursor.execute("DELETE FROM players")
        self.cursor.execute("""
            UPDATE level_stats 
            SET completed_times = 0, best_time = 9999
        """)
        self.cursor.execute("DELETE FROM player_stats")

        self.connection.commit()
        self.disconnect()
