"""
Copyright 2019 Akvelon Inc.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the License for the specific language governing permissions and limitations under the License.
"""
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
