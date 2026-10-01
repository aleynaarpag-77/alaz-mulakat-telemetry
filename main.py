import asyncio
import sqlite3
import random
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

DB_FILE = "telemetry.db"

class TelemetryData(BaseModel):
    id: Optional[int] = None
    timestamp: str
    temperature: float
    rpm: int
    voltage: float

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

async def generate_mock_data():
    while True:
        await asyncio.sleep(15)
        now = datetime.now(timezone.utc).isoformat()
        mock_data = TelemetryData(
            timestamp=now,
            temperature=round(random.uniform(70.0, 110.0), 2),
            rpm=random.randint(1500, 6000),
            voltage=round(random.uniform(11.5, 14.5), 2)
        )
        insert_telemetry(mock_data)
        print(f"[{now}] Generated mock data: Temp={mock_data.temperature}°C, RPM={mock_data.rpm}, Volt={mock_data.voltage}V")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    task = asyncio.create_task(generate_mock_data())
    yield
    task.cancel()

app = FastAPI(title="Alaz Telemetry System", lifespan=lifespan)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/latest", response_model=List[TelemetryData])
async def read_latest_data(limit: int = 20):
    return get_latest_telemetry(limit)
