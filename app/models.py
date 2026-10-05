from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class WeatherType(str, Enum):
    SUNNY = "Sunny"
    RAINY = "Rainy"
    CLEAR = "Clear"
    CLOUDY = "Cloudy"


class CityRequest(BaseModel):
    city: str = Field(examples=["Sochi"])


class LocationInfo(BaseModel):
    city: str
    country: str
    date: date


class TodayWeather(BaseModel):
    temperature: float
    humidity: int
    pressure: float
    uv_index: float


class DaysOfWeekWeather(BaseModel):
    temperature: float
    condition: WeatherType


class WeatherSummary(BaseModel):
    location: LocationInfo
    today: TodayWeather
    weather_for_week: list[DaysOfWeekWeather]  # Погода на неделю
