"""
Copyright 2019 Akvelon Inc.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the License for the specific language governing permissions and limitations under the License.
"""

"""
UTXO response
  {
    "txid" : "txid",          (string) the transaction id
    "vout" : n,               (numeric) the vout value
    "address" : "address",    (string) the bitcoin address
    "account" : "account",    (string) DEPRECATED. The associated account, or "" for the default account
    "scriptPubKey" : "key",   (string) the script key
    "amount" : x.xxx,         (numeric) the transaction output amount in BTC
    "confirmations" : n,      (numeric) The number of confirmations
    "redeemScript" : n        (string) The redeemScript if scriptPubKey is P2SH
    "spendable" : xxx,        (bool) Whether we have the private keys to spend this output
    "solvable" : xxx,         (bool) Whether we know how to spend this output, ignoring the lack of keys
    "safe" : xxx              (bool) Whether this output is considered safe to spend. Unconfirmed transactions
                              from outside keys and unconfirmed replacement transactions are considered unsafe
                              and are not eligible for spending by fundrawtransaction and sendtoaddress.
  }
"""
class UtxoService:
  "monitors Unspent Transaction Outputs"
  
  def __init__(self, bitcoinService):
    self._bitcoinService = bitcoinService
    self._spentOutputs = []
  
  def list_unspent(self):
    def is_unspent(output):
      return not any(spent['txid'] == output['txid'] and spent['vout'] == output['vout'] 
        for spent in self._spentOutputs)
    
    def convert_amount_to_satoshi(output):
      output = dict(output)
      output['amount'] = int(100_000_000 * output['amount'])
      return output

    utxo = self._bitcoinService.list_unspent()
    utxo = map(convert_amount_to_satoshi, utxo)
    return list(filter(is_unspent, utxo))

  def register_spent(self, outputs):
    self._spentOutputs.extend(outputs)
