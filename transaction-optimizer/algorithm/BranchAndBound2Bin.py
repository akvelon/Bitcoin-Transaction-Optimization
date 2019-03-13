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
