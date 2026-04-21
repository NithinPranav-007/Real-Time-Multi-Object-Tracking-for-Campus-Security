import sqlite3
import threading
from datetime import datetime


class AlertRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    object_id TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    message TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def add_alert(self, object_id: str, alert_type: str, message: str):
        ts = datetime.utcnow().isoformat()
        with self.lock:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO alerts (timestamp, object_id, alert_type, message) VALUES (?, ?, ?, ?)",
                    (ts, object_id, alert_type, message),
                )
                conn.commit()

    def get_alerts(self, limit: int = 200):
        with self.lock:
            with self._connect() as conn:
                rows = conn.execute(
                    "SELECT timestamp, object_id, alert_type, message FROM alerts ORDER BY id DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [
            {
                "timestamp": r[0],
                "object_id": r[1],
                "type": r[2],
                "message": r[3],
            }
            for r in rows
        ]
