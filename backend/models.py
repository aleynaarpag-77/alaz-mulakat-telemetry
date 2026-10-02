from typing import Optional
from pydantic import BaseModel


class TelemetryData(BaseModel):
    id: Optional[int] = None
    timestamp: str
    temperature: float
    rpm: int
    voltage: float