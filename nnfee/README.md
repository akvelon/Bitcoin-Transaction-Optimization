# nnfee

Attempt to estimate bitcoin fees with neural networks

## components

* [collector](collector/) - prepares data for training/testing
* [estimator](estimator/) - trains/tests/clients

## usage

Easiest way to run this is with docker:

Open [http://localhost:5000/](http://localhost:5000/) for the web interface

```shell
./collect


// once you have blocks you can prepare for training
// this will create training/testing files and move them in the
// correct directory

./prepare


// train the NN

./nn --train'


// make prediction. the first element in the array is the fee per byte the other
// is the current mempool size

./nn --predict '[2.63,9.66]'
```

## helper commands

```
// evaluates the model, is automatically run after training

./nn --evaluate

// deletes the model to start fresh

./nn --clean
```



## thanks

* https://jochen-hoenicke.de/queue/#1,24h
* https://www.smartbit.com.au/
