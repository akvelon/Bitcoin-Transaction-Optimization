## Getting started

### Install Python
* Install [Python 3.6.1](https://www.python.org/downloads/release/python-361/)
* Install additional python packages:
    ```bash
    pip install boto3 requests
    ```
* For each tool about to run, install its dependencies
    ```bash
    pip install -r requirements.txt
    ```

### Install Docker
* Install Docker for your system (https://docs.docker.com/docker-for-windows/install/)
* Switch container type to Linux (https://docs.docker.com/docker-for-windows/#switch-between-windows-and-linux-containers)

### Get AWS access and credentials
* You need to have an Account with SQS service ready.
* Save your Account ID
* Get Access Key ID & Secret Access Key for CLI

### Install AWS CLI
* [Install](https://docs.aws.amazon.com/cli/latest/userguide/install-windows.html)
* [Configure](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) by running in cmd:
    ```bash
    aws configure --profile bto
    ```
    result profile and credentials could be found here: `c:\Users\<username>\.aws\`.

### Check out the code
```bash
git clone https://github.com/akvelon/Bitcoin-Transaction-Optimization
```

### Launch [Bitcoin full node](https://github.com/bitpay/bitcore)
* could be launched locally or on amazon EC2 machine.

### [Train](../predictor-trainer/README.md#run) Fee Predictor
* [Get](Collector.md) data for training.
* Copy `.\nnfee\data\collector\out\*training.csv` to `.\predictor-trainer\data\training.csv` (note, that file should be renamed to without prefix - `training.csv`).
* cd to `.\predictor-trainer`.
* Train model: `python cli.py --train`.
* Evaluate model: `python cli.py --evaluate`.
* Copy `.\predictor-trainer\data\models\` to `.\predictor-service\model\`.

### Launch [Fee Predictor](../predictor-service/README.md) service
* Run service
    ```bash
    flask run
    ```
* Send the request: GET http://localhost:5000/api/v1.0/prediction/1 to check service working correctly. Expected output looks like this:
    ```bash
    {"recommend_fee":6.536773204803467}
    ```
* could be launched locally or on amazon EC2 machine

### Launch [Transaction Optimizer](../transaction-optimizer/README.md)
* prepare `settings.json` - copy `settings.example.json` to `settings.json`:
    - set connection to Bitcoin full node with `rpc-...` settings
    - set correct SQS URLs.
    - check fee-predictor-url (it might have different port)
    - run optimizer:
        ```bash
        python main.py
        ```

### Launch [Transaction Sender](../transaction-sender/README.md)
```bash
python main.py
```

### Send 10 payment requests with [Request Generator](../pay-request-generator/README.md)
```bash
python generator.py --push 10
```

### Addendum
* Each project that has `settings.example.json` should have `setting.json` to be configured correctly.
* You probably need to specify custom `aws-profile` in the configuration file.
* See `Readme.md` of the corresponding projects for further details.
