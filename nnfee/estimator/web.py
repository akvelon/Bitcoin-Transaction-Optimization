from classifier import FeeClassifier
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def root():
    return app.send_static_file('index.html')

@app.route("/nn")
@app.route("/nn/<int:fee_per_byte>")
@app.route("/nn/<int:fee_per_byte>/<int:mempool_megabytes>")
@app.route("/nn/<int:fee_per_byte>/<int:mempool_megabytes>/<int:mempool_tx_count>")
def predict(fee_per_byte=1, mempool_megabytes=10, mempool_tx_count=10):
    output = FeeClassifier().predict([[fee_per_byte, mempool_megabytes, mempool_tx_count]], ['?'])
    return jsonify({ 'result': output[0] })
