# Fee predictor service
This is service which serves the only purpose - supply the Transaction Optimizer with the predicted fee per byte so that transaction was confirmed by blockchain within specified time class.

It have the only endpoint which is `<server-location>/api/v1.0/prediction/<int:prediction_class>` where `prediction_class` is the number which specifies the the time within which we want transaction to be confirmed by blockchain, please reference the [Fee predictor trainer doc](FeePredictorTrainer.md) for more details about the data.

In order to run the `fee predictor service` need the scaler and model which created by the `Fee predictor trainer`.

The whole server is pretty simple in its `app.py` there is defined route which get the prediction from `Predictor` class and convert it to `json`.

## Predictor
This is class defined in the `predictor/predictor.py`. This incapsulated all the prediction logic.

It can be considered consisted of two parts:

1. Collecting mempool data
2. Making the prediction

### Mempool data collection

For the mempool data collection actually the best option have the full node deployed, connect to it via RPC (please find the related code in removed part of the following [commit](https://gitlab.inyar.ru/bitcoin-transaction-optimization/predictor-service/commit/acd2b1f4e3851246fc104c04f092de96177da632)) and just request the data needed. This is fast request with good precision and this should provide us with the best quality, unfortunately deploying full node consumes a lot of resources so another approach is currently implemented.

We basically using the trick to collect mempool stats without full node - we just asking the server on which we trained our model for its full node info logs (1 row per minute), so our service relies on 3rd party and not the really precise but it works by the way.

### Making the prediction
It uses the trained model and scaler: collected mempool stats and specified time class are going through scaled transform and then feed to model, the result which is the predicted fee_per_byte returned back to caller.