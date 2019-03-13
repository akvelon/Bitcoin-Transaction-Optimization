from utils import is_not_empty, is_empty, Bin
import utils
from datetime import datetime
from bisect import bisect_left
import random, math

def ga_1_bin(utxos, payRequests, fee, timeout, verbose = 0):
  solver = Solver()
  return solver.solve(utxos, payRequests, fee, timeout, verbose)

class Solution:
  def __init__(self, change, inputInds, expense, iteration=0):
    self.change = change
    self.inputInds = inputInds
    self.expense = expense
    self.iteration = iteration

class Problem:
  def __init__(self, utxos, payRequests, fee):
    self.utxos = utxos
    self.payRequests = payRequests
    self.fee = fee

class Solver:
  """throws an exception if solution is not found
  
  fields
  - _payRequests - pay requests that should be included in transaction. 
    Small pay requests may be filtered out to satisfy the following requirement:
    'R.4.C.2. The Transaction Optimizer shall not construct a transaction were 
    the transaction fees are greater than the transaction value.'

  - _inputCountMax - maximum number of inputs allowed
  """
  def solve(self, utxos, payRequests, fee, timeout, verbose):
    self._verbose = verbose
    self._allSolutions = False
    self.problem = Problem(utxos, payRequests, fee)
    self._init()
    self._loop(timeout)
    self._reconstruct_inputs()
    return self.bin, self.restUtxo

  def _init(self):
    fee = self.problem.fee
    self._filter_pay_requests(self.problem.payRequests, fee)
    if is_empty(self._payRequests):
      raise RuntimeError("No pay request")

    amount = utils.get_tx_amount(self._payRequests, fee)

    # utxos = utxos - cost of using it in tx
    utxos = map(lambda v: v-fee*utils.inputSizeBytes, self.problem.utxos)
    utxos = filter(lambda v: v>0, utxos)
    utxos = filter(lambda v: v<amount, utxos)
    utxos = list(utxos)
    #utxos = sorted(utxos, reverse=True)

    if is_empty(utxos):
      raise RuntimeError("Insufficient funds")

    if amount > sum(utxos):
      raise RuntimeError("Insufficient funds")
    
    solution = Solver._build_any_solution(utxos, amount, fee)

    self.utxos = utxos
    self.amount = amount
    self.solution = solution

  def _filter_pay_requests(self, payRequests, fee):
    """
    check which pay requests can be included in transaction
    requirement: fee should not be large than transaction value
    """
    inputCountMin = 3 # minimum number of inputs to consider
    payRequests = sorted(payRequests, key=lambda v: v["amount"], reverse=True)
    while is_not_empty(payRequests):
      amount = sum(map(lambda v: v["amount"], payRequests))
      commission = fee*(utils.containerSizeBytes + (len(payRequests)+1)*utils.outputSizeBytes)
      inputCountMax = math.floor((amount - commission)/utils.inputSizeBytes)
      if inputCountMax >= inputCountMin:
        break
      payRequests.pop()
    self._payRequests = payRequests
    self._inputCountMax = 0 if is_empty(payRequests) else inputCountMax
    
  def _build_any_solution(utxos, amount, fee):
    inputInds = []
    s = 0
    for i, a in enumerate(utxos):
      inputInds.append(i)
      s += a
      if s >= amount:
        break
    change = s-amount
    return Solution(change, inputInds, utils.get_solution_expense(fee, change))

  def _loop(self, timeout):
    if self._verbose > 1:
      self._print_solution(0)
    if is_empty(self.utxos):
      # solution found or does not exist
      return
    if self.solution is not None and self.solution.change == 0:
      return
    iteration = 0
    self.solutionHistory = [self.solution]
    self.maxIterations = 100
    self.maxInputs = 6
    solutionIteration = 0

    parentInputInds = list(self.solution.inputInds)
    while True:
      iteration += 1
      #print(iteration)
      inputInds = list(parentInputInds)
      self._mutate(inputInds)
      inputAmount = self._get_input_amount(inputInds)
      change = inputAmount - self.amount
      #print("{} change {} ({})".format(iteration, change, self.solution.change))
      if change >= 0 and self.solution.change > change:
        solution = Solution(change, inputInds, None, iteration)
        self._add_solution(solution)
        parentInputInds = list(inputInds)
        self._print_solution(iteration)
      elif iteration - solutionIteration < self.maxIterations:
        parentInputInds = inputInds
      else:
        #if random.random() < 0.8:
        #  parentInputInds = inputInds
        #else:
        parentInputInds = list(self.solution.inputInds)
        solutionIteration = iteration
  
  def _add_solution(self, solution):
    self.solution = solution
    self.solutionHistory.append(solution)
    #index = bisect_left(self.solutionHistory, solution.change)

  def _print_solution(self, iteration):
    if self.solution is None:
      print("iter {} not solution".format(iteration))
    else:
      inputs = list(map(lambda i: self.utxos[i], self.solution.inputInds))
      inputAmount = self._get_input_amount(self.solution.inputInds)
      print("iter {} change: {}, inputs[{}] : {}, input sum: {}, amount: {}"\
        .format(iteration, self.solution.change, len(self.solution.inputInds), inputs, inputAmount, self.amount))

  def _get_input_amount(self, inputInds):
    return sum(map(lambda i: self.utxos[i], inputInds))

  def _mutate(self, inputInds):
    changed = False
    inputAmount = self._get_input_amount(inputInds)
    removing = inputAmount >= self.amount and random.randrange(10) == 0
    if removing:
      index = random.randrange(len(inputInds))
      inputAmount -= self.utxos[inputInds[index]]
      del inputInds[index]
      changed = True

    adding = inputAmount < self.amount and len(inputInds) < self.maxInputs and random.randrange(10) == 0
    if adding:
      while True:
        index = random.randrange(len(self.utxos))
        if index not in inputInds:
          break
      inputInds.append(index)
      return
    
    if changed:
      return

    while True:
      index = random.randrange(len(self.utxos))
      if index not in inputInds:
        break
    replacedIndex = random.randrange(len(inputInds))
    inputInds[replacedIndex] = index

  def _reconstruct_inputs(self):
    if self.solution is None:
      return
    fee = self.problem.fee
    inputs = list(map(lambda v: v+fee*utils.inputSizeBytes, self.solution.inputs))
    bin = Bin()
    bin.fee = fee
    bin.payRequests = self._payRequests
    bin.inputs = inputs
    bin.inputAmount = sum(bin.inputs) 
    bin.amount = utils.get_tx_amount(bin.payRequests, bin.fee, bin.inputs)
    self.bin = bin
    utxos = list(self.problem.utxos)
    for a in bin.inputs:
      utxos.remove(a)
    self.restUtxo = utxos
