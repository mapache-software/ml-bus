from typing import Any
from datetime import datetime, timezone
from dataclasses import dataclass

@dataclass
class Metric:
    name: str
    value: float
    batch: int
    epoch: int
    phase: str

@dataclass
class Event:
    type: str
    producer: str
    payload: Any
    timestamp: datetime = datetime.now(timezone.utc)