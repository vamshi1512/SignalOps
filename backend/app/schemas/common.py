from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ApiMessage(BaseModel):
    message: str


T = TypeVar("T")


class ListResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int


class TimeSeriesPoint(BaseModel):
    timestamp: datetime
    value: float

