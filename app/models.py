import math
from bisect import bisect_right
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


class WindForce(str, Enum):
    CALM = "Штиль"
    LIGHT_AIR = "Тихий ветер"
    LIGHT_BREEZE = "Легкий ветер"
    GENTLE_BREEZE = "Слабый ветер"
    MODERATE_BREEZE = "Умеренный ветер"
    FRESH_BREEZE = "Свежий ветер"
    STRONG_BREEZE = "Сильный ветер"
    HIGH_WIND = "Крепкий ветер"
    GALE = "Очень крепкий ветер"
    STRONG_GALE = "Шторм"
    STORM = "Сильный шторм"
    VIOLENT_STORM = "Жестокий шторм"
    HURRICANE = "Ураган"

    @staticmethod
    def from_speed(speed_kmh: float) -> WindForce:
        if not math.isfinite(speed_kmh) or speed_kmh < 0:
            raise ValueError(f"Некорректная скорость ветра: {speed_kmh!r}")
        index = bisect_right(_THRESHOLDS, speed_kmh)
        return _MEMBERS[index]


_THRESHOLDS = (1, 5, 11, 19, 28, 38, 49, 61, 74, 88, 102, 117)
_MEMBERS = tuple(WindForce)


class LocationInfo(BaseModel):
    city: str
    country: str
    date: date


class TodayWeather(BaseModel):
    location: LocationInfo
    condition: WeatherType
    wind_force: WindForce
    temperature: float
    water_temperature: float
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
