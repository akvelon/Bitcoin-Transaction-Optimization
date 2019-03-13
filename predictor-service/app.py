"""
Copyright 2019 Akvelon Inc.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the License for the specific language governing permissions and limitations under the License.
"""
#!flask/bin/python
from flask import Flask, jsonify, make_response
from predictor import Predictor

app = Flask(__name__)
predictor = Predictor()

@app.route('/api/v1.0/prediction/<int:prediction_class>')
def get_prediction(prediction_class):
    predicted = predictor.predict(prediction_class)
    return jsonify({'recommend_fee': predicted})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True)
