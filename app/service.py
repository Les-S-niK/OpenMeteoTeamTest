import asyncio
from typing import Any

import aiohttp

from app.models import LocationInfo, TodayWeather, WeatherCondition, WindForce

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


async def _fetch(sess: aiohttp.ClientSession, url: str, **params) -> dict[str, Any]:
    params = {
        **SOCHI_COORDINATE,
        **params,
        "forecast_days": 1,
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
    )
    result = {
        "current": data.get("current", {}),
        "current_units": data.get("current_units", {}),
        "hourly": data.get("hourly", {}),
        "hourly_units": data.get("hourly_units", {}),
    }

    return result


async def _get_marine_temperature(sess: aiohttp.ClientSession) -> float | None:
    data = await _fetch(sess, MARINE_URL, current=MARINE_CURRENT)
    return data.get("current", {}).get("sea_surface_temperature")


async def _get_week_weather(sess: aiohttp.ClientSession): ...


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


async def main():
    async with aiohttp.ClientSession() as sess:
        return await build_today_weather(sess)


if __name__ == "__main__":
    result = asyncio.run(main())
    print(result.model_dump_json(indent=4))
