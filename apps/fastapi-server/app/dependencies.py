import copy
from datetime import datetime, time
import json
import logging
import os
from fastapi import status
from fastapi.exceptions import HTTPException
from models import Cycle, Machine, Plant, Edgedevice, Incident, Camera, SensorEdgeAssociation, SensorDatatype, Sensor, User, Notification, Comment, CameraConfiguration
import pika
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker

POSTGRES_HOST = os.environ['POSTGRES_HOST']
POSTGRES_USER = os.environ['POSTGRES_USER']
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
POSTGRES_PORT = os.environ['POSTGRES_PORT']
POSTGRES_DB = os.environ['POSTGRES_DB']

RABBITMQ_HOST = os.environ['RABBITMQ_HOST']
RABBITMQ_DEFAULT_USER = os.environ['RABBITMQ_USERNAME']
RABBITMQ_DEFAULT_PASS = os.environ['RABBITMQ_PASSWORD']

rabbitmq_connections_params = pika.ConnectionParameters(host=RABBITMQ_HOST,
                                                        credentials=pika.PlainCredentials(RABBITMQ_DEFAULT_USER,
                                                                                          RABBITMQ_DEFAULT_PASS))

engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB))
session_maker = sessionmaker(bind=engine)
session = session_maker()

# RabbitMQ
connection = pika.BlockingConnection(parameters=rabbitmq_connections_params)
channel = connection.channel()

apiLogger = logging.getLogger("api")


class MESSAGES:
    START_CAPTURE = "start_capture"
    STOP_CAPTURE = "stop_capture"
    TRIGGER = "trigger"
    START_LIVESTREAM = "start_livestream"
    STOP_LIVESTREAM = "stop_livestream"
    INIT_CAMERAS = "init_cameras"
    START_CAMERAS = "start_cameras"
    FINISHED_CONFIG = "finished_config"
    DELETE_MACHINE = "delete_machine"
    DELETE_DEVICE = "delete_device"
    GRACEFUL_SHUTDOWN = "graceful_shutdown"
    CHANGE_FIXED_CYCLE_LENGTH = "change_fixed_cycle_length"
    CHANGE_CYCLE_MODE = "change_cycle_mode"
    GET_CYCLE_VIDEO = "get_cycle_video"
    START_SENSOR_LIVESTREAM = "start_sensor_livestream"
    STOP_SENSOR_LIVESTREAM = "stop_sensor_livestream"
    UPDATE_OPERATIONAL_TIME = "update_operational_time"
    INIT_SENSORS = "init_sensors"
    ANALYSE_IODD_START_MANAGERS = "analyse_iodd_start_managers"
    UPDATE_CAMERA_CONFIG = "update_camera_config"

    START_MANUAL_CYCLE = "manuel_cycle_start"
    END_MANUAL_CYCLE = "manuel_cycle_end"
    NEXT_MANUAL_CYCLE = "manuel_cycle_next"



def get_task_queue_name(vihub_key):
    return "vihub_{}".format(vihub_key)


def execute_query(query, values=None, has_results=True):
    with engine.connect() as conn:
        if values is not None:
            results = conn.execute(query, values)
        else:
            results = conn.execute(query)

    if has_results:
        cursor = results.cursor
        columns = [x.name for x in cursor.description]
        r = []
        for row in cursor.fetchall():
            r.append(dict(zip(columns, row)))
        return r


def send_message_to_queue(vihub_key, data_dir):
    connection = pika.BlockingConnection(parameters=rabbitmq_connections_params)
    channel = connection.channel()
    channel.basic_publish(
        exchange='',
        routing_key=get_task_queue_name(vihub_key),
        body=bytes(json.dumps(data_dir), "utf-8"),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))
    channel.close()


def verify_types(row_dict: dict):
    for key, value in row_dict.items():
        parsed_value = None
        if isinstance(value, datetime):
            value: datetime
            parsed_value = value.strftime("%d.%m.%Y %H:%M:%S")
        if isinstance(value, time):
            value: time
            parsed_value = value.strftime("%H:%M:%S")
        if parsed_value is not None:
            row_dict[key] = parsed_value
    return row_dict


def parse_sql_alc_with_single_object(query_result):
    query_result_copy = copy.deepcopy(query_result)
    if query_result_copy is None:
        print("Encountered None from SQL Alch Result")
    elif type(query_result_copy) == list:
        if len(query_result_copy) > 0:
            result_list = []
            for row in query_result_copy:
                row_dict = row.__dict__
                if "_sa_instance_state" in row_dict:
                    del row_dict["_sa_instance_state"]
                row_dict = verify_types(row_dict)
                result_list.append(row_dict)
            return result_list
        else:
            return None
    else:
        # Returning the object dict
        #_ = query_result.id
        row_dict = query_result.__dict__
        if "_sa_instance_state" in row_dict.keys():
            del row_dict["_sa_instance_state"]
        row_dict = verify_types(row_dict)
        return query_result.__dict__


def parse_sql_alc_with_col_names(query_result, col_names):
    query_result_copy = copy.deepcopy(query_result)
    if query_result_copy is None:
        print("Encountered None from SQL Alch Result")
    elif type(query_result_copy) == list:
        if len(query_result_copy) > 0:
            result_list = []
            for row in query_result_copy:
                res_dict = {}
                for i, value in enumerate(row):
                    res_dict[col_names[i]] = value
                result_list.append(res_dict)
            return result_list
        else:
            return None
    else:
        res_dict = {}
        for i, value in enumerate(query_result_copy):
            res_dict[col_names[i]] = value
        return res_dict


def parse_sql_alc_with_object_names(query_result, object_names):
    query_result_copy = copy.deepcopy(query_result)
    if query_result_copy is None:
        print("Encountered None from SQL Alch Result")
    elif type(query_result_copy) == list:
        if len(query_result_copy) > 0:
            result_list = []
            for row in query_result_copy:
                res_dict = {}
                for i, db_object in enumerate(row):
                    db_object_dict = db_object.__dict__
                    if "_sa_instance_state" in db_object_dict:
                        del db_object_dict["_sa_instance_state"]
                    res_dict[object_names[i]] = db_object_dict
                result_list.append(res_dict)
            return result_list
    return None


def get_sqlalch_session():
    return session


class WorkspaceValidation:
    def __init__(self, user_workspace_id, vihub_key=None, plant_id=None, machine_id=None, cycle_id=None,
                 incident_id=None, camera_id=None, sensor_edge_id=None, datatype_id=None, sensor_id=None,
                 user_id=None, notification_id=None, comment_id=None, config_id=None):
        self.vihub_key = vihub_key
        self.plant_id = plant_id
        self.machine_id = machine_id
        self.cycle_id = cycle_id
        self.incident_id = incident_id
        self.user_workspace_id = user_workspace_id
        self.camera_id = camera_id
        self.sensor_edge_id = sensor_edge_id
        self.datatype_id = datatype_id
        self.sensor_id = sensor_id
        self.user_id = user_id
        self.notification_id = notification_id
        self.comment_id = comment_id
        self.config_id = config_id

    def validate(self):
        credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate workspace credentials",
                headers={"WWW-Authenticate": "Bearer"},
        )

        session = get_sqlalch_session()

        if self.plant_id is not None:
            plant_result = session.query(Plant).filter(Plant.id == self.plant_id)
            if plant_result.one().workspace_id != self.user_workspace_id:
                raise credentials_exception

        if self.machine_id is not None:
            machine_result = session.query(Plant).join(Machine, Plant.id == Machine.plant_id)\
                .filter(Machine.id == self.machine_id)
            if machine_result.one().workspace_id != self.user_workspace_id:
                raise credentials_exception

        if self.cycle_id is not None:
            cycle_result = session.query(Plant).join(Machine, Plant.id == Machine.plant_id)\
                .join(Cycle, Machine.id == Cycle.machine_id)\
                .filter(Cycle.id == self.cycle_id)
            if cycle_result.one().workspace_id != self.user_workspace_id:
                raise credentials_exception

        if self.incident_id is not None:
            incident_result = session.query(Plant).join(Machine, Plant.id == Machine.plant_id)\
                .join(Incident, Machine.id == Incident.machine_id)\
                .filter(Incident.id == self.incident_id)
            if incident_result.one().workspace_id != self.user_workspace_id:
                raise credentials_exception

        if self.vihub_key is not None:
            hub_result = session.query(Edgedevice).filter(Edgedevice.vihub_key == self.vihub_key)
            if hub_result.one().workspace_id != self.user_workspace_id:
                raise credentials_exception

        if self.camera_id is not None:
            camera_result = session.query(Edgedevice).join(Camera, Edgedevice.vihub_key == Camera.vihub_key)\
                .filter(Camera.id == self.camera_id)
            if camera_result.one().workspace_id != self.user_workspace_id:
                raise credentials_exception

        if self.sensor_edge_id is not None:
            sensor_edge_id_result = session.query(Edgedevice)\
                .join(SensorEdgeAssociation, Edgedevice.vihub_key == SensorEdgeAssociation.vihub_key)\
                .filter(SensorEdgeAssociation.id == self.sensor_edge_id)
            if sensor_edge_id_result.one().workspace_id != self.user_workspace_id:
                raise credentials_exception

        if self.sensor_id is not None:
            sensor_id_result = session.query(Edgedevice)\
                .join(SensorEdgeAssociation, Edgedevice.vihub_key == SensorEdgeAssociation.vihub_key)\
                .join(Sensor, Sensor.id == SensorEdgeAssociation.sensor_id).filter(Sensor.id == self.sensor_id)
            contains_workspace = False
            for sensor_row in sensor_id_result.all():
                if sensor_row.workspace_id == self.user_workspace_id:
                    contains_workspace = True
                    break
            if not contains_workspace:
                raise credentials_exception

        if self.datatype_id is not None:
            datatype_id_result = session.query(Edgedevice).join(SensorEdgeAssociation, Edgedevice.vihub_key == SensorEdgeAssociation.vihub_key)\
                .join(SensorDatatype, SensorDatatype.sensor_edge_id == SensorEdgeAssociation.id).filter(SensorDatatype.id == self.datatype_id)
            if datatype_id_result.one().workspace_id != self.user_workspace_id:
                raise credentials_exception

        if self.user_id is not None:
            user_result = session.query(User).filter(User.id == self.user_id)
            if user_result.one().workspace_id != self.user_workspace_id:
                raise credentials_exception

        if self.notification_id is not None:
            notification_result = session.query(User).join(Notification, User.id == Notification.user_id).filter(Notification.id == self.notification_id)
            if notification_result.one().workspace_id != self.user_workspace_id:
                raise credentials_exception

        if self.comment_id is not None:
            comment_result = session.query(User).join(Comment, User.id == Comment.user_id).filter(Comment.id == self.comment_id)
            if comment_result.one().workspace_id != self.user_workspace_id:
                raise credentials_exception

        if self.config_id is not None:
            config_result = session.query(Edgedevice).join(Camera, Edgedevice.vihub_key == Camera.vihub_key)\
                .join(CameraConfiguration, Camera.id == CameraConfiguration.camera_id).filter(CameraConfiguration.id == self.config_id)
            if config_result.one().workspace_id != self.user_workspace_id:
                raise credentials_exception

        return None
