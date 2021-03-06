#!/usr/bin/python3

import copy
import math
import time
from datetime import datetime, timedelta

from flask import Flask  # , render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from models import Position, Datacenter
from openweathermap import request_one_call_timemachine_api
from typing import List
from utils import unix_timestamp_to_datetime_str
from algorithm_test import shift

BASE_URL = 'http://0.0.0.0:5000'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['firstConnect'] = False

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

socketio = SocketIO(app, cors_allowed_origins="*")

datacenters: List[Datacenter] = []
data_points_length = 0
index = 0


@socketio.event
def disconnect():
    global datacenters, data_points_length, index

    datacenters = []
    index = 0
    data_points_length = 0

    print("Resetted internal state!")


@socketio.event
def create_datacenters(datacenter_json):
    print(datacenter_json)

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
                            position=Position(latitude=datacenter_json["latitude"],
                                              longitude=datacenter_json["longitude"]),
                            windpower_kwh=datacenter_json["windpower_kwh"],
                            solarpower_kwh=datacenter_json["solarpower_kwh"],
                            datacenter_vm_count_0=datacenter_json["datacenter_vm_count_0"])

    global datacenters
    global data_points_length

    # Request Today
    now = datetime.today()
    now.replace(minute=0, second=0)
    # noinspection PyTypeChecker
    unix_now = math.floor(time.mktime(now.timetuple()))

    yesterday = datetime.today() - timedelta(days=1)
    yesterday.replace(minute=0, second=0)
    unix_now_yesterday = math.floor(time.mktime(yesterday.timetuple()))

    # Call Mirko API
    a = request_one_call_timemachine_api(datacenter.position, unix_now)
    environment_data = a.forecast.hourly
    environment_data_yest = request_one_call_timemachine_api(datacenter.position, unix_now_yesterday).forecast.hourly

    datacenter.environment = [*environment_data_yest, *environment_data]
    datacenters.append(datacenter)
    data_points_length = len(datacenter.environment)
    if data_points_length == 0:
        print("WARNING: API probably exceeded!")

@socketio.event
def begin_datastream():
    global datacenters, data_points_length, index

    def get_total_vm_cap(datacenter_obj, index):
        VM_KWH_CONSUMPTION = 1
        wind_kwh = datacenter_obj.windpower_kwh * datacenter_obj.environment[index].wind_efficiency
        solar_kwh = datacenter_obj.solarpower_kwh * datacenter_obj.environment[index].solar_efficiency
        non_cooling_kwh = math.floor((wind_kwh + solar_kwh) / 2.65)

        print("{}: S: {} => {}, W: {} => {}".format(datacenter_obj.name,
                                                    solar_kwh,
                                                    datacenter_obj.environment[index].solar_efficiency,
                                                    wind_kwh,
                                                    datacenter_obj.environment[index].wind_efficiency))

        # noinspection PyTypeChecker
        return math.floor(non_cooling_kwh / VM_KWH_CONSUMPTION)

    if index + 2 >= len(datacenters[0].environment):
        index = 0

    timestamp = unix_timestamp_to_datetime_str(datacenters[0].environment[index].unix_timestamp)
    time.sleep(1)
    print("\n--- New Hour {} ---".format(timestamp))

    # Prep the data objects
    algo_input = []
    for datacenter in datacenters:
        prepped_datacenter = copy.deepcopy(datacenter)
        prepped_datacenter.datacenter_vm_count_1 = get_total_vm_cap(prepped_datacenter, index + 0)
        prepped_datacenter.datacenter_vm_count_2 = get_total_vm_cap(prepped_datacenter, index + 1)
        prepped_datacenter.datacenter_vm_count_3 = get_total_vm_cap(prepped_datacenter, index + 2)
        print(prepped_datacenter)
        algo_input.append(prepped_datacenter)

    # Call Algo
    result = shift(algo_input)

    # Integrate back into out DB
    shift_dictionary = result[0]
    changed_dcs = result[1]

    # Don't Blame me for my nice code :D
    for changed_dc in changed_dcs:
        for real_dc in datacenters:
            if changed_dc.name == real_dc.name:
                real_dc.datacenter_vm_count_0 = changed_dc.datacenter_vm_count_0

    # Create JSON to send
    to_send_json = {"shifts": [], "datacenters": {}, "unix_timestamp": timestamp}
    for shift_tuple, value in shift_dictionary.items():
        to_send_json["shifts"].append({"from": shift_tuple[0].name, "to": shift_tuple[1].name, "value": value})
        print("Shifted {} VMs from {} to {}".format(value, shift_tuple[0].name, shift_tuple[1].name))
    for dc in datacenters:
        to_send_json["datacenters"][dc.name] = dc.datacenter_vm_count_0

    index += 1
    emit('step_data', to_send_json)


if __name__ == "__main__":
    socketio.run(app=app, host='0.0.0.0', debug=True)

    # Tests
    # tc = socketio.test_client(app)
    # example_datacenter_1 = {"name": "DC 1",
    #                         "company": "vmware",
    #                         "longitude": 151.085414,
    #                         "latitude": -33.882755,
    #                         "windpower_kwh": 2000,
    #                         "solarpower_kwh": 2000,
    #                         "datacenter_vm_count_0": 2000}
    # tc.emit("create_datacenters", example_datacenter_1)
    #
    # example_datacenter_2 = {"name": "DC 2",
    #                         "company": "wmware",
    #                         "longitude": -22.746257,
    #                         "latitude": -43.387096,
    #                         "windpower_kwh": 2000,
    #                         "solarpower_kwh": 2000,
    #                         "datacenter_vm_count_0": 100}
    # tc.emit("create_datacenters", example_datacenter_2)
    #
    #
    # tc.emit("begin_datastream")
    # received = tc.get_received()
    # print("")
    # print(received)
