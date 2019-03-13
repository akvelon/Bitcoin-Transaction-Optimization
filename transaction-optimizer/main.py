import json, time
from PayRequestService import PayRequestService
from TransactionOptimizer import TransactionOptimizer
from TransactionService import TransactionService
from FeePredictor import FeePredictor
from Settings import Settings
from BitcoinService import BitcoinService
from UtxoService import UtxoService

def main():
  settings = Settings()
  payRequestService = PayRequestService(settings)
  feePredictor = FeePredictor(settings)
  transactionService = TransactionService(settings)
  bitcoinService = BitcoinService(settings)
  utxoService = UtxoService(bitcoinService)
  transactionOptimizer = TransactionOptimizer(settings, feePredictor, payRequestService, 
    transactionService, bitcoinService, utxoService)
  transactionOptimizer.run()

if __name__ == "__main__":
    main()
