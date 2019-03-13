"""
branch and bound algorithm selecting pay requests
"""
import utils, itertools, bisect, cProfile, pstats
from datetime import datetime

def branch_and_bound_by_pay_1_bin(utxos, payRequests, fee, timeout, verbose = 0):
  solver = Solver()
  return solver.solve(utxos, payRequests, fee, timeout, verbose)

class Problem:
  def __init__(self, utxos, payRequests, fee):
    self.utxos = utxos
    self.payRequests = payRequests
    self.fee = fee

class Solution:
  def __init__(self, txInput, txOutputs, value, amount, reward):
    self.txInput = txInput
    self.txOutputs = txOutputs
    self.value = value
    self.amount = amount
    self.change = txInput.amount - amount
    self.reward = reward

class TxInputComplex:
  def __init__(self, utxos, fee):
    self.commission = fee*len(utxos)*utils.inputSizeBytes
    # amount for funding pay requests and fee
    self.amount = sum(utxos) - self.commission
    self.utxos = utxos

class TxOutput:
  def __init__(self, payRequest, fee):
    p = payRequest
    self.amount = p["amount"]
    self.reward = p["amount"]*(p["time"]+utils.transactionIntervalSeconds)/fee/utils.rewardDivisor
    self.payRequest = payRequest

class Solver:
  def solve(self, utxos, payRequests, fee, timeout, verbose):
    self._verbose = verbose
    self._considerUtxosPairs = True
    self._enumerateWide = True
    self._profile = False
    self.problem = Problem(utxos, payRequests, fee)
    self._init()
    if self._profile:
      cProfile.runctx("self._loop(timeout)", globals(), locals(), sort=pstats.SortKey.CUMULATIVE)
    else:
      self._loop(timeout)

  def _init(self):
    inputs = self._get_complex_inputs()
    outputs = map(lambda p: TxOutput(p, self.problem.fee), self.problem.payRequests)
    outputs = sorted(outputs, key=lambda v: v.reward, reverse=False)

    self.inputs = inputs
    self.outputs = outputs
    self.inputAmounts = list(map(lambda v:v.amount, inputs))
    self.solution = self._build_solution_for_all_pay_requests()
    self._minOutputCount = len(outputs)/2

  def _get_complex_inputs(self):
    "single input combines a number of utxos"
    inputs = []
    inputs.extend(map(lambda v: TxInputComplex([v], self.problem.fee), self.problem.utxos))
    if self._considerUtxosPairs:
      size = len(self.problem.utxos)
      pairs = ((x,y) for x in range(size) for y in range(x+1, size))
      inputs.extend(itertools.starmap(lambda x, y: TxInputComplex([self.problem.utxos[x], self.problem.utxos[y]], self.problem.fee), pairs))
    inputs = list(filter(lambda v: v.amount > 0, inputs))
    print("inputs #{} all".format(len(inputs)))
    maxAmount = self._get_amount_for_all_pay_requests() + self._max_input_commission()
    a = map(lambda v: v.amount, inputs)
    a = filter(lambda v: v >= maxAmount, a)
    maxInputAmount = min(a, default=None)
    if maxInputAmount is not None:
      inputs = filter(lambda v: v.amount <= maxInputAmount, inputs)
    inputs = sorted(inputs, key=lambda v: v.amount, reverse=True)
    print("inputs #{} top removed".format(len(inputs)))
    inputs = Solver._remove_duplicate_amounts(inputs)
    inputs = Solver._remove_dominated_input_amounts(inputs)
    inputs = reversed(list(inputs))
    inputs = list(inputs)
    print("inputs #{} duplicates and dominated removed".format(len(inputs)))
    return inputs

  def _remove_duplicate_amounts(inputs):
    last = None
    for a in inputs:
      if last is None:
        last = a
      elif a.amount != last.amount:
        yield last
        last = a
      elif last.commission > a.commission:
        last = a
    if last is not None:
      yield last

  def _max_input_commission(self):
    return 2*self.problem.fee*utils.inputSizeBytes

  def _remove_dominated_input_amounts(inputs):
    """inputs should be sorted in the order of decreasing amount
    we assume that objective function is input.amount - input.commission
    """
    last = None
    for a in inputs:
      if last is None:
        last = a
        yield a
      else:
        amountDiff = last.amount - a.amount
        commissionDiff = a.commission - last.commission
        if amountDiff > commissionDiff:
          last = a
          yield a

  def _get_pay_request_total_amount(self):
    return sum(map(lambda v: v["amount"], self.problem.payRequests))

  def _get_amount_for_all_pay_requests(self):
    "without cost of inputs"
    return \
      sum(map(lambda v: v["amount"], self.problem.payRequests)) \
      + self.problem.fee * len(self.problem.payRequests) * utils.outputSizeBytes \
      + self.problem.fee * utils.containerSizeBytes

  def _get_amount_for_all_outputs(self):
    return self._get_amount_for_outputs(self.outputs)

  def _get_amount_for_outputs(self, txOutput):
    return \
      sum(map(lambda v: v.amount, txOutput)) \
      + self.problem.fee * len(txOutput) * utils.outputSizeBytes \
      + self.problem.fee * utils.containerSizeBytes

  def _build_solution_for_all_pay_requests(self):
    amount = self._get_amount_for_all_outputs()
    txInput = self._find_input(amount)
    if txInput is None:
      raise RuntimeError("Insufficient funds")
    reward = self._get_reward_for_all_outputs()
    value = Solver._get_objective_value(txInput, amount, reward)
    solution = Solution(txInput, self.outputs, value, amount, reward)
    return solution
  
  def _get_reward_for_all_outputs(self):
    return sum(map(lambda v: v.reward, self.outputs))

  def _find_input(self, amount):
    index = bisect.bisect_left(self.inputAmounts, amount)
    if index >= len(self.inputAmounts):
      return None
    #assert self.inputAmounts[index] >= amount
    return self.inputs[index]

  def _get_objective_value(txInput, amount, reward):
    """value of the object function we maximize
    amount - pay requests + tx fee with the exception of space of inputs
    """
    change = txInput.amount - amount
    value = reward - change - txInput.commission
    return value

  def _print_solution(self, iteration):
    print("iter {} change {} value {:.2f} reward {:.2f} outputs #{}"\
      .format(iteration, self.solution.change, self.solution.value, self.solution.reward, len(self.solution.txOutputs)))

  def _get_max_objective_value(self, reward):
    return reward - self.problem.fee*utils.inputSizeBytes

  def _print_reserved(reserved, i, suff = ""):
    a = map(lambda v: 0 if v == False else 1, reserved)
    a = list(a)
    #print(i, a, reserved, suff)
    print(a)

  def _get_depths(self):
    maxDepth = len(self.outputs)
    if not self._enumerateWide:
      yield maxDepth
      return
    minDepth = min(maxDepth, 5)
    step = 3
    yield from range(minDepth, maxDepth+1, step)
    if (maxDepth-minDepth) % step != 0:
      yield maxDepth

  def _loop(self, timeout):
    print("output # {}".format(len(self.outputs)))
    self._print_solution(0)
    fee = self.problem.fee
    """
    i points to leave node of last considered solution
    search is depth-first
    branches are enumerated in the order None - False - True
    """
    i = 0
    reserved = [None for _ in self.outputs]
    amount = self._get_amount_for_all_outputs()
    reward = self._get_reward_for_all_outputs()
    iteration = 0
    outputCount = len(self.outputs)
    self.startTime = datetime.now()

    for maxDepth in self._get_depths():
      while True:
        iteration += 1
        if iteration % 1000000 == 0 and datetime.now() - self.startTime > timeout:
          print("iter {} timeout reached".format(iteration))
          return
        if reserved[i] is None:
          reserved[i] = False
          amount -= self.outputs[i].amount + fee*utils.outputSizeBytes
          reward -= self.outputs[i].reward
          outputCount -= 1
          if outputCount < self._minOutputCount:
            continue
          maxValue = reward - self.problem.fee*utils.inputSizeBytes
          if maxValue <= self.solution.value:
            continue
          txInput = self._find_input(amount)
          value = Solver._get_objective_value(txInput, amount, reward)
          if value > self.solution.value:
            # new solution
            txOutputs = [self.outputs[i] for i, v in enumerate(reserved) if v != False]
            self.solution = Solution(txInput, txOutputs, value, amount, reward)
            self._print_solution(iteration)
          if i+1 < maxDepth:
            i += 1
          else:
            pass
        elif not reserved[i]:
          reserved[i] = True
          amount += self.outputs[i].amount + fee*utils.outputSizeBytes
          reward += self.outputs[i].reward
          outputCount += 1
          if i+1 < maxDepth:
            i += 1
        else: # reserved[i] == True
          # up
          reserved[i] = None
          i -= 1
          if i < 0:
            break
