import json, requests

class BitcoinService:
  def __init__(self, settings):
    self._settings = settings
  
  def list_unspent(self):
    response = self.send_request("listunspent", [1])
    return response.get('result', [])
  
  def send_request(self, method, params):
    auth = (self._settings["rpc-user"], self._settings["rpc-password"])
    url = self._settings["rpc-url"]
    headers = {'content-type': 'application/json'}
    proxies = {} # 'http': 'http://localhost:8888' }
    payload = {
      "method": method,
      "params": params
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers, proxies=proxies, auth=auth).json()
    return response

  def create_change_address(self):
    account = self._settings['change-account-name']
    response = self.send_request('getnewaddress', [account])
    return response['result']
