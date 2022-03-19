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

WIND_FORCE_MIN_SPEED = 4  # m/s
WIND_FORCE_BEST_SPEED = 12  # m/s
WIND_FORCE_MAX_SPEED = 28  # m/s
WIND_FORCE_MAX_SPEED_GUST = 35  # m/s


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
        self.cloudiness: Optional[int] = None
        self.solar_efficiency: Optional[float] = None
        self.set_cloudiness(cloudiness)

        self.wind_speed: Optional[float] = None
        self.wind_gust: Optional[float] = None
        self.wind_efficiency: Optional[float] = None
        self.set_wind_speed(wind_speed, wind_gust)

        self.unix_timestamp: Optional[int] = unix_timestamp

    def set_cloudiness(self, cloudiness: Optional[int]) -> None:
        self.cloudiness = cloudiness
        if cloudiness is None:
            self.solar_efficiency = None
        else:
            # noinspection PyTypeChecker
            self.solar_efficiency = round(1 - cloudiness / 100, 3)

    def set_wind_speed(self, wind_speed: Optional[float], wind_gust: Optional[float]) -> None:
        self.wind_speed = wind_speed
        self.wind_gust = wind_gust

        # data source: https://www.suisse-eole.ch/de/windenergie/faq/ab-welcher-windgeschwindigkeit-dreht-eine-windenergieanlage-8/
        if wind_speed is None:
            self.wind_efficiency = None
        elif WIND_FORCE_MIN_SPEED <= wind_speed < WIND_FORCE_MAX_SPEED:
            if wind_gust is None or wind_gust < WIND_FORCE_MAX_SPEED_GUST:
                if wind_speed >= WIND_FORCE_BEST_SPEED:
                    self.wind_efficiency = 1.0
                else:
                    self.wind_efficiency = \
                        (wind_speed - WIND_FORCE_MIN_SPEED) / (WIND_FORCE_BEST_SPEED - WIND_FORCE_MIN_SPEED)
                    # noinspection PyTypeChecker
                    self.wind_efficiency = round(self.wind_efficiency, 3)
            else:
                # too strong gusts
                self.wind_efficiency = 0.0
        else:
            # not enough or too strong wind
            self.wind_efficiency = 0.0

    def __str__(self) -> str:
        return (f'{self.unix_timestamp} (UTC):' if self.unix_timestamp is not None else '????????????????:') + \
               (f' clouds={self.cloudiness}%' if self.cloudiness is not None else '') + \
               (f' wind={self.wind_speed}m/s' if self.wind_speed is not None else '') + \
               (f' gust={self.wind_gust}m/s' if self.wind_gust is not None else '') + \
               (f' solar_efficiency={self.solar_efficiency}' if self.solar_efficiency is not None else '') + \
               (f' wind_efficiency={self.wind_efficiency}' if self.wind_efficiency is not None else '')

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
        self.hourly: List[SingleForecast] = hourly

    def limit_to_time_range(self,
                            lower: Optional[int],
                            upper: Optional[int],
                            lower_inclusive: bool = True,
                            upper_inclusive: bool = False) -> None:
        if lower is not None:
            if lower_inclusive:
                self.hourly = [forecast for forecast in self.hourly if forecast.unix_timestamp >= lower]
            else:
                self.hourly = [forecast for forecast in self.hourly if forecast.unix_timestamp > lower]

        if upper is not None:
            if upper_inclusive:
                self.hourly = [forecast for forecast in self.hourly if forecast.unix_timestamp <= upper]
            else:
                self.hourly = [forecast for forecast in self.hourly if forecast.unix_timestamp < upper]

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
        self.forecast: OpenWeatherMapForecast = forecast

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


def request_url(url: str) -> requests.Response:
    print("Requesting URL " + url)
    return requests.get(url)


def request_one_call_timemachine_api(pos: Position, unix_timestamp: int) -> OneCallApiResponse:
    """
    Requests historic weather data for 24h. Maybe only works for the last 5 days, not sure...

    :param pos: a position on earth
    :param unix_timestamp: a unix timestamp directly AFTER the wanted 24h forecast epoch, given in UTC
    :return: a forecast with hourly weather data
    """

    # Data block contains hourly historical data starting at 00:00 on the requested day and continues until 23:59 on
    # the same day (UTC time)
    unix_timestamp_yesterday = unix_timestamp - SECONDS_PER_DAY
    timestamps_to_request = [unix_timestamp_yesterday, unix_timestamp]

    urls_to_request = [ONE_CALL_TIMEMACHINE_API_URL.format(lat=pos.latitude, lon=pos.longitude, dt=dt) for dt in
                       timestamps_to_request]

    responses: List[requests.Response] = [request_url(url) for url in urls_to_request]

    resp = OneCallApiResponse.from_responses(responses)
    resp.forecast.limit_to_time_range(
        lower=unix_timestamp_yesterday,
        upper=unix_timestamp,
        lower_inclusive=True,
        upper_inclusive=False
    )

    return resp


if __name__ == '__main__':
    position = Position(
        latitude=52.5041664,
        longitude=13.4119424
    )  # Berlin
    unix_time = 1647713846 - 400000

    response = request_one_call_timemachine_api(position, unix_time)
    print(response)
