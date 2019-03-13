"""
Copyright 2019 Akvelon Inc.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the License for the specific language governing permissions and limitations under the License.
"""
import boto3
sqs_client = boto3.client('sqs')

class SQSQueue:
    def __init__(self, url):

        self.url = url

    def get_message(self):
        response = sqs_client.receive_message(
        QueueUrl=self.url,
        AttributeNames=[]
        )
        message = response['Messages'][0]
        reciept_handle = message['ReceiptHandle']


        sqs_client.delete_message(
            QueueUrl=self.url,
            ReceiptHandle=reciept_handle
        )
        return message

    def push_message(self, message):
        return sqs_client.send_message(
            QueueUrl=self.url,
            DelaySeconds=0,
            MessageBody=message)

