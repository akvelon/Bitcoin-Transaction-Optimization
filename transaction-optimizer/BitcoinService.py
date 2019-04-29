"""
Copyright 2019 Akvelon Inc.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the License for the specific language governing permissions and limitations under the License.
"""

import json, requests

class BitcoinService:
  def __init__(self, settings):
    self._settings = settings
  
  def list_unspent(self):
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
    }"""
    response = self.send_request("listunspent", [1])
    return response.get('result', [])
  
  def send_request(self, method, params):
    auth = (self._settings["rpc-user"], self._settings["rpc-password"])
    url = self._settings["rpc-url"]
    headers = {'content-type': 'application/json'}
    proxies = {} # 'http': 'http://localhost:8888' }
    payload = {
      "method": method,
      "params": params
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers, proxies=proxies, auth=auth).json()
    return response

  def create_change_address(self):
    account = self._settings['change-account-name']
    response = self.send_request('getnewaddress', [account])
    return response['result']
