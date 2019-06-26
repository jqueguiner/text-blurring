import decimal
from flask import Flask
from flask import request
from tempfile import mkdtemp
from werkzeug import serving
import os
import requests
import ssl
from werkzeug.utils import secure_filename
from flask import jsonify
import random
import string
import json
from uuid import uuid4
import sys
import random

from flask import send_file
from text_detection import detect_text
import traceback
import cv2

try:  # Python 3.5+
    from http import HTTPStatus
except ImportError:
    try:  # Python 3
        from http import client as HTTPStatus
    except ImportError:  # Python 2
        import httplib as HTTPStatus


app = Flask(__name__)


def get_model_bin(url, output_path):
    if not os.path.exists(output_path):
        cmd = "wget -O %s %s" % (output_path, url)
        os.system(cmd)
    return output_path

def download(url, filename):
    data = requests.get(url).content
    with open(filename, 'wb') as handler:
        handler.write(data)

    return filename


def generate_random_filename(extension):
    filename = str(uuid4())
    filename = os.path.join(upload_directory, filename + "." + extension)
    return filename


def clean_me(filename):
    if os.path.exists(filename):
        os.remove(filename)


def clean_all(files):
    for me in files:
        clean_me(me)


# define a predict function as an endpoint 
@app.route("/process", methods=["POST"])
def process():
    
    input_path = generate_random_filename("jpg")
    output_path = generate_random_filename("jpg")

    try:
        url = request.json["url"]
        strength = request.json["strength"]
   
        download(url, input_path)

        detect_text(
            input_path=input_path, 
            output_path=output_path, 
            net=net,
            width=320, 
            height=320, 
            min_confidence=0.5, 
            blur=True, 
            strength=25,
            sigma=30,
            bounding_box=False
        )

        callback = send_file(output_path, mimetype='image/jpeg')

        return callback, 200

    except:
        traceback.print_exc()
        return {'message': 'input error'}, 400

    finally:
        clean_all([
            input_path,
            output_path
            ])

if __name__ == '__main__':
    global upload_directory, model, net
    
    upload_directory = 'upload'

    if not os.path.exists(upload_directory):
        os.makedirs(upload_directory)

    model_name = "frozen_east_text_detection.pb"
    model_url = "https://storage.gra5.cloud.ovh.net/v1/AUTH_18b62333a540498882ff446ab602528b/pretrained-models/" + model_name

    get_model_bin(model_url , model_name)

    net = cv2.dnn.readNet(model_name)

    port = 5000
    host = '0.0.0.0'

    app.run(host=host, port=port, threaded=True)

