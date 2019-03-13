# Queue Generator

Allows to push new transaction requests into Amazon SQS
 
### How to use

Requires Python 3.6.2 (or higher)

Install the dependencies:

```sh
$ pip install boto3
```
How to use:

```sh
$ python generator.py --push N
$ python generator.py --recieve
```
First allow you to push N messages into queue
Second allows to recieve one

Want to contribute? Great!

### configuration file

Configuration settings are loaded from `settings.json` in the current directory. See `settings.example.json` for example.

*  `aws-profile`: `bto`, - aws profile name. It's used for access to aws resources.
*  `pay-request-sqs-url`: `https://sqs.us-east-1.amazonaws.com/xxxxxxxxxxxx/pay-request`, - sqs url. Pay requests are pushed into this queue.
*  `target-addresses`: [ ] - list of target bitcoin addresses. Script randomly select address for each payment request.
  