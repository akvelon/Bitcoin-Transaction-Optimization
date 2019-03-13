"""
Copyright 2019 Akvelon Inc.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the License for the specific language governing permissions and limitations under the License.
"""

inputSizeBytes = 148
outputSizeBytes = 34
containerSizeBytes = 10
transactionIntervalSeconds = 600
rewardDivisor = 60000

class Bin:
  def __init__(self):
    self.payRequests = []
    # total amount payments that must be made: sum(payRequests) + fee * size-of-transaction
    self.amount = 0
    # sum(self.inputs)
    self.inputAmount = 0
    self.inputs = []

def is_empty(iterator):
  return all(False for _ in iterator)

def is_not_empty(iterator):
  return any(True for _ in iterator)

def convert_bin_to_serializable(bin):
  d = dict()
  d["fee"] = bin.fee
  d["payRequests"] = bin.payRequests
  d["inputs"] = bin.inputs
  return d

def convert_bin_from_serializable(d):
  bin = Bin()
  bin.fee = d["fee"]
  bin.payRequests = d["payRequests"]
  bin.inputs = d["inputs"]
  bin.inputAmount = sum(bin.inputs)
  bin.amount = get_tx_amount(bin.payRequests, bin.fee, bin.inputs)
  return bin

def get_change_cost(fee):
  "calculate cost of making change"
  return fee*(inputSizeBytes+outputSizeBytes)

def get_solution_expense(fee, change):
  changeCost = get_change_cost(fee)
  return change if change < changeCost else changeCost

def get_change(bin):
  return sum(bin.inputs) - bin.amount

def get_tx_amount(payRequests, fee, inputs = None):
  amount = sum(map(lambda v: v["amount"], payRequests))
  amount += fee * containerSizeBytes
  amount += fee * outputSizeBytes * len(payRequests)
  if inputs != None:
    amount += fee * inputSizeBytes * len(inputs)
  return amount

def is_postpone_pay_request(payRequest, fees):
  "true - postpone this pay request to the next tx"
  p = payRequest
  return (p["time"]+transactionIntervalSeconds)/fees[0] < (p["time"])/fees[1]
