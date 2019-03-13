from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from classifier import data_loading
import tensorflow as tf


class FeeClassifier:
    MODELS_DIR = os.getenv('MODELS_DIR', 'data/models/')
    BATCH_SIZE = 100
    TRAIN_STEPS = 1000

    def __init__(self, batch_size=BATCH_SIZE, train_steps=TRAIN_STEPS):
        self.batch_size = batch_size
        self.train_steps = train_steps
        # print(self.batch_size)
        self.feature_column_names = []

        self.train_path = '/train/201802_training.csv'
        self.test_path = '/train/201802_test.csv'

        my_feature_columns = []
        for key in data_loading.load_train_keys(self.test_path):
            feature_column = tf.feature_column.numeric_column(key=key)
            my_feature_columns.append(feature_column)
            self.feature_column_names.append(feature_column.name)

        # print(self.MODELS_DIR)

        # Build 2 hidden layer DNN with 10, 10 units respectively.
        self.classifier = tf.estimator.DNNClassifier(
            feature_columns=my_feature_columns,
            # Two hidden layers of 10 nodes each.
            hidden_units=[100, 100],
            # The model must choose between 3 classes.
            n_classes=8,
            model_dir=FeeClassifier.MODELS_DIR)

    def train(self):
        train_x, train_y = data_loading.load_training_data(self.train_path)

        # Train the Model.
        self.classifier.train(
            input_fn=lambda: data_loading.train_input_fn(train_x, train_y,
                                                          self.batch_size),
            steps=self.train_steps)

    def evaluate(self):
        test_x, test_y = data_loading.load_test_data(self.test_path)

        # Evaluate the model.
        eval_result = self.classifier.evaluate(
            input_fn=lambda: data_loading.eval_input_fn(test_x, test_y,
                                                         self.batch_size))

        print('Test set accuracy: {accuracy:0.3f}\n'.format(**eval_result))

    def predict(self, predict, expected):
        predict_x = {}

        # format to expected predict format
        index = -1
        for key in self.feature_column_names:
            index += 1
            new_array = []
            for elem in predict:
                new_array.append(elem[index])
            predict_x[key] = new_array
        # print(predict_x)

        # TODO: is this good?
        def input_fn():
            return data_loading.eval_input_fn(predict_x, labels=None,
                                               batch_size=self.batch_size)

        predictions = self.classifier.predict(input_fn=input_fn)

        template = ('Prediction is "{}" ({:.1f}%), expected "{}"\n')

        output = []
        i = 0
        for pred_dict, expec in zip(predictions, expected):
            class_id = pred_dict['class_ids'][0]
            probability = pred_dict['probabilities'][class_id]

            print(template.format(class_id, 100 * probability, expec))
            output.append({ 'fee_per_byte': predict[i][0], 'mempool_megabytes': predict[i][1], 'mempool_tx_count': predict[i][2], 'prediction': class_id.item(), 'confidence': (100 * probability).item() })
            i += 1

        return output
