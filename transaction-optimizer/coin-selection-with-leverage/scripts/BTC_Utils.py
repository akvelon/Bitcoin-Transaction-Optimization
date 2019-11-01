"""
Copyright 2019 Akvelon Inc.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at 
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the License for the specific language governing permissions and limitations under the License.
"""

# BTC_Utils

# Oct. 2019 1 BTC ~= $8,582
# Jan. 2018 1 BTC ~= $1,7174


def USD_to_Satoshi(usd, oneBTC = 8582):
	# OneBTC = dollar value of a single Bitcoin
	oneDollar = 1/oneBTC # 1 dollar in BTC value
	haveBTC = oneDollar*usd
	return haveBTC*1e8

def Satoshi_to_USD(sat, oneBTC = 8582):
	haveBTC = sat*1e-8
	return oneBTC*haveBTC
