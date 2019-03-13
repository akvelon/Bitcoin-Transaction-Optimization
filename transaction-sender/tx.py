import json, boto3
from SQSQueue import SQSQueue
from Settings import Settings

app_settings = Settings()

class Transaction:

    success_queue = SQSQueue(app_settings['succeed-tx-que'])

    def __init__(self, host, tx_str):
        self.tx_obj = json.loads(tx_str)
        self.__outputs = {}
        self.host = host

    def __prepare_raw(self):
        self.__inputs = self.tx_obj['inputs']
        outputs = self.tx_obj['outputs']
        change = self.tx_obj['change']
        self.__unpack_outputs(outputs, change)
        return self.host.call('createrawtransaction', self.__inputs, self.__outputs)

    def __sign_raw(self, raw):
        return self.host.call('signrawtransaction', raw)

    def __unpack_outputs(self, *outputs):
        for o in outputs:
            self.__push_output(o)

    def __push_output(self, o):
        if type(o) is dict:
            self.__outputs[o['address']] = o['amount'] / 100000000
        elif type(o) is list:
            for out in o:
                self.__outputs[out['address']] = out['amount'] / 100000000

    def __decode_raw(self, raw):
        self.host.call('decoderawtransaction', raw['hex'])

    def send(self):
        raw = self.__prepare_raw()
        signed = self.__sign_raw(raw)

        result = self.host.call('sendrawtransaction', signed['hex'])
        print("Send complete. txid is: " + result)
        self.success_queue.push_message(f'tx {result} was successfully sent')
