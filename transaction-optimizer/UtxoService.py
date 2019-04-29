"""
Copyright 2019 Akvelon Inc.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the License for the specific language governing permissions and limitations under the License.
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
