"""
Copyright 2019 Akvelon Inc.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the License for the specific language governing permissions and limitations under the License.
"""
import utils
from utils import Bin, is_postpone_pay_request
from BranchAndBound1Bin import branch_and_bound_1_bin

def branch_and_bound_2_bin(utxos, payRequests, fee1, fee2, timeout):
  assert fee1 > fee2
  bins = [Bin(), Bin()]
  bins[0].fee = fee1
  bins[1].fee = fee2
  for p in payRequests:
    if is_postpone_pay_request(p, [fee1, fee2]):
      bins[1].payRequests.append(p)
    else:
      bins[0].payRequests.append(p)
  for i, bin in enumerate(bins):
    bin.amount = utils.get_tx_amount(bin.payRequests, bin.fee)
    bin.inputAmount = 0
    bin.inputs = []
  
  bin, utxos2 = branch_and_bound_1_bin(utxos, bins[0].payRequests, bins[0].fee, timeout)
  bins[0] = bin
  bin, utxos3 = branch_and_bound_1_bin(utxos2, bins[1].payRequests, bins[1].fee, timeout)
  bins[1] = bin
  return bins, utxos3
