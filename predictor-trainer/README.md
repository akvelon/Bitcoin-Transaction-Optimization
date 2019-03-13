# Predictor trainer
Trainer for fee prediction model

``TODO:`` Review model features and change model architecture 

## Requirements

* Python 3.6.*
* All packages from ``requirements.txt``
* CSV file with training data in ``data/training.csv``(currently we using collector from https://github.com/mess110/nnfee)

## Run
* Train model
```bash
python cli.py --train
```
Directory with model and ``scaler.pkl`` will be saved in ``model/`` directory and can be used by ``predictor-service``
* Evaluate model
```bash
python cli.py --evaluate model_name
```
``model_name`` from ``model/`` directory

Example: ``python cli.py --evaluate 20190125-131755``

* Predict fee (WIP: parameters can be changed in cli.py)

```bash
python cli.py --predict
```