from RPCHost import RPCHost
from SQSQueue import SQSQueue
from tx import Transaction
from Settings import Settings
import time, boto3


app_settings = Settings()

sqs = boto3.client('sqs')
bitcoind_url = 'http://' + app_settings['rpc-user'] + ':' + app_settings['rpc-password'] + '@' + app_settings['rpc-url']
host = RPCHost(bitcoind_url)

incoming_tx_queue = SQSQueue(url=app_settings['prepared-transaction-sqs-url'])

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