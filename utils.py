from sqlalchemy.orm import Session
from models import Setting, Symbols, Config
from datetime import datetime, timedelta
from setLogger import get_logger



logger = get_logger(__name__)



def get_user_params(db: Session):
    try:
        user = db.query(Setting).first()
        config = db.query(Config).all()
        user_symbols = db.query(Symbols).all()
        from main import Bingx
        Bingx.timeframe = user.timeframe
        Bingx.TP_percent = user.TP_percent
        Bingx.SL_percent = user.SL_percent
        Bingx.leverage = user.leverage

        Bingx.rsi_short = {}
        Bingx.rsi_long = {}
        for conf in config:
            if conf.side == "Long":
                Bingx.rsi_long[conf.rsi_level] = conf.margin
            elif conf.side == "Short":
                Bingx.rsi_short[conf.rsi_level] = conf.margin

        Bingx.rsi_long_levels = sorted(Bingx.rsi_long)
        Bingx.rsi_short_levels = sorted(Bingx.rsi_short)
        
        Bingx.user_symbols = []
        for symbol in user_symbols:
            Bingx.user_symbols.append(symbol.symbol)
        print(Bingx.user_symbols)
    except Exception as e:
        logger.exception(msg="get_user_params" + str(e))