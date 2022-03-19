#!/usr/bin/python3
"""
aircontrol ewfs blinds api
Control your Warema EWFS blinds via 433.92 MHz protocol and aircontrol backend
See: https://github.com/rfkd/aircontrol
"""
import math
import os
import glob
import logging
import time
from datetime import datetime, date, timedelta
from os import path
from io import BytesIO

from flask import Flask, send_from_directory, request  # , render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from models import Position
from openweathermap import request_one_call_timemachine_api

import gphoto2 as gp
from PIL import Image, ImageOps

BASE_URL = 'http://127.0.0.1:5000'
IMAGE_DIRECTORY = 'tmp'
IMAGE_SIZE = 1000

logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
gp.check_result(gp.use_python_logging())

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['firstConnect'] = False

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

socketio = SocketIO(app, cors_allowed_origins="*")

datacenters = []
data_points_length = 0


@socketio.event
def create_datacenters(datacenter_json):
    # JSON Format
    example_json = {"name": "",
                    "company": "",
                    "longitude": 0,
                    "latitude": 0,
                    "windpower_kwh": 0,
                    "solarpower_kwh": 0,
                    "datacenter_vm_count": 1000}

    print(datacenter_json)
    global datacenters
    global data_points_length

    # Request Today
    now = datetime.today()
    now.replace(minute=0, second=0)
    unix_now = math.floor(time.mktime(now.timetuple()))

    # Call Mirko API
    position = Position(
        latitude=datacenter_json["latitude"],
        longitude=datacenter_json["longitude"])
    environment_data = request_one_call_timemachine_api(position, unix_now).forecast.hourly
    data_points_length = len(environment_data)
    datacenter_json["environment_data"] = environment_data
    datacenters.append(datacenter_json)

@socketio.event
def begin_datastream():
    global datacenters, data_points_length

    for i in range(data_points_length):
        time.sleep(1)

        # Prep the data objects
        for datacenter in datacenters:
            mini_datacenter = []

        # Call Algo








@socketio.event
def end_datastream(datacenter_json):
    # TODO
    pass


if __name__ == "__main__":
    socketio.run(app=app, host='127.0.0.1', debug=True)
