"""
Copyright 2019 Akvelon Inc.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the License for the specific language governing permissions and limitations under the License.
"""
from utils import is_not_empty, is_empty, Bin
import utils
from datetime import datetime
import random, math

def branch_and_bound_1_bin(utxos, payRequests, fee, timeout, verbose = 0):
  solver = Solver()
  return solver.solve(utxos, payRequests, fee, timeout, verbose)

def get_stat_branch_and_bound_1_bin(utxos, payRequests, fee, timeout, verbose = 0):
  solver = Solver()
  startTime = datetime.now()
  solver.solve(utxos, payRequests, fee, timeout, verbose)
  time = datetime.now() - startTime
  return solver.solution.expense, solver.solution.iteration, time

class Solution:
  def __init__(self, change, inputs, expense):
    self.change = change
    self.inputs = inputs
    self.expense = expense

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
    #self._loop_size2()
    #self._loop_size3()
    #self._loop_size4()
    self._loop(timeout)
    self._reconstruct_inputs()
    return self.bin, self.restUtxo

  def _init(self):
    fee = self.problem.fee
    self._filter_pay_requests(self.problem.payRequests, fee)
    if is_empty(self._payRequests):
      raise RuntimeError("No pay request")

    # utxos = utxos - cost of using it in tx
    utxos = map(lambda v: v-fee*utils.inputSizeBytes, self.problem.utxos)
    utxos = filter(lambda v: v>0, utxos)
    utxos = list(utxos)
    if is_empty(utxos):
      raise RuntimeError("Insufficient funds")

    amount = utils.get_tx_amount(self._payRequests, fee)
    if amount > sum(utxos):
      raise RuntimeError("Insufficient funds")
    largeUtxos = list(filter(lambda v: v>=amount, utxos))
    if is_not_empty(largeUtxos):
      minUtxo = min(largeUtxos)
      change = minUtxo - amount
      solution = Solution(change, [minUtxo], utils.get_solution_expense(fee, change))
      utxos = list(filter(lambda v: v < minUtxo, utxos))
    else:
      solution = Solver._build_solution_min_inputs_with_change(utxos, amount, fee)
    # solution - the best solution so far
    if solution is None or len(solution.inputs) > self._inputCountMax:
      raise RuntimeError("No solution")

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
    inputs = []
    s = 0
    for a in utxos:
      inputs.append(a)
      s += a
      if s >= amount:
        break
    change = s-amount
    return Solution(s-amount, inputs, utils.get_solution_expense(fee, change))

  def _build_solution_min_inputs_with_change(utxos, amount, fee):
    # add change
    amount += fee*utils.outputSizeBytes
    utxos = sorted(utxos, reverse=True)
    inputs = []
    s = 0
    for a in utxos:
      inputs.append(a)
      s += a
      if s >= amount:
        break
    if s < amount:
      return None
    change = s-amount
    return Solution(s-amount, inputs, utils.get_solution_expense(fee, change))

  def _get_first_unused_index(reserved):
    for i, v in enumerate(reserved):
      if v is None:
        return i
    raise RuntimeError("reserved vector is full")

  def _build_input_by_reserv(utxos, reserved):
    input = []
    for i, v in enumerate(reserved):
      if v:
        input.append(utxos[i])
    return input

  def _sum_undefined(utxos, reserved):
    s = 0
    for i, v in enumerate(reserved):
      if v is None:
        s += utxos[i]
    return s

  def _print_solution(self, iteration):
    if self.solution is None:
      print("iter {} not solution".format(iteration))
    else:
      print("iter {} change: {}, inputs[{}] : {}, input sum: {}, amount: {}"\
        .format(iteration, self.solution.change, len(self.solution.inputs), self.solution.inputs, sum(self.solution.inputs), self.amount))

  def _loop(self, timeout):
    if self._verbose > 1:
      self._print_solution(0)
    if is_empty(self.utxos):
      # solution found or does not exist
      return
    if self.solution is not None and self.solution.change == 0:
      return

    self.utxos = sorted(self.utxos, reverse=True)
    #random.shuffle(self.utxos)
    i = 0
    reserved = [None for _ in self.utxos] # None - default, True - utxos used, False - utxos unused
    inputAmount = 0
    inputCount = 0
    iteration = 0
    self.startTime = datetime.now()

    while True:
      iteration += 1
      if iteration % 100000 == 0 and datetime.now() - self.startTime > timeout:
        print("iter {} timeout reached".format(iteration))
        break
      if reserved[i] is None:
        reserved[i] = True
        inputAmount += self.utxos[i]
        inputCount += 1

        # Note. amount does not include commision of change output.
        if inputAmount >= self.amount:
          # solution found
          change = inputAmount - self.amount
          expense = utils.get_solution_expense(self.problem.fee, change)
          if self.solution is None or expense < self.solution.expense or (self._allSolutions and expense == 0):
            inputs = Solver._build_input_by_reserv(self.utxos, reserved)
            self.solution = Solution(change, inputs, expense)
            self.solution.iteration = iteration
            if self._verbose > 1:
              self._print_solution(iteration)
            if change == 0 and not self._allSolutions:
              break # optimal solution found
        elif inputCount < self._inputCountMax and i+1 < len(reserved):
          i += 1
      elif reserved[i]:
        reserved[i] = False
        inputAmount -= self.utxos[i]
        inputCount -= 1
        if inputCount < self._inputCountMax and i+1 < len(reserved):
          i += 1
      else: # reserved[i] == False
        reserved[i] = None
        i -= 1
        if i < 0:
          break
  
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

  def _loop_size2(self):
    size = len(self.utxos)
    iteration = 0
    for i in range(size):
      iteration += 1
      if self.utxos[i] > self.amount:
        change = self.utxos[i] - self.amount
        expense = utils.get_solution_expense(self.problem.fee, change)
        if expense < self.solution.expense:
          self.solution = Solution(change, [self.utxos[i]], expense)
          if self._verbose > 1:
            self._print_solution(iteration)
      else:
        for j in range(i+1, size):
          iteration += 1
          if self.utxos[i] + self.utxos[j] > self.amount:
            # solution
            change = (self.utxos[i] + self.utxos[j]) - self.amount
            expense = utils.get_solution_expense(self.problem.fee, change)
            if expense < self.solution.expense:
              self.solution = Solution(change, [self.utxos[i], self.utxos[j]], expense)
              if self._verbose > 1:
                self._print_solution(iteration)

  def _loop_size3(self):
    size = len(self.utxos)
    iteration = 0
    for i in range(size):
      iteration += 1
      if self.utxos[i] > self.amount:
        change = self.utxos[i] - self.amount
        expense = utils.get_solution_expense(self.problem.fee, change)
        if expense < self.solution.expense:
          self.solution = Solution(change, [self.utxos[i]], expense)
          if self._verbose > 1:
            self._print_solution(iteration)
      else:
        for j in range(i+1, size):
          iteration += 1
          if self.utxos[i] + self.utxos[j] > self.amount:
            # solution
            change = (self.utxos[i] + self.utxos[j]) - self.amount
            expense = utils.get_solution_expense(self.problem.fee, change)
            if expense < self.solution.expense:
              self.solution = Solution(change, [self.utxos[i], self.utxos[j]], expense)
              if self._verbose > 1:
                self._print_solution(iteration)
          else:
            for k in range(j+1, size):
              iteration += 1
              if self.utxos[i] + self.utxos[j] + self.utxos[k] > self.amount:
                # solution
                change = (self.utxos[i] + self.utxos[j] + self.utxos[k]) - self.amount
                expense = utils.get_solution_expense(self.problem.fee, change)
                if expense < self.solution.expense:
                  self.solution = Solution(change, [self.utxos[i], self.utxos[j], self.utxos[k]], expense)
                  if self._verbose > 1:
                    self._print_solution(iteration)

  def _loop_size4(self):
    size = len(self.utxos)
    iteration = 0
    for i in range(size):
      iteration += 1
      if self.utxos[i] > self.amount:
        change = self.utxos[i] - self.amount
        expense = utils.get_solution_expense(self.problem.fee, change)
        if expense < self.solution.expense:
          self.solution = Solution(change, [self.utxos[i]], expense)
          if self._verbose > 1:
            self._print_solution(iteration)
      else:
        for j in range(i+1, size):
          iteration += 1
          if self.utxos[i] + self.utxos[j] > self.amount:
            # solution
            change = (self.utxos[i] + self.utxos[j]) - self.amount
            expense = utils.get_solution_expense(self.problem.fee, change)
            if expense < self.solution.expense:
              self.solution = Solution(change, [self.utxos[i], self.utxos[j]], expense)
              if self._verbose > 1:
                self._print_solution(iteration)
          else:
            for k in range(j+1, size):
              iteration += 1
              if self.utxos[i] + self.utxos[j] + self.utxos[k] > self.amount:
                # solution
                change = (self.utxos[i] + self.utxos[j] + self.utxos[k]) - self.amount
                expense = utils.get_solution_expense(self.problem.fee, change)
                if expense < self.solution.expense:
                  self.solution = Solution(change, [self.utxos[i], self.utxos[j], self.utxos[k]], expense)
                  if self._verbose > 1:
                    self._print_solution(iteration)
              else:
                for l in range(k+1, size):
                  iteration += 1
                  if self.utxos[i] + self.utxos[j] + self.utxos[k] + self.utxos[l] > self.amount:
                    # solution
                    change = (self.utxos[i] + self.utxos[j] + self.utxos[k] + self.utxos[l]) - self.amount
                    expense = utils.get_solution_expense(self.problem.fee, change)
                    if expense < self.solution.expense:
                      self.solution = Solution(change, [self.utxos[i], self.utxos[j], self.utxos[k], self.utxos[l]], expense)
                      if self._verbose > 1:
                        self._print_solution(iteration)
