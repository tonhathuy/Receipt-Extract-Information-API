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
logging.basicConfig(filename=os.path.join(LOG_PATH, str(time.time())+".log"), filemode="w", level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
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


        print('Original Dimensions : ',img.shape)
        if img.shape[0] > 3000:
            scale_percent = 20
        elif img.shape[0] > 2000:
            scale_percent = 40 # percent of original size
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        print(dim)
        # resize image
        image = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)


        # save image
        time = strftime("%Y-%m-%d_%H:%M:%S", gmtime())
        number = str(random.randint(0, 10000))
        img_name = time + '_' + number + '.jpg'
        img_path = os.path.join(BACKUP, img_name)
        cv2.imwrite(img_path, image)

        return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
