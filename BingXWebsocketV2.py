
import websocket, time, gzip
import json, requests, threading
import pandas_ta as ta
import numpy as np
import pandas as pd


from setLogger import get_logger
logger = get_logger(__name__)



with open('config.json') as f:
    config = json.load(f)

class BingxWS:
    def __init__(self, handler=None, sub=None, Bingx=None):
        self.url = "wss://open-api-swap.bingx.com/swap-market"
        #self.url = f"wss://open-api-swap.bingx.com/swap-market?listenKey={listenKey}"
        self.handeler = handler
        self.sub = sub
        self.Bingx = Bingx
        self.ws = None
        self.listenKey = ''
        self.extendListenKeyStatus = False
        self.APIKEY = config['api_key']
        self.headers = {
            'Host': 'open-api-swap.bingx.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X -1_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        }
        
    def getListenKey(self):
        headers = {"X-BX-APIKEY" : self.APIKEY}
        res = requests.post("https://open-api.bingx.com/openApi/user/auth/userDataStream", headers=headers)
        self.listenKey = res.json()['listenKey']
        return self.listenKey
    
    def extendListenKey(self):
        headers = {"X-BX-APIKEY" : self.APIKEY}
        res = requests.put(f"https://open-api.bingx.com/openApi/user/auth/userDataStream?listenKey={self.listenKey}", headers=headers)
        #print("extendListenKey:......", res)
        return res
    

    def on_open(self, ws):
        #sub = {"id":"BTCUSDT-klin_1m", "reqType": "sub", "dataType":"BTC-USDT@kline_1m"}
        subscribe = self.sub
        for sub in subscribe:
            ws.send(json.dumps(sub))


    def on_message(self, ws, msg):
        data = gzip.decompress(msg)
        data = str(data,'utf-8')
        if self.Bingx.bot == "Stop":
            self.stop()
        if data == "Ping":
            ws.send("Pong")
            # if int(time.strftime('%M', time.localtime(time.time()))) % 30 == 0 and (not self.extendListenKeyStatus):
            #     #print('its time to extend key .... .... .... .... .... .... ... ... ...')
            #     self.extendListenKey()
            #     self.extendListenKeyStatus = True
            # elif int(time.strftime('%M', time.localtime(time.time()))) % 30 != 0:
            #     self.extendListenKeyStatus = False
        else:
            #print(data)
            self.handeler(data, self.Bingx)


    def on_error(self, ws, error):
        print('on_error: ', error)


    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")
        if close_status_code or close_msg:
            print("close status code: " + str(close_status_code))
            print("close message: " + str(close_msg))
        if self.Bingx.bot == "Run":
            print("try open websocket ...................")
            self.start()


    def start(self):
        #websocket.enableTrace(True)
        listenKey = self.getListenKey()
        self.ws = websocket.WebSocketApp(url=self.url+f"?listenKey={listenKey}", 
                                on_open=self.on_open, 
                                on_close=self.on_close,
                                on_message=self.on_message,
                                on_error=self.on_error,
                                header = self.headers)
        print("BingX WS OPENING ... ... ...")
        self.ws.run_forever()#dispatcher=rel, reconnect=5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
        #rel.signal(2, rel.abort)  # Keyboard Interrupt
        #rel.dispatch()


    def stop(self):
        self.ws.close()
        print('BingxWS  Closed.')



def start_bingx(data, Bingx):
    subscribe = []
    for symbol in data:
        subscribe.append({f"id":f"{symbol}", "reqType": "sub", "dataType":f"{symbol}@kline_{Bingx.timeframe}"})
        
    bingxWS = BingxWS(handler=handler, sub=subscribe, Bingx=Bingx)
    bingxWS.start()


def handler(data, Bingx):
    # print(data)
    try: 
        if not Bingx.kline:
            data = json.loads(data) # code/ dataType/ s/ data: c/o/h/l/c/v/T
            # print(data)
            symbol = data['s']
            close = float(data['data'][0]['c'])
            time_ = data['data'][0]['T']
            # print(symbol)
            if not Bingx.position or (Bingx.position == symbol):
                df = pd.DataFrame([close, *Bingx.close[symbol][1:]][::-1], columns=['close'])
                rsi = ta.rsi(close=df['close'], length=14)
                
                from main import cross_down, cross_up
                cross_up(symbol, close, rsi, time_)
                cross_down(symbol, close, rsi, time_)
                
                print(symbol, close, round(rsi.iat[-1], 2), Bingx.close[symbol][1], Bingx.close[symbol][2])
          
        else:
            print("please wait, update klines ... ... ...")
            # request_update_klines
    except Exception as e:
        # logger.exception(f"{e}")
        pass
            
    

def main_job(Bingx):
    symbols = Bingx.symbols
    start_bingx(symbols, Bingx)

