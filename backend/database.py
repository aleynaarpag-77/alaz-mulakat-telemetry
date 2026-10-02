import sqlite3
from typing import List

from models import TelemetryData

DB_FILE = "telemetry.db"


def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                temperature REAL NOT NULL,
                rpm INTEGER NOT NULL,
                voltage REAL NOT NULL
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON telemetry(timestamp)')
        conn.commit()


def insert_telemetry(data: TelemetryData):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO telemetry (timestamp, temperature, rpm, voltage) 
               VALUES (?, ?, ?, ?)''',
            (data.timestamp, data.temperature, data.rpm, data.voltage)
        )
        conn.commit()


def get_latest_telemetry(limit: int = 50) -> List[TelemetryData]:
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT id, timestamp, temperature, rpm, voltage 
               FROM telemetry ORDER BY timestamp DESC LIMIT ?''',
            (limit,)
        )
        rows = cursor.fetchall()
        return [TelemetryData(**dict(row)) for row in rows]