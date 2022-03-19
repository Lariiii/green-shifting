#!/usr/bin/python3

import copy
import logging
import math
import time
from datetime import datetime

from flask import Flask  # , render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from models import Position, Datacenter
from openweathermap import request_one_call_timemachine_api

BASE_URL = 'http://127.0.0.1:5000'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['firstConnect'] = False

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

socketio = SocketIO(app, cors_allowed_origins="*")

datacenters: list[Datacenter] = []
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
                    "datacenter_vm_count_0": 1000}

    datacenter = Datacenter(name=datacenter_json["name"],
                            company=datacenter_json["company"],
                            position=Position(latitude=datacenter_json["latitude"], longitude=datacenter_json["longitude"]),
                            windpower_kwh=datacenter_json["windpower_kwh"],
                            solarpower_kwh=datacenter_json["solarpower_kwh"],
                            datacenter_vm_count_0=datacenter_json["datacenter_vm_count_0"])

    global datacenters
    global data_points_length

    # Request Today
    now = datetime.today()
    now.replace(minute=0, second=0)
    unix_now = math.floor(time.mktime(now.timetuple()))

    # Call Mirko API
    environment_data = request_one_call_timemachine_api(datacenter.position, unix_now).forecast.hourly
    data_points_length = len(environment_data)
    datacenter.environment = environment_data
    datacenters.append(datacenter)


@socketio.event
def begin_datastream():
    global datacenters, data_points_length

    def get_total_vm_cap(datacenter_obj, index):
        VM_KWH_CONSUMPTION = 1
        wind_kwh = datacenter_obj.windpower_kwh * datacenter_obj.environment[index].wind_efficiency
        solar_kwh = datacenter_obj.solarpower_kwh * datacenter_obj.environment[index].solar_efficiency

        return math.floor((wind_kwh + solar_kwh) / VM_KWH_CONSUMPTION)

    for i in range(data_points_length - 3):
        time.sleep(1)

        # Prep the data objects
        algo_input = []
        for datacenter in datacenters:
            prepped_datacenter = copy.deepcopy(datacenter)
            prepped_datacenter.datacenter_vm_count_1 = get_total_vm_cap(prepped_datacenter, i + 0)
            prepped_datacenter.datacenter_vm_count_2 = get_total_vm_cap(prepped_datacenter, i + 1)
            prepped_datacenter.datacenter_vm_count_3 = get_total_vm_cap(prepped_datacenter, i + 2)
            print(prepped_datacenter)
            algo_input.append(prepped_datacenter)

        # Call Algo
        # result = algo.predict(algo_input)

        # Mock Code to test
        mock_dc_1 = datacenters[0]
        mock_dc_1.datacenter_vm_count_0 = mock_dc_1.datacenter_vm_count_0 - 300
        mock_dc_2 = datacenters[1]
        mock_dc_2.datacenter_vm_count_0 = mock_dc_2.datacenter_vm_count_0 + 300
        mock_result = ({(mock_dc_1, mock_dc_2): 300}, [mock_dc_1, mock_dc_2])

        # Integrate back into out DB
        shift_dictionary = mock_result[0]
        changed_dcs = mock_result[1]

        # Don't Blame me for my nice code :D
        for changed_dc in changed_dcs:
            for real_dc in datacenters:
                if changed_dc.name == real_dc.name:
                    real_dc.datacenter_vm_count_0 = changed_dc.datacenter_vm_count_0

        emit('step_data', {})


if __name__ == "__main__":
    # socketio.run(app=app, host='127.0.0.1', debug=True)

    # Tests
    tc = socketio.test_client(app)
    example_datacenter_1 = {"name": "DC 1",
                            "company": "vmware",
                            "longitude": 55.2321664,
                            "latitude": 9.5155424,
                            "windpower_kwh": 2000,
                            "solarpower_kwh": 2000,
                            "datacenter_vm_count_0": 10000}
    tc.emit("create_datacenters", example_datacenter_1)

    example_datacenter_2 = {"name": "DC 2",
                            "company": "wmware",
                            "longitude": 52.5041664,
                            "latitude": 13.4119424,
                            "windpower_kwh": 2000,
                            "solarpower_kwh": 2000,
                            "datacenter_vm_count_0": 10000}
    tc.emit("create_datacenters", example_datacenter_2)


    tc.emit("begin_datastream")
    received = tc.get_received()
    print(received)
