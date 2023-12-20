import json, time
from models import Signal
import concurrent.futures
from database import SessionLocal
from BingXApi_v2 import BingXApi
import random


from setLogger import get_logger
logger = get_logger(__name__)


with open('config.json') as f:
    config = json.load(f)

api = BingXApi(APIKEY=config['api_key'], SECRETKEY=config['api_secret'], demo=False)


class BingX:
	bot: str = 'Stop' # 'Run'
	timeframe: str = ''
	leverage: int = 10
	TP_percent: float = 2
	SL_percent: float = 1
	user_symbols: list = []
    
	rsi_long : dict
	rsi_long_levels : []
	rsi_short : dict
	rsi_short_levels : []



Bingx = BingX()


		