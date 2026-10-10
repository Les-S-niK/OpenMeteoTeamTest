import math
from bisect import bisect_right
from datetime import date
from enum import Enum
from typing import Self

from pydantic import BaseModel, Field, computed_field


class WeatherType(str, Enum):
    icon: str
    alt: str
    codes: tuple[int, ...]

    def __new__(cls, value: str, icon: str, alt: str, codes: tuple[int, ...]) -> Self:
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.icon = icon
        obj.alt = alt
        obj.codes = codes
        return obj

    CLEAR = ("clear", "sun.png", "Ясно", (0,))
    PARTLY_CLOUDY = ("partly_cloudy", "cloud-sun.png", "Переменная облачность", (1, 2))
    CLOUDS = ("clouds", "cloud.png", "Пасмурно", (3, 45, 48, 71, 73, 75, 77, 85, 86))
    RAIN = (
        "rain",
        "rain.png",
        "Дождь",
        (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82),
    )
    THUNDERSTORM = ("thunderstorm", "storm.png", "Гроза", (95, 96, 99))

    @classmethod
    def from_wmo(cls, code: int) -> WeatherType:
        for weather_type in cls:
            if code in weather_type.codes:
                return weather_type
        return cls.CLOUDS  # Запасной вариант


class WeatherCondition(BaseModel):
    type: WeatherType

    @computed_field
    @property
    def icon(self) -> str:
        return self.type.icon

    @computed_field
    @property
    def alt(self) -> str:
        return self.type.alt

    @classmethod
    def from_wmo(cls, code: int) -> WeatherCondition:
        return cls(type=WeatherType.from_wmo(code))


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
    temperature: float = Field(description="°C")
    water_temperature: float = Field(description="°C")
    humidity: int = Field(description="%")
    pressure: float = Field(description="мм. рт. ст.")
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
