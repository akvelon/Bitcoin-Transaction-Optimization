import random, json, math, itertools, statistics
from utils import get_change, outputSizeBytes
from BranchAndBound1Bin import branch_and_bound_1_bin, get_stat_branch_and_bound_1_bin
from BranchAndBound2Bin import branch_and_bound_2_bin
from BranchAndBoundByPay1Bin import branch_and_bound_by_pay_1_bin
from datetime import timedelta
from ga1Bin import ga_1_bin

modelTemplatePath=r"models\{}-model.json"
dataTemplatePath=r"data\{}.json"

def generate_utxos(n, mu = 10**6):
  muLog = math.log(mu)
  sigma = math.log(10)
  a = (int(random.lognormvariate(muLog, sigma)) for i in range(n))
  return a

def generate_pay_requests(requests_per_second, time, mu = 10**6):
  "time in seconds"
  muLog = math.log(mu)
  sigma = math.log(10)
  a = (int(random.lognormvariate(muLog, sigma)) for i in itertools.count())
  def time_generator():
    time = 0
    while True:
      time += random.expovariate(requests_per_second)
      yield time
  a = map(lambda amount, time: { "amount": amount, "time": time }, a, time_generator())
  a = itertools.takewhile(lambda v: v["time"] < time, a)
  return a

def generate_pay_requests_fixed_amount(count=10, mu=10**6):
  interval_seconds = 600/count
  amount_sequence = (int(mu) for _ in range(count))
  time_sequence = ((i+1)*interval_seconds for i in range(count))
  a = map(lambda amount, time: { "amount": amount, "time": time }, amount_sequence, time_sequence)
  return a

def generate_pay_requests_fixed_number(count=10, mu=10**6):
  muLog = math.log(mu)
  sigma = math.log(10)
  a = (int(random.lognormvariate(muLog, sigma)) for _ in itertools.count())
  a = map(lambda amount: { "amount": amount, "time": random.randrange(0, 600) }, a)
  a = itertools.islice(a, count)
  return a

def save_model(values, name, isPlain = True):
  if isPlain:
    b = map(lambda v: {"a":v}, values)
  else:
    b = values
  modelPath = modelTemplatePath.format(name)
  with open(modelPath, 'w') as f:
    json.dump(list(b), f)

def save_data(path, data):
  with open(path, 'w') as f:
    json.dump(data, f)

def save_data_rel(name, data):
  path = dataTemplatePath.format(name)
  with open(path, 'w') as f:
    json.dump(data, f)

def load_data(path):
  with open(path, 'r') as f:
    return json.load(f)

def load_data_rel(name):
  path = dataTemplatePath.format(name)
  with open(path, 'r') as f:
    return json.load(f)

def save_data_bin(bin):
  d = algo.convert_bin_to_serializable(bin)
  save_data_rel("bin", d)

def load_data_bin():
  d = load_data_rel("bin")
  bin = algo.convert_bin_from_serializable(d)
  return bin

def pin_random_generator():
  random.seed(1550832049495)

def main():
  #pin_random_generator()
  #test_branch_and_bound_1_bin()
  test_branch_and_bound_by_pay_1_bin()

def test_branch_and_bound_1_bin():
  utxos = generate_utxos(1000)
  utxos = list(utxos)
  payRequests = generate_pay_requests(1/60, 600)
  payRequests = list(payRequests)
  timeout = timedelta(seconds = 5)
  bin, utxosRest_ = branch_and_bound_1_bin(utxos, payRequests, 1, timeout, verbose=2)

def test_branch_and_bound_by_pay_1_bin():
  utxos = generate_utxos(1000, 10**6)
  utxos = list(utxos)
  payRequests = generate_pay_requests_fixed_number(100, 10**6)
  payRequests = list(payRequests)
  timeout = timedelta(seconds = 30)
  branch_and_bound_by_pay_1_bin(utxos, payRequests, 1, timeout)

if __name__ == "__main__":
    main()
