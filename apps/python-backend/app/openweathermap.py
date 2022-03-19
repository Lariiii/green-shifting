#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from pprint import pprint
from models import Position
from typing import Any, Dict, List, Optional

# belongs to Mirko - should be deleted later
API_KEY = "720ad709ee32204a850f50794813a928"

BASE_URL = "https://api.openweathermap.org/data/2.5"
ONE_CALL_API_URL = f"{BASE_URL}/onecall?lat={{lat}}&lon={{lon}}&exclude=alerts,minutely,daily&appid={API_KEY}"
ONE_CALL_TIMEMACHINE_API_URL = f"{BASE_URL}/onecall/timemachine?lat={{lat}}&lon={{lon}}&dt={{dt}}&appid={API_KEY}"


class SingleForecast(object):
    def __init__(self,
                 cloudiness: int,
                 wind_speed: float,
                 wind_gust: float,
                 unix_timestamp: int,
                 ):
        """
        :param cloudiness: in percent
        :param wind_speed: in metre/sec
        :param wind_gust: in metre/sec
        """
        self.cloudiness = cloudiness
        self.wind_speed = wind_speed
        self.wind_gust = wind_gust
        self.unix_timestamp = unix_timestamp

    @staticmethod
    def from_json_dict(dic: Dict[str, Any]):
        return SingleForecast(
            cloudiness=dic['clouds'],
            wind_speed=dic['wind_speed'],
            wind_gust=dic['wind_gust'],
            unix_timestamp=dic['dt']
        )


class OpenWeatherMapForecast(object):
    def __init__(self, hourly: Optional[List[SingleForecast]] = None):
        if hourly is None:
            hourly = []

        self.hourly = hourly

    @staticmethod
    def from_json_dict(dic: Dict[str, Any]):
        return OpenWeatherMapForecast(
            hourly=[SingleForecast.from_json_dict(hourly_forecast_dict) for hourly_forecast_dict in dic['hourly']]
        )


class OneCallApiResponse(object):
    def __init__(self, forecast: Optional[OpenWeatherMapForecast] = None):
        if forecast is None:
            forecast = OpenWeatherMapForecast()
        self.forecast = forecast

    @staticmethod
    def from_response(resp: requests.Response):
        json_response = resp.json()

        return OneCallApiResponse(
            forecast=OpenWeatherMapForecast.from_json_dict(json_response)
        )


# def request_one_call_api(pos: Position) -> OneCallApiResponse:
#     url = ONE_CALL_API_URL.format(lat=pos.latitude, lon=pos.longitude)
#     print(f"requesting {url}")
#     resp: Dict[str, Any] = requests.get(url).json()
#     pprint(resp)
#
#     return OneCallApiResponse()

def request_one_call_timemachine_api(pos: Position, unix_timestamp: int) -> OneCallApiResponse:
    """
    Requests historic weather data for one day.
    Data block contains hourly historical data starting at 00:00 on the requested day and continues until 23:59 on the same day (UTC time)

    :param pos: a position on earth
    :param unix_timestamp: a unix timestamp on the day of the wanted forecast epoch in UTC
    :return: a forecast with hourly weather data
    """
    url = ONE_CALL_API_URL.format(lat=pos.latitude, lon=pos.longitude, dt=unix_timestamp)
    print(f"requesting {url}")
    resp: requests.Response = requests.get(url)

    return OneCallApiResponse.from_response(resp)


if __name__ == '__main__':
    position = Position(
        latitude=52.5041664,
        longitude=13.4119424
    )  # Berlin
    unix_time = 1647713846 - 1000000

    response = request_one_call_timemachine_api(position, unix_time)
    pprint(response)
