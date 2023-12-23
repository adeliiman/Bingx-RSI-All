from sqlalchemy.orm import Session
from models import Setting, UserSymbols, Config, AllSymbols
from datetime import datetime, timedelta
from setLogger import get_logger
import pandas as pandas
import pandas_ta as ta
import concurrent.futures
from main import Bingx



logger = get_logger(__name__)



# def kline(symbol, interval):
def kline(items):
    symbol = items[0]
    print(symbol)
    interval = items[1]
    from main import api, Bingx
    res = api.getKline(symbol=symbol, interval=interval, limit=100)
    # print(symbol, res['code'])
    close = []
    for data in res['data']:
        close.append(float(data['close']))

    Bingx.close[symbol] = close


def get_all_klines(symbols):
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        items = [(sym, f'{Bingx.timeframe}') for sym in symbols]
        executor.map(kline, items)
    logger.info("get all klines done.")
    Bingx.get_kline = True
    

async def update_klines(symbols):
    get_all_klines(symbols)


def get_user_params(db: Session):
    try:
        user = db.query(Setting).first()
        config = db.query(Config).all()
        user_symbols = db.query(UserSymbols).all()
        
        Bingx.timeframe = user.timeframe
        Bingx.TP_percent = user.TP_percent
        Bingx.SL_percent = user.SL_percent
        Bingx.leverage = user.leverage
        Bingx.use_symbols = user.use_symbols

        Bingx.rsi_short = {}
        Bingx.rsi_long = {}
        for conf in config:
            if conf.side == "Long":
                Bingx.rsi_long[conf.rsi_level] = conf.margin
            elif conf.side == "Short":
                Bingx.rsi_short[conf.rsi_level] = conf.margin

        Bingx.rsi_long_levels = sorted(Bingx.rsi_long)
        Bingx.rsi_short_levels = sorted(Bingx.rsi_short)
        
        Bingx.symbols = []
        if Bingx.use_symbols == "user-symbols":
            for symbol in user_symbols:
                Bingx.symbols.append(symbol.symbol)
        else:
            all_symbols = db.query(AllSymbols).all()
            for symbol in all_symbols:
                Bingx.symbols.append(symbol.symbol)
            
        #
        get_all_klines(Bingx.symbols)
            
    except Exception as e:
        logger.exception(msg="get_user_params" + str(e))



def add_all_symbols(db: Session):
    
    from main import api
    info = api.info()['data']
    for data in info:
        all = AllSymbols()
        all.symbol = data['symbol']
        db.add(all)
        db.commit()
        db.close()
    
    logger.info("add all symbols to SQl.")
    
