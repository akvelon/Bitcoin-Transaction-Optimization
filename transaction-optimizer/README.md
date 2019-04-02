# Transaction Optimizer

Requirements:

Python 3.6.1 or newer

```sh
pip install boto3 requests
```

Create `settings.json` file by example of `settings.example.json`.

`settings.json` is searched in the current directory.

### settings

*  `rpc-url`: `http://localhost:18443` - url of the bitcoin full node. It's used for rpc requests.
*  `rpc-user`: `user`, - user name for rpc access to bitcoin full node
*  `rpc-password`: `password`, - password for `rpc-user`
*  `pay-request-chunk-size`: 15, - number payment requests to get at a time
*  `aws-profile`: `bto`, - aws profile name. It's required for access to aws resources like sqs.
*  `pay-request-sqs-url`: `https://sqs.us-east-1.amazonaws.com/xxxxxxxxxxxx/pay-request`, - url of the pay request sqs
*  `prepared-transaction-sqs-url`: `https://sqs.us-east-1.amazonaws.com/xxxxxxxxxxxx/prepared-transaction`, - url of the prepared transactions sqs
*  `sqs-wait-time-seconds`: 2, - how long to wait for pay requests. It should be >= 0.
*  `optimize-round-time-seconds`: 5, - duration of optimization round. Every round we start building transactions from scratch.
*  `pay-request-visibility-time-seconds`: 15, - period of time during which pull transaction should be hidden for subsequent pulls. It should be at least twice as large as `optimize-round-time-seconds`
*  `change-account-name`: `main`, bitcoin account name
*  `fee-predictor-url`: `http://localhost:8000/api/v1.0/prediction/` - fee predictor service url without the last fragment. Full url looks like `http://localhost:8000/api/v1.0/prediction/<int:prediction_class>/`. Optional parameter. If it is not specified, than optimizer user hard-coded fees.

where `xxxxxxxxxxxx` - is AWS Account number

How to use:

```sh
$ python main.py
```
