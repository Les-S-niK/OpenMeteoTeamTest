import math
from bisect import bisect_right
from datetime import date
from enum import Enum
from typing import Self

from pydantic import BaseModel, Field, computed_field


class WeatherType(str, Enum):
    icon: str
    alt: str

    def __new__(cls, value: str, icon: str, alt: str) -> Self:
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.icon = icon
        obj.alt = alt
        return obj

    CLEAR = ("clear", "sun.png", "Ясно")
    PARTLY_CLOUDY = ("partly_cloudy", "cloud-sun.png", "Переменная облачность")
    CLOUDS = ("clouds", "cloud.png", "Пасмурно")
    RAIN = ("rain", "rain.png", "Дождь")
    THUNDERSTORM = ("thunderstorm", "storm.png", "Гроза")


WMO_TO_WEATHER_TYPE: dict[int, WeatherType] = {
    0: WeatherType.CLEAR,
    **dict.fromkeys((1, 2), WeatherType.PARTLY_CLOUDY),
    **dict.fromkeys((3, 45, 48, 71, 73, 75, 77, 85, 86), WeatherType.CLOUDS),
    **dict.fromkeys(
        (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82), WeatherType.RAIN
    ),
    **dict.fromkeys((95, 96, 99), WeatherType.THUNDERSTORM),
}


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
        return cls(type=WMO_TO_WEATHER_TYPE.get(code, WeatherType.CLOUDS))


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
    condition: WeatherCondition = Field(examples=[WeatherCondition.from_wmo(0)])
    hourly_condition: list[WeatherCondition] = Field(
        examples=[[WeatherCondition.from_wmo(1), WeatherCondition.from_wmo(3)]]
    )
    wind_force: WindForce
    temperature: float = Field(description="°C")
    feels_like_temp: float = Field(description="Ощущаемая температура, °C")
    water_temperature: float = Field(description="°C")
    humidity: int = Field(description="%")
    pressure: float = Field(description="мм. рт. ст.")
    uv_index: float


class DaysOfWeekWeather(BaseModel):
    temperature: float
    condition: WeatherCondition
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
                    condition=WeatherCondition.from_wmo(0),
                    date=date(2026, 10, 9),
                ),
                DaysOfWeekWeather(
                    temperature=21.0,
                    condition=WeatherCondition.from_wmo(3),
                    date=date(2026, 10, 10),
                ),
            ]
        ],
    )
