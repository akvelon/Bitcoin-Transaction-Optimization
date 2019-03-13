"""
Copyright 2019 Akvelon Inc.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the License for the specific language governing permissions and limitations under the License.
"""
import boto3, json, itertools

class PayRequestService:
  "operation with pay request queue"
  
  def __init__(self, settings):
    self._settings = settings
    profile = self._settings['aws-profile']
    self._sqsClient = boto3.Session(profile_name=profile).client('sqs')
    self._visibilityTimeoutSeconds = self._settings["pay-request-visibility-time-seconds"]
    # sqs can return up to 10 messages
    self._sqsMaxMessages = 10
    
  def get(self):
    payRequests = []
    def decode(request):
      return { 
        'MessageId': request['MessageId'],
        'ReceiptHandle': request['ReceiptHandle'],
        'Body': json.loads(request['Body'])
      }
    
    # pull the target number of pay requests
    count = self._settings['pay-request-chunk-size']
    while count > 0:
      response = self._sqsClient.receive_message(
        QueueUrl=self._settings['pay-request-sqs-url'],
        MaxNumberOfMessages=min(count, self._sqsMaxMessages),
        VisibilityTimeout=self._visibilityTimeoutSeconds,
        WaitTimeSeconds=self._settings['sqs-wait-time-seconds']
      )

      messages = response.get('Messages', [])
      if len(messages) == 0:
        break
      count -= len(messages)
      payRequests.extend(map(decode, messages))

    return payRequests

  def remove(self, payRequests):
    if len(payRequests) == 0:
      return

    def create_entry(request, i):
      return { 'Id': str(i), 'ReceiptHandle': request['ReceiptHandle'] }

    def chunk_generator():
      entries = list(map(create_entry, payRequests, itertools.count()))
      for i in range(0, len(entries), self._sqsMaxMessages):
        yield entries[i:i+self._sqsMaxMessages]

    for chunk in chunk_generator():
      self._sqsClient.delete_message_batch(
        QueueUrl=self._settings['pay-request-sqs-url'],
        Entries=chunk
      )
      print("removed {} items from pay request queue".format(len(chunk)))

  def unhide(self, payRequests):
    if len(payRequests) == 0:
      return

    def create_entry(request, i):
      return { 'Id': str(i), 'ReceiptHandle': request['ReceiptHandle'], 'VisibilityTimeout': 0 }

    def chunk_generator():
      entries = list(map(create_entry, payRequests, itertools.count()))
      for i in range(0, len(entries), self._sqsMaxMessages):
        yield entries[i:i+self._sqsMaxMessages]

    for chunk in chunk_generator():
      self._sqsClient.change_message_visibility_batch(
        QueueUrl=self._settings['pay-request-sqs-url'],
        Entries=chunk
      )
      print("unhidden {} items of pay request queue".format(len(chunk)))
