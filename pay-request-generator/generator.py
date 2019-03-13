"""
Copyright 2019 Akvelon Inc.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the License for the specific language governing permissions and limitations under the License.
"""
import boto3
import sys
import hashlib
import time
import random
import json
from Settings import Settings

settings = Settings()
sqs = boto3.Session(profile_name=settings["aws-profile"]).client('sqs')

if len(sys.argv) > 1 and sys.argv[1] == '--push':
    count = int(sys.argv[2])

    for i in range(count):
        now = str(time.time())
        address = random.choice(settings["target-addresses"])
        amount = random.randrange(1, 1000)
        customerId = "customer{}".format(random.randrange(100))
        response = sqs.send_message(
            QueueUrl=settings["pay-request-sqs-url"],
            DelaySeconds=0,
            MessageBody=json.dumps({
                'customerId': customerId,
                'targetAddress': address,
                'amount': amount
            })
        )

        print(response['MessageId'])

elif len(sys.argv) > 1 and sys.argv[1] == '--recieve':
    response = sqs.receive_message(
        QueueUrl=settings["pay-request-sqs-url"],
        AttributeNames=[]
    )

    message = response['Messages'][0]
    receipt_handle = message['ReceiptHandle']

    # Delete received message from queue
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )
    print('Received and deleted message: %s' % message)
else:
    print('''
    Example of work: 
    ~python main.py --push 10
        ''')