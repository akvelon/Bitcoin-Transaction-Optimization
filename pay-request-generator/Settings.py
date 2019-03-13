import json

class Settings:
  def __init__(self):
    with open("settings.json", 'r') as f:
      self._settings = json.load(f)
    
  def __getitem__(self, key):
    if key == "aws-profile":
      return self._settings.get(key, "")
    if key == "pay-request-sqs-url":
      return self._settings.get(key, "")
    if key == "target-addresses":
      return self._settings.get(key, [])
      
    raise KeyError("unknown key {}".format(key))
