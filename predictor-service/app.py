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
