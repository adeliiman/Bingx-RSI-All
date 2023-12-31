import requests, json, time, math
import hmac, hashlib, base64, urllib
import time
import json
from setLogger import get_logger


logger = get_logger(__name__)


with open('config.json') as f:
    config = json.load(f)


class BingXApi:
    def __init__(self, APIKEY='', SECRETKEY='', demo=True):
        self.SECRETKEY = SECRETKEY
        self.APIKEY = APIKEY
        self.APIURL = " https://open-api.bingx.com"
        if demo:
            self.APIURL = " https://open-api-vst.bingx.com"

    try:
        
        def get_sign(self, api_secret, payload):
            signature = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod='sha256').hexdigest()
            return signature


        def send_request(self, method, path, urlpa, payload):
            url = "%s%s?%s&signature=%s" % (self.APIURL, path, urlpa, self.get_sign(self.SECRETKEY, urlpa))
            headers = {
                'X-BX-APIKEY': self.APIKEY,
            }
            response = requests.request(method, url, headers=headers, data=payload)
            return response.json()

        def praseParam(self, paramsMap):
            sortedKeys = sorted(paramsMap)
            paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
            return paramsStr+"&timestamp="+str(int(time.time() * 1000))


        def getServerTime(self):
            url = "https://api-swap-rest.bingbon.pro/api/v1/common/server/time"
            res = requests.get(url)
            res = res.json()
            return res


        def getLatestPrice(self,symbol):
            payload = {}
            path = '/openApi/swap/v2/quote/price'
            method = "GET"
            paramsMap = {"symbol": f"{symbol}"}
            paramsStr = self.praseParam(paramsMap)
            return self.send_request(method, path, paramsStr, payload)



        def getKline(self, symbol, interval, startTime='', endTime='', limit=''):
            payload = {}
            path = '/openApi/swap/v3/quote/klines'
            method = "GET"
            paramsMap = {
            "symbol": symbol,
            "interval": interval,
            "startTime": startTime,
            "endTime": endTime,
            "limit": limit
             }
            paramsStr = self.praseParam(paramsMap)
            return self.send_request(method, path, paramsStr, payload)


        def getBalance(self):
            payload = {}
            path = '/openApi/swap/v2/user/balance'
            method = "GET"
            paramsMap = {
            "recvWindow": 5000
            }
            paramsStr = self.praseParam(paramsMap)
            return self.send_request(method, path, paramsStr, payload)



        def getPositions(self, symbol):  # --> 'data': {'positions': None}
            payload = {}
            path = '/openApi/swap/v2/user/positions'
            method = "GET"
            paramsMap = {
            "symbol": symbol,
            "recvWindow": 0
            }
            paramsStr = self.praseParam(paramsMap)
            return self.send_request(method, path, paramsStr, payload)


        def placeOrder(self, symbol, side, positionSide, price='', tradeType="MARKET", quoteOrderQty='', quantity='', stopPrice='', 
                       takeProfit='', stopLoss='', clientOrderID=''):
            # side: SELL/BUY
            # tradeType: MARKET/LIMIT/STOP_MARKET/TAKE_PROFIT_MARKET/STOP/TAKE_PROFIT/TRIGGER_LIMIT/TRIGGER_MARKET/TRAILING_STOP_MARKET
            payload = {}
            path = '/openApi/swap/v2/trade/order'
            method = "POST"
            paramsMap = {
            "symbol": symbol,
            "side": side,
            "positionSide": positionSide,
            "price": price,
            "type": tradeType,
            "quoteOrderQty": quoteOrderQty,
            "quantity": quantity,
            "stopPrice": stopPrice,
            "takeProfit": takeProfit,
            "stopLoss": stopLoss,
            "clientOrderID": clientOrderID
            }
            paramsStr = self.praseParam(paramsMap)
            return self.send_request(method, path, paramsStr, payload)


        def closeAllPositions(self):
            payload = {}
            path = '/openApi/swap/v2/trade/closeAllPositions'
            method = "POST"
            paramsMap = {
            "recvWindow": 0
            }
            paramsStr = self.praseParam(paramsMap)
            return self.send_request(method, path, paramsStr, payload)



        def setLeverage(self, symbol, side, leverage):
            payload = {}
            path = '/openApi/swap/v2/trade/leverage'
            method = "POST"
            paramsMap = {
            "symbol": symbol,
            "side": side, # LONG/SHORT
            "leverage": leverage,
            "recvWindow": 0
            }
            paramsStr = self.praseParam(paramsMap)
            return self.send_request(method, path, paramsStr, payload)


        def getOrders(self, symbol):  # --> 'data': {'orders': None}
            payload = {}
            path = 'GET /openApi/swap/v2/trade/openOrders'
            method = "GET"
            paramsMap = {
            "symbol": symbol,
            "recvWindow": 5000
            }   
            paramsStr = self.praseParam(paramsMap)
            return self.send_request(method, path, paramsStr, payload)


        def info(self):
            payload = {}
            path = '/openApi/swap/v2/quote/contracts'
            method = "GET"
            paramsMap = {}
            paramsStr = self.praseParam(paramsMap)
            return self.send_request(method, path, paramsStr, payload)


        def setMarginMode(self, symbol, mode):
            payload = {}
            path = '/openApi/swap/v2/trade/marginType'
            method = "POST"
            paramsMap = {
            "symbol": symbol,
            "marginType": mode, # ISOLATED/CROSSED
            }
            paramsStr = self.praseParam(paramsMap)
            return self.send_request(method, path, paramsStr, payload)
    
    except Exception as e:
        logger.exception(f"{e}")





# api = BingXApi(APIKEY=config['api_key'], SECRETKEY=config['api_secret'], demo=False)
# print(api.setMarginMode("BTC-USDT", "ISOLATED"))
# print(api.info()['data'][0])

# # print(api.getServerTime())
# klines = api.getKline(symbol="BTC-USDT", interval="1m", limit=20)
# klines = klines['data'][::-1]
# import pandas as pd
# df = pd.DataFrame(klines)
# df['time'] = pd.to_datetime(df['time']*1000000)
# print(df['time'].iat[-1])



# print(api.getBalance())
# print(api.getPositions(symbol="BTC-USDT")['data'][0])

# print(api.getOrders("BTC-USDT"))
# print(api.getStopOrders("ADA-USDT"))
# print(api.placeOrder(symbol="BTC-USDT", side="BUY",positionSide="LONG", price='30000', quantity=1, tradeType='MARKET'))
# print("."*10)
# print(api.placeOrder(symbol="BTC-USDT", side="SELL",positionSide="SHORT", price='30000', quantity=1, tradeType='MARKET'))
# print("."*10)
# print(api.getPositions("BTC-USDT"))
# print(api.placeOrder(symbol="BTC-USDT", side="SELL",positionSide="LONG", stopPrice='35000', price=35000, quantity=0.0001, tradeType='STOP'))
# print(api.placeOrder(symbol="BTC-USDT", side="SELL",positionSide="LONG", stopPrice='36500', price=37000, quantity=0.0001, tradeType='TAKE_PROFIT'))
# print(api.placeOrder(symbol="BTC-USDT", side="SELL",positionSide="LONG", stopPrice='36500', price=37000, quantity=0.0001, tradeType='TRAILING_STOP_MARKET'))

# take_profit = "{\"type\": \"TAKE_PROFIT_MARKET\", \"quantity\": 0.1,\"stopPrice\": 1000,\"price\": 1000,\"workingType\":\"MARK_PRICE\"}"
# print(api.placeOrder(symbol="ETH-USDT",side= "SELL",positionSide= "SHORT",tradeType= "MARKET",
#                      quoteOrderQty=100, quantity=0.1,
#                      takeProfit=take_profit))

# take_profit = "{\"type\": \"TAKE_PROFIT_MARKET\", \"quantity\": %s,\"stopPrice\": %s,\"price\": %s,\"workingType\":\"MARK_PRICE\"}"% (0.013, 1000, 1000)
# stop_loss = "{\"type\": \"STOP_MARKET\", \"quantity\": %s,\"stopPrice\": %s,\"price\": %s,\"workingType\":\"MARK_PRICE\"}"% (0.013, 3000, 3000)
# res = api.placeOrder(symbol="ETH-USDT", side="SELL", positionSide=f"SHORT", tradeType="MARKET", 
#             quantity=0.013, 
#             quoteOrderQty=100,
#             takeProfit=take_profit,
#             stopLoss=stop_loss)
# print(res)
# print(api.setLeverage("BTC-USDT", "LONG", '20'))




# print(api.closePosition(symbol="ADA-USDT", positionId='1575974277398663168'))
# print(api.closeStopOrder(symbol="ADA-USDT", orderId=123456))

# print(api.closeAllPositions())
# print( api.closeAllOrders())

