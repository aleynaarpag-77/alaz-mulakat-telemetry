import asyncio
import random
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from models import TelemetryData
from database import init_db, insert_telemetry, get_latest_telemetry


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
templates = Jinja2Templates(directory="../frontend/templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/latest", response_model=List[TelemetryData])
async def read_latest_data(limit: int = 20):
    return get_latest_telemetry(limit)