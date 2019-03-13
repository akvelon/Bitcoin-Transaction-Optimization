## Requirements

Install Python 3.7 or newer (tensorflow supports only 3.6.*, so if planning work on fee predictor install this version as well)

Install the following additional python packages: `boto3`, `requests`

Check out `https://github.com/akvelon/Bitcoin-Transaction-Optimization`.

You need to run these services on your local machine. Bitcoin full node for testnet and fee predictor should be launched locally or on amazon ec2 machine.

Prepare `setting.json` for each project. You may use `settings.example.json` file as example. You probably need to specify custom `aws-profile` in the configuration file.

Use pay request generator to create pay requests. You may specify the number request to generate via parameters.

Launch Transaction optimizer and transaction sender. Use Ctrl+c to terminate them if needed.

See Readme.md of the corresponding projects for further details.
