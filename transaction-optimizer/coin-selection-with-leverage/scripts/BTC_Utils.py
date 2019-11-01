# BTC_Utils

# Today (Oct. 2019) 1 BTC ~= $8,582
# Jan. 2018 1 BTC ~= $1,7174


def USD_to_Satoshi(usd, oneBTC = 8582):
	# OneBTC = dollar value of a single Bitcoin
	oneDollar = 1/oneBTC # 1 dollar in BTC value
	haveBTC = oneDollar*usd
	return haveBTC*1e8

def Satoshi_to_USD(sat, oneBTC = 8582):
	haveBTC = sat*1e-8
	return oneBTC*haveBTC