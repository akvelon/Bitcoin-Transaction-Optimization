import json, boto3

class TransactionService:
  def __init__(self, settings):
    self._settings = settings
    profile = self._settings['aws-profile']
    self._sqsClient = boto3.Session(profile_name=profile).client('sqs')

  def push(self, payRequests, inputs, change):
    def pay_request_to_output(request):
      body = request['Body']
      return { 'address': body['targetAddress'], 'amount': body['amount'] }
    
    def convert_input(input):
      return { 'txid': input['txid'], 'vout': input['vout'] }

    trans = {
      'inputs': list(map(convert_input, inputs)),
      'outputs': list(map(pay_request_to_output, payRequests))
    }
    if change != None:
      trans['change'] = change
    print("pay request: {}".format(json.dumps(trans)))
    
    self._sqsClient.send_message(
      QueueUrl=self._settings['prepared-transaction-sqs-url'],
      DelaySeconds=0,
      MessageBody=json.dumps(trans)
    )
    print("pay request sent")
