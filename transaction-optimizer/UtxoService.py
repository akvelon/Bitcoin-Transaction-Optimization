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
