import asyncio
from datetime import datetime
from typing import Any

import aiohttp

from app.models import (
    DaysOfWeekWeather,
    LocationInfo,
    TodayWeather,
    WeatherCondition,
    WeatherSummary,
    WindForce,
)

SOCHI_COORDINATE = {"latitude": 43.5992, "longitude": 39.7257}
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"

WEATHER_CURRENT = (
    "weather_code",
    "wind_speed_10m",
    "temperature_2m",
    "apparent_temperature",
    "relative_humidity_2m",
    "surface_pressure",
    "uv_index",
)
WEATHER_HOURLY = (
    "weather_code",
    "temperature_2m",
)
MARINE_CURRENT = "sea_surface_temperature"

WEEKLY_WEATHER = (
    "temperature_2m_mean",
    "weather_code",
)


async def _fetch(sess: aiohttp.ClientSession, url: str, **params) -> dict[str, Any]:
    params = {
        **SOCHI_COORDINATE,
        **params,
        "timezone": "auto",
    }
    async with sess.get(url, params=params) as response:
        response.raise_for_status()
        return await response.json()


async def _get_today_weather(sess: aiohttp.ClientSession) -> dict[str, Any]:
    data = await _fetch(
        sess,
        FORECAST_URL,
        current=",".join(WEATHER_CURRENT),
        hourly=",".join(WEATHER_HOURLY),
        forecast_days=1,
    )
    result = {
        "current": data.get("current", {}),
        "hourly": data.get("hourly", {}),
    }

    return result


async def _get_marine_temperature(sess: aiohttp.ClientSession) -> float | None:
    data = await _fetch(
        sess,
        MARINE_URL,
        current=MARINE_CURRENT,
        forecast_days=1,
    )
    return data.get("current", {}).get("sea_surface_temperature")


async def _get_week_weather(sess: aiohttp.ClientSession) -> dict[str, Any]:
    data = await _fetch(
        sess,
        FORECAST_URL,
        daily=WEEKLY_WEATHER,
        forecast_days=7,
    )
    return data.get("daily", {})


async def build_today_weather(sess: aiohttp.ClientSession) -> TodayWeather:
    air_weather, sea_temperature = await asyncio.gather(
        _get_today_weather(sess=sess),
        _get_marine_temperature(sess=sess),
    )
    sea_temperature = sea_temperature or 0.0

    current = air_weather.get("current", {})
    hourly = air_weather.get("hourly", {})
    weather_codes: list[int] = hourly.get("weather_code", [])

    weather_codes_every_4h = [*weather_codes[::4], weather_codes[23]]

    hourly_condition = [
        WeatherCondition.from_wmo(condition) for condition in weather_codes_every_4h
    ]

    result = TodayWeather(
        location=LocationInfo(city="Сочи", country="Россия", date=current.get("time")),
        condition=WeatherCondition.from_wmo(current.get("weather_code")),
        hourly_condition=hourly_condition,
        wind_force=WindForce.from_speed(current.get("wind_speed_10m")),
        temperature=current.get("temperature_2m"),
        feels_like_temp=current.get("apparent_temperature"),
        water_temperature=sea_temperature,
        humidity=current.get("relative_humidity_2m"),
        pressure=current.get("surface_pressure"),
        uv_index=current.get("uv_index"),
    )
    return result


async def build_weekly_weather(sess: aiohttp.ClientSession) -> WeatherSummary:
    daily = await _get_week_weather(sess=sess)

    dates: list[str] = daily.get("time", [])
    temperatures: list[int] = daily.get("temperature_2m_mean", [])
    weather_codes: list[int] = daily.get("weather_code", [])

    weekly_weather: list[DaysOfWeekWeather] = []

    for temp, weath_code, date in zip(temperatures, weather_codes, dates):
        weekly_weather.append(
            DaysOfWeekWeather(
                temperature=temp,
                condition=WeatherCondition.from_wmo(weath_code).type,
                date=datetime.fromisoformat(date),
            )
        )

    result = WeatherSummary(
        location=LocationInfo(
            city="Сочи", country="Россия", date=datetime.fromisoformat(dates[0])
        ),
        weather_for_week=weekly_weather,
    )
    return result


async def main():
    """Функция быстрой проверки при запуске отдельным скриптом"""
    async with aiohttp.ClientSession() as sess:
        results = await asyncio.gather(
            build_today_weather(sess),
            build_weekly_weather(sess),
            return_exceptions=True,
        )
        for name, res in zip(("Сегодняшняя", "Недельная"), results):
            print(f"\t{name.upper()} ПОГОДА\nСтатус: ", end="")
            if isinstance(res, (Exception, BaseException)):
                print(f"Ошибка: \n[{type(res).__name__}] {res}\n")
            else:
                print(f"Успешный результат \n{res.model_dump_json(indent=4)}\n")

        return results


if __name__ == "__main__":
    asyncio.run(main())
