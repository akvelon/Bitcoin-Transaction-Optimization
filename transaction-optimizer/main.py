"""
Copyright 2019 Akvelon Inc.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the License for the specific language governing permissions and limitations under the License.
"""
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
