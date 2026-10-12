from contextlib import asynccontextmanager
from typing import Annotated

import aiohttp
from fastapi import Depends, FastAPI, Request

from app.models import (
    TodayWeather,
    WeatherSummary,
)
from app.service import build_today_weather, build_weekly_weather


@asynccontextmanager
async def lifespan(app: FastAPI):
    timeout = aiohttp.ClientTimeout(total=10, connect=3)
    connector = aiohttp.TCPConnector(limit=100, ttl_dns_cache=300)
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as sess:
        app.state.http = sess
        yield


app: FastAPI = FastAPI(lifespan=lifespan)


def get_http(request: Request) -> aiohttp.ClientSession:
    return request.app.state.http


HttpSession = Annotated[aiohttp.ClientSession, Depends(get_http)]


@app.get("/health/")
async def health():
    return {"status": "ok"}


@app.get("/weather/today")
async def get_today_weather(sess: HttpSession) -> TodayWeather:
    return await build_today_weather(sess=sess)


@app.get("/weather/week")
async def get_week_weather(sess: HttpSession) -> WeatherSummary:
    return await build_weekly_weather(sess=sess)
