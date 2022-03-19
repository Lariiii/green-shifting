#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from pprint import pprint
from models import Position
from typing import Any, Dict

# belongs to Mirko - should be deleted later
API_KEY = "720ad709ee32204a850f50794813a928"

BASE_URL = "https://api.openweathermap.org/data/2.5"
ONE_CALL_API_URL = f"{BASE_URL}/onecall?lat={{lat}}&lon={{lon}}&exclude=alerts,minutely,daily&appid={API_KEY}"
ONE_CALL_TIMEMACHINE_API_URL = f"{BASE_URL}/onecall/timemachine?lat={{lat}}&lon={{lon}}&dt={{dt}}&appid={API_KEY}"


class OneCallApiResponse:
    def __init__(self):
        pass


# def request_one_call_api(pos: Position) -> OneCallApiResponse:
#     url = ONE_CALL_API_URL.format(lat=pos.latitude, lon=pos.longitude)
#     print(f"requesting {url}")
#     resp: Dict[str, Any] = requests.get(url).json()
#     pprint(resp)
#
#     return OneCallApiResponse()

def request_one_call_timemachine_api(pos: Position, unix_timestamp: int) -> OneCallApiResponse:
    """
    requests historic weather data for one day

    :param pos: a position on earth
    :param unix_timestamp: the unix timestamp AFTER the wanted epoch
    :return: hourly weather data
    """
    url = ONE_CALL_API_URL.format(lat=pos.latitude, lon=pos.longitude, dt=unix_timestamp)
    print(f"requesting {url}")
    resp: Dict[str, Any] = requests.get(url).json()
    pprint(resp)

    return OneCallApiResponse()


if __name__ == '__main__':
    position = Position(
        latitude=52.5041664,
        longitude=13.4119424
    )  # Berlin
    response = request_one_call_timemachine_api(position)
    print(response)
