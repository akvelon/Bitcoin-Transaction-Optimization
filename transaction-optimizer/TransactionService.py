"""
Copyright 2019 Akvelon Inc.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the License for the specific language governing permissions and limitations under the License.
"""
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
