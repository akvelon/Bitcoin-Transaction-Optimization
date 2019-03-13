import json

class Settings:
  def __init__(self):
    with open("settings.json", 'r') as f:
      self._settings = json.load(f)
    
  def __getitem__(self, key):
    if key == "rpc-url":
      return self._settings.get(key, "")
    if key == "rpc-user":
      return self._settings.get(key, "")
    if key == "rpc-password":
      return self._settings.get(key, "")
    if key == "pay-request-chunk-size":
      return self._settings.get(key, 10)
    if key == "aws-profile":
      return self._settings.get(key, "")
    if key == "pay-request-sqs-url":
      return self._settings.get(key, "")
    if key == "prepared-transaction-sqs-url":
      return self._settings.get(key, "")
    if key == "sqs-wait-time-seconds":
      return self._settings.get(key, 5)
    if key == "optimize-round-time-seconds":
      return self._settings.get(key, 15*60)
    if key == "pay-request-visibility-time-seconds":
      return self._settings.get(key, 30*60+30)
    if key == "change-account-name":
      return self._settings.get(key, "")
    if key == "fee-predictor-url":
      url = self._settings.get(key, "").strip()
      if url != "" and not url.endswith("/"):
        url += "/"
      return url
      
    raise KeyError("unknown key {}".format(key))
