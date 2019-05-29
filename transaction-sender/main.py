"""
Copyright 2019 Akvelon Inc.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the License for the specific language governing permissions and limitations under the License.
"""

from RPCHost import RPCHost
from SQSQueue import SQSQueue
from tx import Transaction
from Settings import Settings
import time, boto3


app_settings = Settings()

bitcoind_url = 'http://' + app_settings['rpc-user'] + ':' + app_settings['rpc-password'] + '@' + app_settings['rpc-url']
host = RPCHost(bitcoind_url)

queue_url = app_settings['prepared-transaction-sqs-url']
aws_profile_name = app_settings["aws-profile"]
incoming_tx_queue = SQSQueue(queue_url, aws_profile_name)

def loop():
    try:
        print('Round start')
        incoming_tx = incoming_tx_queue.get_message()
        if incoming_tx:
            print('Got tx, working on it')
            tx = Transaction(host, incoming_tx['Body'])
            result = tx.send()
            print('Round end')
            time.sleep(5)
            loop()
        else:
            print('Got no tx. Round end')
            time.sleep(5)
            loop()
    except Exception as e:
        print('An error occured:')
        print(e)
        print('Round end')
        time.sleep(5)
        loop()

loop()