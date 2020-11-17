import cv2
import numpy as np
import time
import logging
import traceback
import os
import io
import requests
import random
import json
from time import gmtime, strftime

from flask import Flask, render_template, Response, request, jsonify

from utils.parser import get_config
from utils.utils import load_class_names, get_image

import cv2
import numpy as np

# create backup dir
if not os.path.exists('backup'):
    os.mkdir('backup')

# create json dir
if not os.path.exists('json_dir'):
    os.mkdir('json_dir')

# setup config
cfg = get_config()
cfg.merge_from_file('configs/service.yaml')

# create log_file, rcode
TASK1_URL = cfg.SERVICE.TASK1_URL
TASK2_URL = cfg.SERVICE.TASK2_URL
TASK3_URL = cfg.SERVICE.TASK3_URL
LOG_PATH = cfg.SERVICE.LOG_PATH
BACKUP = cfg.SERVICE.BACKUP_DIR
HOST = cfg.SERVICE.SERVICE_IP
PORT = cfg.SERVICE.SERVICE_PORT

if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)
logging.basicConfig(filename=os.path.join(LOG_PATH, str(time.time())+".log"), filemode="w", level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
logging.getLogger("").addHandler(console)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates', static_folder='static')


@app.route('/receipt')
def hello_world():
    return render_template('index.html')


@app.route('/')
def index():
    return render_template('home.html')


@app.route("/predict", methods=['POST'])
def predict():
    if request.method == 'POST':
        file = request.files['file']
        image_file = file.read()
        img = cv2.imdecode(np.frombuffer(image_file, dtype=np.uint8), -1)

        print('Original Dimensions : ', img.shape)
        scale_percent = 100
        if img.shape[0] > 3000:
            scale_percent = 20
        elif img.shape[0] > 2000:
            scale_percent = 40  # percent of original size
        if scale_percent < 50:
            width = int(img.shape[1] * scale_percent / 100)
            height = int(img.shape[0] * scale_percent / 100)
            dim = (width, height)
            print(dim)
            # resize image
            img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

        # save image
        time = strftime("%Y-%m-%d_%H:%M:%S", gmtime())
        number = str(random.randint(0, 10000))
        img_name = time + '_' + number + '.jpg'
        img_path = os.path.join(BACKUP, img_name)
        cv2.imwrite(img_path, img)
        detect_task1 = requests.post(TASK1_URL, files={"file": (
            "filename", open(img_path, "rb"), "image/jpeg")}).json()
        detect_task1_txt = str(detect_task1)
        files = [
            ("file", ("filename", open(img_path, "rb"), "image/jpeg")),
            ('data', ('data', json.dumps(detect_task1), 'application/json')),
        ]

        detect_task2 = requests.post(TASK2_URL, files=files).json()
        detect_task2_txt = str(detect_task2)

        return detect_task2_txt


@app.route('/show_img/<path:image_path>', methods=['GET'])
def visualize(image_path):
    try:
        image_path = os.path.join(BACKUP, image_path)
    except Exception as e:
        print(str(e))
        print(str(traceback.print_exc()))
        result = {'code': '609', 'status': RCODE.code_609}
    return Response(get_image(image_path), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
