import requests

class FeePredictor:
  def __init__(self, settings):
    self.settings = settings

  def get(self, n):
    "get target fee for class n"
    url = self.settings["fee-predictor-url"]
    if url == "":
      return (n+1)*100
    # for example
    # url: "http://localhost:8000/api/v1.0/prediction/"
    # n: 1
    url += str(n)
    # url = http://localhost:8000/api/v1.0/prediction/1
    try:
      result = requests.get(url)
    except requests.exceptions.RequestException:
      print("unable to obtain target fee. Request to Fee Predictor service failed")
      raise
    if result.status_code != requests.codes.ok:
      msg = "unable to obtain target fee. Fee Predictor service returned status code {}".format(result.status_code)
      print(msg)
      raise RuntimeError(msg)
    try:
      return result.json()['recommend_fee']
    except:
      print("unable to obtain target fee. Fee Predictor service returned unexpectected result")
      raise
