from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RobotStatus


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str


class Point(OrmModel):
    x: float = Field(ge=0.0, le=5_000.0)
    y: float = Field(ge=0.0, le=5_000.0)


class TaskArea(OrmModel):
    label: str = Field(min_length=2, max_length=80)
    x: float = Field(ge=0.0, le=5_000.0)
    y: float = Field(ge=0.0, le=5_000.0)
    width: float = Field(gt=0.0, le=5_000.0)
    height: float = Field(gt=0.0, le=5_000.0)


class RobotSnapshotSummary(OrmModel):
    id: str
    name: str = Field(min_length=2, max_length=120)
    status: RobotStatus
    battery_level: float = Field(ge=0.0, le=100.0)


JsonObject = dict[str, Any]


T = TypeVar("T")


class ListResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
