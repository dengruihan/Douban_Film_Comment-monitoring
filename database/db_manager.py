import sqlite3
import os
import logging
from config.settings import DB_PATH

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_path = db_path or DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS movie_info (
                    movie_id TEXT PRIMARY KEY,
                    movie_name TEXT,
                    avg_rating REAL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS movie_comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    movie_id TEXT,
                    user_name TEXT,
                    star_rating INTEGER,
                    comment_text TEXT,
                    vote_count INTEGER,
                    comment_time TEXT,
                    UNIQUE(movie_id, user_name)
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_movie_id ON movie_comments(movie_id)
            """)
            conn.commit()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def insert_movie_info(self, movie_id, movie_name, avg_rating):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO movie_info (movie_id, movie_name, avg_rating)
                VALUES (?, ?, ?)
            """, (movie_id, movie_name, avg_rating))
            conn.commit()

    def insert_comments(self, comments):
        if not comments:
            return 0
        inserted = 0
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for comment in comments:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO movie_comments
                        (movie_id, user_name, star_rating, comment_text, vote_count, comment_time)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        comment.get("movie_id"),
                        comment.get("user_name"),
                        comment.get("star_rating"),
                        comment.get("comment_text"),
                        comment.get("vote_count"),
                        comment.get("comment_time")
                    ))
                    if cursor.rowcount > 0:
                        inserted += 1
                except Exception as e:
                    logger.error(f"插入评论失败: {e}")
            conn.commit()
        return inserted

    def get_movie_info(self, movie_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT movie_id, movie_name, avg_rating FROM movie_info WHERE movie_id = ?
            """, (movie_id,))
            row = cursor.fetchone()
            if row:
                return {"movie_id": row[0], "movie_name": row[1], "avg_rating": row[2]}
            return None

    def get_comments(self, movie_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT movie_id, user_name, star_rating, comment_text, vote_count, comment_time
                FROM movie_comments WHERE movie_id = ?
                ORDER BY comment_time DESC
            """, (movie_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def comment_count(self, movie_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM movie_comments WHERE movie_id = ?
            """, (movie_id,))
            return cursor.fetchone()[0]

    def close(self):
        pass


_db_instance = None


def get_db():
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance