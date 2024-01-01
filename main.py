import json, time, requests
from models import Signal
import concurrent.futures
from database import SessionLocal
from BingXApi_v2 import BingXApi
import random, schedule
import threading
from datetime import datetime
from database import SessionLocal


from setLogger import get_logger
logger = get_logger(__name__)


with open('config.json') as f:
    config = json.load(f)

api = BingXApi(APIKEY=config['api_key'], SECRETKEY=config['api_secret'], demo=False)


class BingX:
	bot: str = 'Stop' # 'Run'
	kline : bool =  False
	timeframe: str = ''
	leverage: int 
	margin_mode: str = "Isolated"
	symbols: list = []

	use_symbols : str = "all-symbols"
	close : dict = {}
    
	rsi_long : dict
	rsi_long_levels : []
	rsi_short : dict
	rsi_short_levels : []

	position : str = ''
	entry_rsi : list = []
	entry_time : int = 0
      

Bingx = BingX()


def schedule_kline():
	second_ = time.gmtime().tm_sec
	min_ = time.gmtime().tm_min
	hour_ = time.gmtime().tm_hour

	kline = False
	if Bingx.timeframe == '1m':
		kline = True
	elif Bingx.timeframe == "3m" and (min_ % 3 == 0):
		kline = True
	elif Bingx.timeframe == "5m" and (min_ % 5 == 0):
		kline = True
	elif Bingx.timeframe == "15m" and (min_ % 15 == 0):
		kline = True
	elif Bingx.timeframe == "30m" and (min_ % 30 == 0):
		kline = True
	elif Bingx.timeframe == "1h" and (min_ == 0):
		kline = True
	elif Bingx.timeframe == "4h" and (hour_ % 4 == 0) and (min_ == 0):
		kline = True
	
	if kline:
		logger.info("kline closed.")
		Bingx.kline = True
		logger.debug(f"Bingx kline---{Bingx.kline}")
		# requests.get(f"http://0.0.0.0:8000/bingx?s={True}", headers={'accept' : 'application/json'})
		# from tasks import update_klines
		# update_klines()
		from utils import update_all_klines
		if Bingx.position:
			update_all_klines(symbols=[Bingx.position])
		else:
			update_all_klines(symbols=Bingx.symbols)
		

	def delta(t):
		if t != 0:
			tm = datetime.fromtimestamp(t/1000)
			delta=datetime.now() - tm
			print(delta.days)
			if delta.days >= 1:
				logger.info("24-Hours pass from entry")
				Bingx.position = ""
				Bingx.entry_rsi = []
				Bingx.entry_time = 0

	delta(Bingx.entry_time)

	def reset_rsi_levels():
		if len(Bingx.entry_rsi) == len(Bingx.rsi_long_levels) + len(Bingx.rsi_short_levels):
			
			logger.info(f"{Bingx.position}---All levels done. reset ...")
			Bingx.position = ""
			Bingx.entry_rsi = []
			Bingx.entry_time = 0

	reset_rsi_levels()

def schedule_job():

	schedule.every(1).minutes.at(":02").do(schedule_kline)

	while True:
		if Bingx.bot == "Stop":
			schedule.clear()
			break
		schedule.run_pending()
		# print(time.ctime(time.time()))
		time.sleep(1)



def cross_up(symbol, close, rsi, time_):
	for level in Bingx.rsi_long_levels:
		# if round(rsi.iat[-1], 2) > level and round(rsi.iat[-2], 2) < level and\
		if round(rsi.iat[-1], 2) < level  and level not in Bingx.entry_rsi:
			Bingx.position = symbol
			Bingx.entry_rsi.append(level)
			if not Bingx.entry_time:
				Bingx.entry_time = time_
			logger.info(f"RSI up-cross: {symbol}---{round(rsi.iat[-1], 2)}---{level}---{time_}")
			# symbol, rsi, side, margin, price, time
			body = {"symbol": symbol, "rsi": round(rsi.iat[-1], 2),
					"side" : "BUY", "positionSide": "LONG",
					"margin" : Bingx.rsi_long[level]['margin'], 
					"price" : close, "time_" : time_, "rsi_level":level,
					'leverage':Bingx.leverage, 'margin_mode':Bingx.margin_mode,
					'TP':Bingx.rsi_long[level]['TP'],
					'SL':Bingx.rsi_long[level]['SL']}
			
			from producer import publish
			publish(body=json.dumps(body))


def cross_down(symbol, close, rsi, time_):
	for level in Bingx.rsi_short_levels:
		# if round(rsi.iat[-1], 2) < level and round(rsi.iat[-2], 2) > level and\
		if round(rsi.iat[-1], 2) > level and level not in Bingx.entry_rsi:
			Bingx.position = symbol
			Bingx.entry_rsi.append(level)
			if not Bingx.entry_time:
				Bingx.entry_time = time_
			logger.info(f"RSI down-cross: {symbol}---{round(rsi.iat[-1], 2)}---{level}---{time_}")
			#
			body = {"symbol": symbol, "rsi": round(rsi.iat[-1], 2),
					"side" : "SELL", "positionSide" : "SHORT",
					"margin" : Bingx.rsi_short[level]['margin'], 
					"price" : close, "time_" : time_, "rsi_level":level,
					'leverage':Bingx.leverage, 'margin_mode':Bingx.margin_mode,
					'TP':Bingx.rsi_short[level]['TP'],
					'SL':Bingx.rsi_short[level]['SL']}
			from producer import publish
			publish(body=json.dumps(body))


def placeOrder(symbol, side, positionSide, price, margin, qty, rsi, time_, rsi_level,
			   leverage, margin_mode, TP, SL):
	res = api.setLeverage(symbol=symbol, side=positionSide, leverage=leverage)
	logger.info(f"set leverage {res}")

	if side == "BUY":
		TP = price * (1 + TP/100)
		SL = price * (1 - SL/100)
	else:
		TP = price * (1 - TP/100)
		SL = price * (1 + SL/100)
	# print(symbol, side, margin, Bingx.TP_percent, Bingx.SL_percent)
	logger.info(f"{symbol}---{side}---{price}---{margin}---{rsi}---{qty}")

	res = api.setMarginMode(symbol=symbol, mode=margin_mode)
	logger.info(f"set margin type: {res}")

	take_profit = "{\"type\": \"TAKE_PROFIT_MARKET\", \"quantity\": %s,\"stopPrice\": %s,\"price\": %s,\"workingType\":\"MARK_PRICE\"}"% (qty, TP, TP)
	stop_loss = "{\"type\": \"STOP_MARKET\", \"quantity\": %s,\"stopPrice\": %s,\"price\": %s,\"workingType\":\"MARK_PRICE\"}"% (qty, SL, SL)
	res = api.placeOrder(symbol=symbol, side=f"{side}", positionSide=f"{positionSide}", tradeType="MARKET", 
				quantity=qty, 
				quoteOrderQty=margin,
				takeProfit=take_profit,
				stopLoss=stop_loss)
	logger.info(f"{res}")
	#
	from models import Signal
	signal = Signal()
	signal.symbol = symbol
	signal.side = side
	signal.price = price
	signal.time = datetime.fromtimestamp(time_/1000)
	db = SessionLocal()
	db.add(signal)
	db.commit()
	db.close()
	logger.info(f"load to sqlite. {symbol}---{side}---{datetime.fromtimestamp(time_/1000)}")