#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from models import Position
from typing import Any, Dict, List, Optional

# belongs to Mirko - should be deleted later
API_KEY = "720ad709ee32204a850f50794813a928"

BASE_URL = "https://api.openweathermap.org/data/2.5"
ONE_CALL_API_URL = f"{BASE_URL}/onecall?lat={{lat}}&lon={{lon}}&exclude=alerts,minutely,daily&appid={API_KEY}"
ONE_CALL_TIMEMACHINE_API_URL = f"{BASE_URL}/onecall/timemachine?lat={{lat}}&lon={{lon}}&dt={{dt}}&appid={API_KEY}"


class SingleForecast(object):
    def __init__(self,
                 cloudiness: Optional[int],
                 wind_speed: Optional[float],
                 wind_gust: Optional[float],
                 unix_timestamp: Optional[int],
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

    def __str__(self) -> str:
        return f"{f'{self.unix_timestamp} (UTC):' if self.unix_timestamp is not None else '????????????????:'}{f' clouds={self.cloudiness}%' if self.cloudiness is not None else ''}{f' wind={self.wind_speed}m/s' if self.wind_speed is not None else ''}{f' gust={self.wind_gust}m/s' if self.wind_gust is not None else ''}"

    @staticmethod
    def from_json_dict(dic: Dict[str, Any]):
        return SingleForecast(
            cloudiness=dic.get('clouds', None),
            wind_speed=dic.get('wind_speed', None),
            wind_gust=dic.get('wind_gust', None),
            unix_timestamp=dic.get('dt', None)
        )


def concatenate_lists(lists: List[List[Any]]) -> List[Any]:
    if len(lists) == 0:
        return []

    if len(lists) == 1:
        return lists[0]

    res = lists[0]
    for l in lists[1:]:
        res += l
    return res


class OpenWeatherMapForecast(object):
    def __init__(self, hourly: Optional[List[SingleForecast]] = None):
        if hourly is None:
            hourly = []
        self.hourly = hourly

    def __str__(self) -> str:
        return f"{len(self.hourly)} Hours\n" + "\n".join([forecast.__str__() for forecast in self.hourly])

    @staticmethod
    def from_json_dict(dic: Dict[str, Any]):
        return OpenWeatherMapForecast(
            hourly=[SingleForecast.from_json_dict(hourly_forecast_dict) for hourly_forecast_dict in
                    dic.get('hourly', [])]
        )

    @staticmethod
    def from_json_dicts(dicts: List[Dict[str, Any]]):
        return OpenWeatherMapForecast(
            hourly=[SingleForecast.from_json_dict(hourly_forecast_dict) for hourly_forecast_dict in
                    concatenate_lists([dic.get('hourly', []) for dic in dicts])]
        )


class OneCallApiResponse(object):
    def __init__(self, forecast: Optional[OpenWeatherMapForecast] = None):
        if forecast is None:
            forecast = OpenWeatherMapForecast()
        self.forecast = forecast

    def __str__(self) -> str:
        return "Forecast:\n\n" + self.forecast.__str__()

    @staticmethod
    def from_response(resp: requests.Response):
        json_response = resp.json()

        return OneCallApiResponse(
            forecast=OpenWeatherMapForecast.from_json_dict(json_response)
        )

    @staticmethod
    def from_responses(responses: List[requests.Response]):
        json_responses = [resp.json() for resp in responses]

        return OneCallApiResponse(
            forecast=OpenWeatherMapForecast.from_json_dicts(json_responses)
        )


# def request_one_call_api(pos: Position) -> OneCallApiResponse:
#     url = ONE_CALL_API_URL.format(lat=pos.latitude, lon=pos.longitude)
#     print(f"requesting {url}")
#     resp: Dict[str, Any] = requests.get(url).json()
#     pprint(resp)
#
#     return OneCallApiResponse()

SECONDS_PER_HOUR = 60 * 60
SECONDS_PER_DAY = 24 * SECONDS_PER_HOUR


def request_one_call_timemachine_api(pos: Position, unix_timestamp: int) -> OneCallApiResponse:
    """
    Requests historic weather data for 24h. Maybe only works for the last 5 days, not sure...

    :param pos: a position on earth
    :param unix_timestamp: a unix timestamp directly AFTER the wanted 24h forecast epoch, given in UTC
    :return: a forecast with hourly weather data
    """

    # Data block contains hourly historical data starting at 00:00 on the requested day and continues until 23:59 on
    # the same day (UTC time)
    timestamps_to_request = [unix_timestamp - SECONDS_PER_DAY, unix_timestamp]

    urls_to_request = [ONE_CALL_TIMEMACHINE_API_URL.format(lat=pos.latitude, lon=pos.longitude, dt=dt) for dt in
                       timestamps_to_request]
    responses: List[requests.Response] = [requests.get(url) for url in urls_to_request]

    resp = OneCallApiResponse.from_responses(responses)

    return resp


if __name__ == '__main__':
    position = Position(
        latitude=52.5041664,
        longitude=13.4119424
    )  # Berlin
    unix_time = 1647713846 - 400000

    response = request_one_call_timemachine_api(position, unix_time)
    print(response)
