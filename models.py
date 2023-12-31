
from sqlalchemy import Column,Integer,Numeric,String, DateTime, Boolean, Float
from database import Base
from sqladmin import Admin, ModelView
from sqladmin import BaseView, expose
import wtforms




class Setting(Base):
    __tablename__ = "setting"
    id = Column(Integer,primary_key=True)  
    timeframe = Column(String, default='15m')
    leverage = Column(Integer, default=10)
    # TP_percent = Column(Float, default=1)
    # SL_percent = Column(Float, default=1)
    margin_mode = Column(String, default='ISOLATED')
    use_symbols = Column(String, default='all-symbols')
    reset = Column(Boolean, default=False)



class SettingAdmin(ModelView, model=Setting):
    #form_columns = [User.name]
    column_list = [Setting.timeframe, Setting.leverage, Setting.margin_mode,
                    Setting.use_symbols, Setting.reset]
    name = "Setting"
    name_plural = "Setting"
    icon = "fa-solid fa-user"
    form_args = dict(timeframe=dict(default="15m", choices=["15m", "5m", "1h", "4h", "1m", "3m"]), 
                     use_symbols=dict(default='All-symbols', choices=["all-symbols", "user-symbols"]),
                     margin_mode=dict(default='ISOLATED', choices=['ISOLATED', 'CROSSED']))
    form_overrides =  dict(timeframe=wtforms.SelectField, use_symbols=wtforms.SelectField,
                           margin_mode=wtforms.SelectField)

    # async def on_model_change(self, data, model, is_created):
    #     # Perform some other action
    #     #print(data)
    #     pass

    # async def on_model_delete(self, model):
    #     # Perform some other action
    #     pass



class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer,primary_key=True,index=True)
    symbol = Column(String)
    side = Column(String)
    price = Column(Float)
    time = Column(String)
    rsi_level = Column(Integer)


class SignalAdmin(ModelView, model=Signal):
    column_list = [Signal.id, Signal.symbol, Signal.side, Signal.price, Signal.time, Signal.rsi_level]
    column_searchable_list = [Signal.symbol, Signal.side, Signal.time, Signal.price, Signal.rsi_level]
    #icon = "fa-chart-line"
    icon = "fas fa-chart-line"
    column_sortable_list = [Signal.id, Signal.time, Signal.price, Signal.symbol, Signal.side, Signal.rsi_level]
    # column_formatters = {Signal.level0 : lambda m, a: round(m.level0,4),
    #                      Signal.level1 : lambda m, a: round(m.level1,4),
    #                      Signal.level2 : lambda m, a: round(m.level2,4),
    #                      Signal.level3 : lambda m, a: round(m.level3,4),
    #                      Signal.SLPrice : lambda m, a:round(m.SLPrice,4)}
    
    async def on_model_change(self, data, model, is_created):
        # Perform some other action
        #print(data)
        pass


class UserSymbols(Base):
    __tablename__ = "user-symbols"
    id = Column(Integer,primary_key=True)
    symbol = Column(String)

class UserSymbolAdmin(ModelView, model=UserSymbols):
    column_list = [UserSymbols.id, UserSymbols.symbol
                   ]
    name = "symbol"
    name_plural = "User Symbols"
    icon = "fa-sharp fa-solid fa-bitcoin-sign"
    column_sortable_list = [UserSymbols.symbol, UserSymbols.id]
    column_searchable_list = [UserSymbols.symbol, UserSymbols.id]
    page_size = 100
    # form_overrides = dict(symbol=wtforms.StringField, marginMode=wtforms.SelectField)
    # form_args = dict(symbol=dict(validators=[wtforms.validators.regexp('.+[A-Z]-USDT')], label="symbol(BTC-USDT)"),
    #                  marginMode=dict(choices=["Isolated", "Cross"]))
    # async def on_model_change(self, data, model, is_created):
    #     print(is_created)
    #     from database import SessionLocal
    #     db = SessionLocal()
    #     symbol = db.query(Symbols).order_by(Symbols.id.desc()).first()
    #     symbol.test = "iman"
    #     db.commit()


class Config(Base):
    __tablename__ = "config"
    id = Column(Integer,primary_key=True)  
    side = Column(String)
    rsi_level = Column(Integer)
    TP_percent = Column(Float)
    SL_percent = Column(Float)
    margin = Column(Integer)



class ConfigAdmin(ModelView, model=Config):
    #form_columns = [User.name]
    column_list = [Config.side, Config.rsi_level, Config.margin,
                   Config.TP_percent, Config.SL_percent
                   ]
    name = "Config"
    name_plural = "Config"
    icon = "fa-solid fa-user"
    column_searchable_list = [Config.margin, Config.rsi_level, Config.side, Config.id]
    column_sortable_list = [Config.margin, Config.rsi_level, Config.side, Config.id]
    form_args = dict(side=dict(choices=["Long", "Short"]), 
                     )
    form_overrides =  dict(side=wtforms.SelectField)

    # async def on_model_change(self, data, model, is_created):
    #     # Perform some other action
    #     #print(data)
    #     pass

    # async def on_model_delete(self, model):
    #     # Perform some other action
    #     pass


class AllSymbols(Base):
    __tablename__ = "all-symbols"
    id = Column(Integer,primary_key=True)
    symbol = Column(String)

class AllSymbolAdmin(ModelView, model=AllSymbols):
    column_list = [AllSymbols.id, AllSymbols.symbol
                   ]
    name = ""
    name_plural = "All Symbols"
    icon = "fa-sharp fa-solid fa-bitcoin-sign"
    column_sortable_list = [AllSymbols.symbol, AllSymbols.id]
    column_searchable_list = [AllSymbols.symbol, AllSymbols.id]
    page_size = 20
    # form_overrides = dict(symbol=wtforms.StringField, marginMode=wtforms.SelectField)
    # form_args = dict(symbol=dict(validators=[wtforms.validators.regexp('.+[A-Z]-USDT')], label="symbol(BTC-USDT)"),
    #                  marginMode=dict(choices=["Isolated", "Cross"]))
    # async def on_model_change(self, data, model, is_created):
    #     print(is_created)
    #     from database import SessionLocal
    #     db = SessionLocal()
    #     symbol = db.query(Symbols).order_by(Symbols.id.desc()).first()
    #     symbol.test = "iman"
    #     db.commit()



class ReportView(BaseView):
    name = "Home"
    icon = "fas fa-house-user"

    @expose("/home", methods=["GET"])
    async def report_page(self, request):
        from main import Bingx
        return await self.templates.TemplateResponse(name="base1.html", request=request, context={"request":request, "status":Bingx.bot})



