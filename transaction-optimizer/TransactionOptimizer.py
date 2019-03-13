from datetime import datetime, timedelta
from enum import Enum, auto
import random, json

class TransactionOptimizer:
  def __init__(self, settings, feePredictor, payRequestService, transactionService, bitcoinService, utxoService):
    self._settings = settings
    self._feePredictor = feePredictor
    self._payRequestService = payRequestService
    self._transactionService = transactionService
    self._bitcoinService = bitcoinService
    self._utxoService = utxoService
    self._roundTime = timedelta(seconds=self._settings["optimize-round-time-seconds"])
    # minimum change amount. Do not create change below this value
    self._dustTheshhold = 300

  def run(self):
    self._init()
    while True:
      self._make_round()

  def _make_round(self):
    self._init_round()
    while not self._is_round_time_is_up():
      self.payRequests = self._payRequestService.get()
      print("received {} pay requests".format(len(self.payRequests)))
      requests = self._distribute_pay_requests_to_transactions()
      print("distribution: trans0: {}, trans1: {}, skipped: {}" \
        .format(len(requests[0]), len(requests[1]), len(self.payRequests)-len(requests[0])-len(requests[1])))
      self._add_requests_to_transaction(self.trans[0], requests[0])
      self._add_requests_to_transaction(self.trans[1], requests[1])
    self._finish_round()
  
  def _init(self):
    self.trans = [None, None]
  
  def _init_round(self):
    print("round started")
    self.unspentOutputs = self._utxoService.list_unspent()
    self.trans[0] = self._create_transaction()
    self.trans[1] = self._create_transaction()
    self.roundStartDatetime = datetime.now()

  def _finish_round(self):
    self._try_generate_transaction(self.trans[0])
    self._try_generate_transaction(self.trans[1])
    self.trans[0] = None
    self.trans[1] = None
    print("round finished")

  def _create_transaction(self):
    fee = self._feePredictor.get(0)
    trans = self.Transaction(fee)
    if len(self.unspentOutputs) == 0:
      print("no available outputs that can be spent")
    else:
      idx = random.randrange(len(self.unspentOutputs))
      print("utxo left {}".format(len(self.unspentOutputs)))
      print("selected utxo. amount {}".format(self.unspentOutputs[idx]['amount']))
      trans.add_input(self.unspentOutputs[idx])
      del self.unspentOutputs[idx]
    return trans

  def _is_round_time_is_up(self):
    delta = datetime.now() - self.roundStartDatetime
    return delta > self._roundTime
    
  def _is_current_transaction_optimized(self):
    return False
    
  def _distribute_pay_requests_to_transactions(self):
    requests=[[], []]
    for request in self.payRequests:
      result = self._classify_pay_request(request)
      if result == self.OptimizationDecision.CurrentTrans:
        requests[0].append(request)
      elif result == self.OptimizationDecision.NextTrans:
        requests[1].append(request)
    return requests
  
  def _add_requests_to_transaction(self, trans, payRequests):
    if len(payRequests) == 0:
      return
    skippedRequests = []
    print("adding pay requests to transaction #{}".format(len(payRequests)))
    for request in payRequests:
      amount = request['Body']['amount'] + trans.get_fee_per_pay_request()
      if trans.get_unspent_amount() >= amount:
        trans.add_pay_request(request)
        print("pay request added. Amount: {}".format(request['Body']['amount']))
      else:
        skippedRequests.append(request)
        print("pay request skipped. Amount: {}".format(request['Body']['amount']))
    # if no pay requests were added and transaction is empty
    # than maybe inputs are too small
    if len(skippedRequests) == len(payRequests) and trans.is_empty():
      pass
      # todo: add more inputs

  def _try_generate_transaction(self, trans):
    if len(trans.get_inputs()) == 0 or len(trans.get_pay_requests()) == 0:
      return
    unspendAmount = trans.get_unspent_amount()
    if unspendAmount > self._dustTheshhold:
      changeAddress = self._bitcoinService.create_change_address()
      change = { 'address': changeAddress, 'amount': unspendAmount }
      trans.set_change(change)
    print("transaction generated. input #/sum: {}/{}, output #/sum: {}/{}, change: {}, unspent: {}, fee: {}"\
      .format(len(trans.inputs), trans.get_inputs_amount(), \
        len(trans.payRequests), trans.get_pay_requests_amount(), \
        trans.change['amount'] if trans.change != None else 0, \
        unspendAmount, trans.get_fee()))
    if trans.get_inputs_amount() != trans.get_pay_requests_amount() + trans.get_change_amount() + trans.get_fee():
      print("!!! incorrect balance")
    self._payRequestService.remove(trans.payRequests)
    self._transactionService.push(trans.payRequests, trans.inputs, trans.change)
    self._utxoService.register_spent(trans.inputs)

  def _classify_pay_request(self, payRequest):
    code = random.randrange(0, 100)
    if code < 40:
      return self.OptimizationDecision.CurrentTrans
    elif code < 80:
      return self.OptimizationDecision.NextTrans
    else:
      return self.OptimizationDecision.Skip

  class Transaction:
    def __init__(self, fee):
      self.payRequests = []
      self.inputs = []
      self.change = None
      self.feePerByte = fee

    def is_empty(self):
      return len(self.payRequests) == 0
    
    def add_pay_request(self, request):
      self.payRequests.append(request)
    
    def add_input(self, input):
      self.inputs.append(input)

    def get_inputs(self):
      return self.inputs

    def get_pay_requests(self):
      return self.payRequests

    def set_change(self, change):
      self.change = change
    
    def get_fee_per_pay_request(self):
      return int(100 * self.feePerByte)

    def get_inputs_amount(self):
      return sum(map(lambda i: i['amount'], self.inputs))

    def get_pay_requests_amount(self):
      return sum(map(lambda p: p['Body']['amount'], self.payRequests))

    def get_change_amount(self):
      return self.change['amount'] if self.change != None else 0

    def get_fee(self):
      return self.get_inputs_amount() - self.get_pay_requests_amount() - self.get_change_amount()

    def get_unspent_amount(self):
      return self.get_inputs_amount() \
        - self.get_pay_requests_amount() \
        - int(self.get_fee_per_pay_request() * len(self.payRequests))

  class OptimizationDecision(Enum):
    CurrentTrans = auto()
    NextTrans = auto()
    Skip = auto()
    #Error = auto()
