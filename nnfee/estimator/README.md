# estimator

## install

```
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

## commands

Training is done from [fee_training.csv](csv/fee_training.csv) and [fee_test.csv](csv/fee_test.csv).

The training model is saved to the folder `models`, make sure not to overtrain
your model.

To train it:

```
python cli.py --train
```

To predict using the model:

```
python cli.py --predict '[2.63,9.66]'
```
