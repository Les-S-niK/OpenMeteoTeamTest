from fastapi import FastAPI

from app.models import (
    TodayWeather,
    WeatherSummary,
)

app: FastAPI = FastAPI()


@app.get("/health/")
async def health():
    return {"status": "ok"}


@app.post("/weather/today")
async def get_today_weather() -> TodayWeather: ...


@app.post("/weather/week")
async def get_week_weather() -> WeatherSummary: ...
