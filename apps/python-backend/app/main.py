#!/usr/bin/python3
"""
aircontrol ewfs blinds api
Control your Warema EWFS blinds via 433.92 MHz protocol and aircontrol backend
See: https://github.com/rfkd/aircontrol
"""
import os
import glob
import logging
from os import path
from io import BytesIO

from flask import Flask, send_from_directory #, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit

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



@app.route(f"/{ IMAGE_DIRECTORY }/<path:path>")
def serve_images(path):
    return send_from_directory(IMAGE_DIRECTORY, path)

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/enpoint/<int:id>', methods=['POST'])
# def endpoint(id):
#     return ('', 200)

# @socketio.on('message')
# def handle_message(data):
#     print('received message: ' + data)

# @socketio.on('json')
# def handle_json(json):
#     print('received json: ' + str(json))


@socketio.event
def get_cameras(json):
    cameras = gp.Camera.autodetect()
    cameras_json = { name: value for (name, value) in cameras }
    emit('cameras', cameras_json, broadcast=True)

@socketio.event
def get_latest_images(json):
    count = json['count']
    list_of_files = glob.glob(f"{ IMAGE_DIRECTORY }/*.jpg")
    sorted_list = sorted(list_of_files, key=os.path.getctime, reverse=True)[:count]
    urls = [ path.join(BASE_URL, target) for target in sorted_list ]
    emit('latest_images', urls, broadcast=True)
    return urls

@socketio.event
def capture():
    try:
        camera = gp.Camera()
        camera.init()

        # Capture image
        file_path = camera.capture(gp.GP_CAPTURE_IMAGE)

        # Creating file name 
        target = path.join(IMAGE_DIRECTORY, file_path.name.lower())
        
        # Loading image from camera and shrinking to IMAGE_SIZE 
        camera_file = camera.file_get(file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
        with BytesIO(camera_file.get_data_and_size()) as file:
            img = Image.open(file)
            img.thumbnail(size=(IMAGE_SIZE, IMAGE_SIZE))
            transposed_img = ImageOps.exif_transpose(img)
            transposed_img.save(target)

        # Emit new image url
        emit('new_image', path.join(BASE_URL, target), broadcast=True)
        
        camera.exit()
    except Exception as e:
        emit('error', f"Capturing failed: { e }")
        logger.exception(f"Capturing failed: { e }")


if __name__ == "__main__":

    socketio.run(app=app, host='127.0.0.1', debug=True)