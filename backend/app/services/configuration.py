from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.configuration import PlatformConfig
from app.models.enums import WeatherState
from app.schemas.config import PlatformConfigUpdate


class ConfigurationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_create(self) -> PlatformConfig:
        result = await self.session.execute(select(PlatformConfig).where(PlatformConfig.name == "default"))
        config = result.scalar_one_or_none()
        if config:
            return config
        config = PlatformConfig(
            name="default",
            weather_enabled=True,
            demo_mode=True,
            deterministic_mode=True,
            rain_pause_enabled=True,
            low_battery_threshold=24.0,
            collision_threshold=0.65,
            geofence_tolerance_m=4.0,
            simulator_tick_seconds=1.0,
            current_weather=WeatherState.CLEAR,
            weather_intensity=0.12,
        )
        self.session.add(config)
        await self.session.flush()
        return config

    async def update(self, payload: PlatformConfigUpdate) -> PlatformConfig:
        config = await self.get_or_create()
        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(config, field, value)
        await self.session.flush()
        return config
