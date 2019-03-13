from settings import Settings
import tensorflow as tf
import numpy as np
import requests
import time
import math
from sklearn.externals import joblib
import json

class Predictor:
    URL = "https://dedi.jochen-hoenicke.de/queue/db.php"
    TWO_UNIX_MINS = 60 * 2
    MEMPOOL_TIME = 0
    MEMPOOL_TX_COUNT_INDEX = 1
    MEMPOOL_SIZE_INDEX = 2
    MEMPOOL_FEE_INDEX = 3

    def __init__(self):
        self.settings = Settings()
        model_path = self.settings[Settings.MODEL_PATH]

        self.scaler = joblib.load(self.settings[Settings.SCALER_PATH])
        print('Scaler loaded')

        self.model = tf.keras.models.load_model(model_path, custom_objects={'huber_loss': tf.losses.huber_loss})
        self.graph = tf.get_default_graph()
        print('Model loaded')

    def predict(self, time_class):
        fee_change_speed, mempool_size = self.get_mempool_stats()
        model_input = self.scaler.transform([[mempool_size, time_class, fee_change_speed]])
        with self.graph.as_default(): # https://github.com/keras-team/keras/issues/2397
            return float(self.model.predict(model_input).flatten()[0])

    def get_mempool_stats(self):
        current_time = math.floor(time.time())
        start_time = current_time - Predictor.TWO_UNIX_MINS
        payload = {'s': start_time, 'e': current_time, 'i': 1}
        r = requests.get(Predictor.URL, params=payload)
        response = r.text[len("call("): -len(");\n")]
        m1, m2 = json.loads(response)[:2] #we expect only two items here, but do slice just in case there are three..
        m1_fee_total = sum(m1[Predictor.MEMPOOL_FEE_INDEX])
        m2_fee_total = sum(m2[Predictor.MEMPOOL_FEE_INDEX])
        m2_size_total = sum(m2[Predictor.MEMPOOL_SIZE_INDEX])
        fee_change_speed = (m2_fee_total - m1_fee_total) / (m2[Predictor.MEMPOOL_TIME] - m1[Predictor.MEMPOOL_TIME])
        if (fee_change_speed < 0):
            fee_change_speed = 1000 # we need to actually calculate or estimate but currently leaving just SWAG value.
        return fee_change_speed, m2_size_total
