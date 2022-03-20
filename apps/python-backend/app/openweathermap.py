#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import requests
from models import Position
from utils import unix_timestamp_to_datetime_str
from typing import Any, Dict, List, Optional, Tuple

# belongs to Mirko - should be deleted later
API_KEY = "ed8d992385ca6f2ae87669b34679bbe8"

BASE_URL = "https://api.openweathermap.org/data/2.5"
ONE_CALL_API_URL = f"{BASE_URL}/onecall?lat={{lat}}&lon={{lon}}&exclude=alerts,minutely,daily&appid={API_KEY}"
ONE_CALL_TIMEMACHINE_API_URL = f"{BASE_URL}/onecall/timemachine?lat={{lat}}&lon={{lon}}&dt={{dt}}&appid={API_KEY}"

WIND_FORCE_MIN_SPEED = 4  # m/s
WIND_FORCE_BEST_SPEED = 12  # m/s
WIND_FORCE_MAX_SPEED = 28  # m/s
WIND_FORCE_MAX_SPEED_GUST = 35  # m/s

logging.basicConfig()
logger = logging.getLogger("OpenWeatherMap")
logger.setLevel(logging.INFO)


class SingleForecast(object):
    def __init__(self,
                 cloudiness: Optional[int],
                 wind_speed: Optional[float],
                 wind_gust: Optional[float],
                 sunrise: Optional[int],
                 sunset: Optional[int],
                 unix_timestamp: Optional[int],
                 position: Optional[Position]
                 ):
        """
        :param cloudiness: in percent
        :param wind_speed: in metre/sec
        :param wind_gust: in metre/sec
        :param sunrise: unix timestamp in UTC of the sunrise on the current day at the current location
        :param sunset: unix timestamp in UTC of the sunset on the current day at the current location
        :param sunrise: unix timestamp in UTC of the forecast's timestamp
        """
        # must be set beforehand
        self.unix_timestamp: Optional[int] = unix_timestamp
        self.sunrise: Optional[int] = sunrise
        self.sunset: Optional[int] = sunset
        self.position: Optional[Position] = position

        self.cloudiness: Optional[int] = None
        self.solar_efficiency: Optional[float] = None
        self.set_cloudiness(cloudiness)

        self.wind_speed: Optional[float] = None
        self.wind_gust: Optional[float] = None
        self.wind_efficiency: Optional[float] = None
        self.set_wind_speed(wind_speed, wind_gust)

    def set_cloudiness(self, cloudiness: Optional[int]) -> None:
        self.cloudiness = cloudiness
        if cloudiness is None:
            logger.debug("solar_efficiency is None because cloudiness was None")
            self.solar_efficiency = None
        elif self.sunrise is None:
            logger.debug("solar_efficiency is None because sunrise was None")
            self.solar_efficiency = None
        elif self.unix_timestamp is None:
            logger.debug("solar_efficiency is None because unix_timestamp was None")
            self.solar_efficiency = None
        elif self.sunset is None:
            logger.debug("solar_efficiency is None because sunset was None")
            self.solar_efficiency = None
        else:
            if self.sunrise < self.unix_timestamp < self.sunset:
                efficiency = 1 - cloudiness / 100
                logger.debug(f"cloudiness={cloudiness}% -> max_efficiency={efficiency}")

                # assuming linear increase and decrease of the sun's intensity from sunrise to noon and
                # from noon to sunset
                intensity = (self.unix_timestamp - self.sunrise) / (self.sunset - self.sunrise)
                if intensity > 0.5:  # afternoon
                    intensity -= 0.5
                logger.debug(f"intensity={intensity}")

                # noinspection PyTypeChecker
                solar_efficiency = round(intensity * efficiency, 3)
                self.solar_efficiency = solar_efficiency
                logger.debug(f"solar_efficiency={solar_efficiency}")
            else:
                logger.debug("solar_efficiency is 0 because it is night")
                self.solar_efficiency = 0.0

    def set_wind_speed(self, wind_speed: Optional[float], wind_gust: Optional[float]) -> None:
        self.wind_speed = wind_speed
        self.wind_gust = wind_gust

        # data source: https://www.suisse-eole.ch/de/windenergie/faq/ab-welcher-windgeschwindigkeit-dreht-eine-windenergieanlage-8/
        if wind_speed is None:
            logger.debug("wind_efficiency is None because wind_speed was None")
            self.wind_efficiency = None
        elif WIND_FORCE_MIN_SPEED <= wind_speed < WIND_FORCE_MAX_SPEED:
            if wind_gust is None or wind_gust < WIND_FORCE_MAX_SPEED_GUST:
                if wind_speed >= WIND_FORCE_BEST_SPEED:
                    logger.debug(f"wind_efficiency is optimal with {wind_speed}m/s wind")
                    self.wind_efficiency = 1.0
                else:
                    wind_efficiency = \
                        (wind_speed - WIND_FORCE_MIN_SPEED) / (WIND_FORCE_BEST_SPEED - WIND_FORCE_MIN_SPEED)
                    # noinspection PyTypeChecker
                    self.wind_efficiency = round(wind_efficiency, 3)
                    logger.debug(f"wind_efficiency of {wind_efficiency} is NOT optimal with {wind_speed}m/s wind")
            else:
                logger.debug(f"wind_efficiency is 0 because wind_gust of {wind_gust}m/s was too high")
                # too strong gusts
                self.wind_efficiency = 0.0
        else:
            logger.debug(
                f"wind_efficiency is 0 because wind_speed of {wind_speed}m/s was either too low or too high"
            )
            # not enough or too strong wind
            self.wind_efficiency = 0.0

    def __str__(self) -> str:
        return (f'{self.unix_timestamp} (UTC):' if self.unix_timestamp is not None else '????????????????:') + \
               (f' {self.position.__str__()}' if self.position is not None else '') + \
               (f' sunrise={self.sunrise}%' if self.sunrise is not None else '') + \
               (f' sunset={self.sunset}%' if self.sunset is not None else '') + \
               (f' clouds={self.cloudiness}%' if self.cloudiness is not None else '') + \
               (f' wind={self.wind_speed}m/s' if self.wind_speed is not None else '') + \
               (f' gust={self.wind_gust}m/s' if self.wind_gust is not None else '') + \
               (f' solar_efficiency={self.solar_efficiency}' if self.solar_efficiency is not None else '') + \
               (f' wind_efficiency={self.wind_efficiency}' if self.wind_efficiency is not None else '')

    def log_efficiency(self, level: int = logging.INFO) -> None:
        # noinspection PyTypeChecker
        logger.log(level,
                   f"{unix_timestamp_to_datetime_str(self.unix_timestamp)}@{self.position.__str__()}: {round(self.solar_efficiency * 100) if self.solar_efficiency is not None else '?'} % solar and {round(self.wind_efficiency * 100) if self.wind_efficiency is not None else '?'} % wind efficiency")

    @staticmethod
    def from_json_dict(
            hourly_forecast_dict: Dict[str, Any],
            forecast_dict: Optional[Dict[str, Any]] = None,
            position: Optional[Position] = None):
        if forecast_dict is None:
            current_forecast = dict()
        else:
            current_forecast = forecast_dict.get('current', dict())

        return SingleForecast(
            cloudiness=hourly_forecast_dict.get('clouds', None),
            wind_speed=hourly_forecast_dict.get('wind_speed', None),
            wind_gust=hourly_forecast_dict.get('wind_gust', None),
            sunrise=current_forecast.get('sunrise', None),
            sunset=current_forecast.get('sunset', None),
            unix_timestamp=hourly_forecast_dict.get('dt', None),
            position=position
        )


class OpenWeatherMapForecast(object):
    def __init__(self, hourly: Optional[List[SingleForecast]] = None, position: Optional[Position] = None):
        if hourly is None:
            hourly = []
        self.hourly: List[SingleForecast] = hourly
        self.position = position

    def limit_to_time_range(self,
                            lower: Optional[int],
                            upper: Optional[int],
                            lower_inclusive: bool = True,
                            upper_inclusive: bool = False) -> None:
        previous_hourly_len = len(self.hourly)
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

        new_hourly_len = len(self.hourly)
        logger.debug(f'kept {new_hourly_len} of {previous_hourly_len} hourly forecasts')

    def __str__(self) -> str:
        return f"{len(self.hourly)} Hours\n" + "\n".join([forecast.__str__() for forecast in self.hourly])

    # @staticmethod
    # def from_json_dict(dic: Dict[str, Any]):
    #     return OpenWeatherMapForecast(
    #         hourly=[SingleForecast.from_json_dict(hourly_forecast_dict) for hourly_forecast_dict in
    #                 dic.get('hourly', [])]
    #     )

    @staticmethod
    def from_json_dicts(forecast_dicts: List[Dict[str, Any]], position: Optional[Position] = None):
        hourly_and_forecast_dicts: List[Tuple[Dict[str, Any], Dict[str, Any]]] = \
            [
                (hourly_dict, forecast_dict)
                for forecast_dict in forecast_dicts
                for hourly_dict in forecast_dict.get('hourly', [])
            ]

        return OpenWeatherMapForecast(
            hourly=[SingleForecast.from_json_dict(hourly_forecast_dict, forecast_dict, position) for
                    hourly_forecast_dict, forecast_dict in hourly_and_forecast_dicts],
            position=position
        )


class OneCallApiResponse(object):
    def __init__(self, forecast: Optional[OpenWeatherMapForecast] = None, position: Optional[Position] = None):
        if forecast is None:
            forecast = OpenWeatherMapForecast()
        self.forecast: OpenWeatherMapForecast = forecast

        self.position = position

    def __str__(self) -> str:
        return "Forecast:\n\n" + self.forecast.__str__()

    # @staticmethod
    # def from_response(resp: requests.Response):
    #     json_response = resp.json()
    #
    #     return OneCallApiResponse(
    #         forecast=OpenWeatherMapForecast.from_json_dict(json_response)
    #     )

    @staticmethod
    def from_responses(responses: List[requests.Response], position: Optional[Position] = None):
        json_responses = [resp.json() for resp in responses]

        return OneCallApiResponse(
            forecast=OpenWeatherMapForecast.from_json_dicts(json_responses, position),
            position=position
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
    logger.debug("Requesting URL " + url)
    return requests.get(url)


def request_one_call_timemachine_api(position: Position, unix_timestamp: int) -> OneCallApiResponse:
    """
    Requests historic weather data for 24h. Maybe only works for the last 5 days, not sure...

    :param position: a position on earth
    :param unix_timestamp: a unix timestamp directly AFTER the wanted 24h forecast epoch, given in UTC
    :return: a forecast with hourly weather data
    """

    logger.info(
        f"requesting weather information for {position.__str__()} at {unix_timestamp_to_datetime_str(unix_timestamp)}")
    # Data block contains hourly historical data starting at 00:00 on the requested day and continues until 23:59 on
    # the same day (UTC time)
    unix_timestamp_yesterday = unix_timestamp - SECONDS_PER_DAY
    timestamps_to_request = [unix_timestamp_yesterday, unix_timestamp]

    urls_to_request = [ONE_CALL_TIMEMACHINE_API_URL.format(lat=position.latitude, lon=position.longitude, dt=dt) for dt
                       in
                       timestamps_to_request]

    responses: List[requests.Response] = [request_url(url) for url in urls_to_request]
    logger.info(f"requested weather information for {position.__str__()} at "
                f"{' and '.join([unix_timestamp_to_datetime_str(dt) for dt in timestamps_to_request])}")

    resp = OneCallApiResponse.from_responses(responses, position)
    resp.forecast.limit_to_time_range(
        lower=unix_timestamp_yesterday,
        upper=unix_timestamp,
        lower_inclusive=True,
        upper_inclusive=False
    )

    for hour_forecast in resp.forecast.hourly:
        hour_forecast.log_efficiency(logging.DEBUG)

    return resp


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)

    pos = Position(
        latitude=52.5041664,
        longitude=13.4119424
    )  # Berlin
    unix_time = 1647713846 - 200000

    response = request_one_call_timemachine_api(pos, unix_time)
    print(response)
