from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class WeatherType(str, Enum):
    CLEAR = "clear"
    CLOUDS = "clouds"
    RAIN = "rain"
    SNOW = "snow"
    THUNDERSTORM = "thunderstorm"
    DRIZZLE = "drizzle"
    FOG = "fog"


class LocationInfo(BaseModel):
    city: str
    country: str
    date: date


class TodayWeather(BaseModel):
    location: LocationInfo
    temperature: float
    humidity: int
    pressure: float
    uv_index: float


class DaysOfWeekWeather(BaseModel):
    temperature: float
    condition: WeatherType
    date: date


class WeatherSummary(BaseModel):
    """Прогноз погоды на неделю"""

    location: LocationInfo
    weather_for_week: list[DaysOfWeekWeather] = Field(
        ...,
        examples=[
            [
                DaysOfWeekWeather(
                    temperature=26.0,
                    condition=WeatherType.CLEAR,
                    date=date(2026, 10, 9),
                ),
                DaysOfWeekWeather(
                    temperature=21.0,
                    condition=WeatherType.CLOUDS,
                    date=date(2026, 10, 10),
                ),
            ]
        ],
    )
