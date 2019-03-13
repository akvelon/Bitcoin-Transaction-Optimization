"""
Copyright 2019 Akvelon Inc.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the License for the specific language governing permissions and limitations under the License.
"""
import time
import os
import pandas as pd
import numpy as np
from pathlib import Path
import tensorflow as tf
from sklearn.preprocessing import RobustScaler
from sklearn.externals import joblib
import matplotlib.pyplot as plt
from tensorflow import keras


class PredictorTrainer:
    DATA_PATH = 'data/training.csv'
    MODEL_PATH = 'data/models/'
    SCALER_PATH = 'data/models/scaler.pkl'
    TRAINED_MODEL_PATH = 'data/models/fee-predictor-model.h5'
    BATCH_SIZE = 256
    TRAIN_STEPS = 10
    TRAIN_DATA_PERCENT = 0.9

    def __init__(self, batch_size=BATCH_SIZE, train_steps=TRAIN_STEPS):
        self.initialize_scaler()

    def initialize_scaler(self):
        path = Path(PredictorTrainer.SCALER_PATH)

        if not path.is_file():
            print('Scaler model not found. Initializing.')
            #self.scaler = MinMaxScaler(feature_range=(0, 1))
            self.scaler = RobustScaler()
            data = self.load_data()
            self.scaler.fit(data.values[:, 1:])
            path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(self.scaler, PredictorTrainer.SCALER_PATH)
            print('Scaler initialized and saved.')
        else:
            print('Found scaler model. Loading.')
            self.scaler = joblib.load(PredictorTrainer.SCALER_PATH)
            print('Scaler loaded.')

    def scale_data(self, data):
        return self.scaler.transform(data)

    # splits the data onto training and test set
    def split_data(self, data, n):
        train_start = 0
        train_end = int(np.floor(0.8 * n))
        test_start = train_end + 1
        test_end = n
        return data[train_start:train_end], data[test_start:test_end]

    # loads the file with default data
    def load_file(self):
        return pd.read_csv(PredictorTrainer.DATA_PATH)

    # there are helper fields in data, this function left only ones which needed to train the model
    def get_learning_data(self, dataframe):
        return dataframe.drop(['block_median_fee_per_byte', 'block_id'], axis='columns')

    # sometimes fee_per_byte is enormous, so we take care of having the normal one here
    def filter_out_outliners(self, dataframe):
        return dataframe.query('fee_per_byte < block_median_fee_per_byte')

    # do all transformation needed to get info suitable for training
    def load_data(self):
        data = self.load_file()
        data = self.filter_out_outliners(data)
        return self.get_learning_data(data)

    def train(self):
        data = self.load_data()
        n = data.shape[0]
        data = data.values

        data_train, data_test = self.split_data(data, n)

        x_train = self.scale_data(data_train[:, 1:])
        y_train = data_train[:, 0]
        x_test = self.scale_data(data_test[:, 1:])
        y_test = data_test[:, 0]

        model = keras.Sequential([
            keras.layers.Dense(3, kernel_initializer='normal', input_dim=3),
            keras.layers.Dense(1024, kernel_initializer='normal'),
            keras.layers.PReLU(),
            keras.layers.Dropout(0.1),
            keras.layers.Dense(512, kernel_initializer='normal'),
            keras.layers.PReLU(),
            keras.layers.Dropout(0.1),
            keras.layers.Dense(256, kernel_initializer='normal'),
            keras.layers.PReLU(),
            keras.layers.Dropout(0.1),
            keras.layers.Dense(128, kernel_initializer='normal'),
            keras.layers.PReLU(),
            keras.layers.Dropout(0.1),
            keras.layers.Dense(64, kernel_initializer='normal',),
            keras.layers.PReLU(),
            keras.layers.Dropout(0.1),
            keras.layers.Dense(32, kernel_initializer='normal'),
            keras.layers.PReLU(),
            keras.layers.Dropout(0.1),
            keras.layers.Dense(1, kernel_initializer='normal')
        ])

        model.compile(optimizer='adam', 
              loss=tf.losses.huber_loss)
        model.fit(x_train, y_train, epochs=10, batch_size=250)

        model.save(PredictorTrainer.TRAINED_MODEL_PATH)

    def load_model(self, model_name):
        return keras.models.load_model(model_name, custom_objects={'huber_loss': tf.losses.huber_loss})

    def evaluate_block(self, model_name, test_file):
        model = self.load_model(model_name)
        data_raw = pd.read_csv(test_file)
        min_fee = data_raw[['fee_per_byte']].min().values[0]
        median_fee = data_raw[['block_median_fee_per_byte']].values[0][0]
        data = data_raw.query('confirmation_speed == 0')
        data = self.get_learning_data(data)
        data_y = data[:, 0]
        data_x = self.scale_data(data[:, 1:])
        predicted = model.predict(data_x).flatten()

        hit = np.where(predicted > min_fee)[0].size
        out = np.where(predicted > median_fee)[0].size
        total_good = np.where((min_fee < predicted) & (predicted < median_fee))[0].size

        print('hit', hit)
        print('out', out)
        print('total_good', total_good)

        total_fee_loss = 0
        sizes = data_raw.query('confirmation_speed == 0')[['vsize']].values.flatten()
        for i in range(0, data_y.size):
            total_fee_loss += sizes[i] * (data_y[i] - predicted[i])
        print('total_fee_loss', total_fee_loss)
        return

    # evaluates the model predictions and write down values to file for further analisys
    def evaluate(self):
        # idea is to check how well we predict fee so that transaction were added to the first block after they appear in mempool
        model = self.load_model(PredictorTrainer.TRAINED_MODEL_PATH)
        data_raw = self.load_file()
        # looking for blocks which wasn't used during training so that get legitimate result
        # the first step is get training set the same way as we did this during training session
        data = self.filter_out_outliners(data_raw)
        data_train, data_test = self.split_data(data, data.shape[0])

        data_train_blocks = set(data_train['block_id'].values.flatten()) # block ids which were used during training
        all_blocks = set(data_raw['block_id'].values.flatten()) # all block ids in our data
        block_indexes_to_evaluate = list(all_blocks.difference(data_train_blocks)) # this difference are block ids which wasn't used by training process
        data = data_raw[(data_raw['block_id'].isin(block_indexes_to_evaluate))] # filter the data which wasn't used in training so we can use it to evaluate
        data = data.query('confirmation_speed == 0') # we looking only for results where transaction were added to the first next block after it added to mempool

        #collecting the statistics
        output = pd.DataFrame(columns=['block_id', 'min_fee', 'median_fee', 'predicted_mean_fee', 'predicted_median_fee'])
        for name, group in data.groupby('block_id'):
            min_fee = group['fee_per_byte'].min()
            median_fee = group['fee_per_byte'].median()
            learning_data = self.get_learning_data(group)
            x_test = self.scale_data(learning_data.values[:, 1:])
            y_predicted = model.predict(x_test).flatten()
            predicted_mean_fee = float(np.mean(y_predicted))
            predicted_median_fee = float(np.median(y_predicted))
            output = output.append({
                'block_id': name,
                'min_fee': min_fee,
                'median_fee': median_fee,
                'predicted_mean_fee': predicted_mean_fee,
                'predicted_median_fee': predicted_median_fee
            }, ignore_index=True)

        output.to_csv(os.path.join(PredictorTrainer.MODEL_PATH, 'evaluation_output.csv'))

    def predict(self, predict, expected, model_name):
        predict_scaled = self.scale_data(predict)[:, 1:]
        sess, x, y, out = self.load_model(os.path.join(PredictorTrainer.MODEL_PATH, model_name))
        predictions = sess.run(out, feed_dict={x: predict_scaled})

        template = 'Prediction is "{}", expected "{}"\n'
        output = []
        i = 0

        for pred, expec in zip(predictions[0, :], expected):
            inversed = self.scaler.inverse_transform(np.array([[pred, predict[i][1], predict[i][2], predict[i][3]]]))
            pred = inversed[0, 0]
            print(template.format(pred, expec))
            output.append(
                {'mempool_megabytes': predict[i][1], 'mempool_tx_count': predict[i][2],
                 'confirmation_speed': predict[i][3],
                 'prediction': pred})

            i += 1

        return output
