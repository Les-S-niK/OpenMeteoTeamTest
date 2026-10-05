from fastapi import FastAPI

from app.models import (
    CityRequest,
    TodayWeather,
    WeatherSummary,
)

app: FastAPI = FastAPI()


@app.post("/weather/today")
async def get_today_weather(body: CityRequest) -> TodayWeather: ...


@app.post("/weather/week")
async def get_week_weather(body: CityRequest) -> WeatherSummary: ...
