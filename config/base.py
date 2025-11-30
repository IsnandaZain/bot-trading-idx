import datetime
from datetime import date

import pymysql
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.dialects.mysql import DOUBLE, LONGTEXT

from urllib.parse import quote



Base = declarative_base()

DB_URL = "mysql+pymysql://{user}:{passwd}@{host}:{port}/{dbname}".format(
    user="root",
    passwd="",
    host="127.0.0.1",
    port=3306,
    dbname="stockanalyst"
)

# create session
Session = sessionmaker(bind=create_engine(DB_URL))
session = Session()


class MasterTicker(Base):
    __tablename__ = "mst_ticker"

    id = Column(Integer, primary_key=True, autoincrement=True)

    ticker = Column(String(5), nullable=False, default='')

    name = Column(String(200), nullable=False, default='')


class SupportResistance(Base):
    __tablename__ = "support_resistance"

    id = Column(Integer, primary_key=True, autoincrement=True)

    ticker = Column(String(5), nullable=False, index=True)

    support = Column(LONGTEXT, nullable=False, default='')  # Simpan sebagai JSON string

    data = Column(Date, default=date.today())


class DataHistories(Base):
    __tablename__ = 'data_histories'

    id = Column(Integer, primary_key=True, autoincrement=True)

    ticker = Column(String(5), nullable=False, default='')

    open = Column(Integer, nullable=False, default=0)

    high = Column(Integer, nullable=False, default=0)

    low = Column(Integer, nullable=False, default=0)

    close = Column(Integer, nullable=False, default=0)

    volume = Column(Integer, nullable=False, default=0)

    date = Column(Date, default=None)


    def __init__(self, ticker: str, open: int, high: int, low: int, close: int, volume: int, date: str):
        self.ticker = ticker
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.date = date


class TradeLog(Base):
    __tablename__ = 'trade_log'

    ACTION_BUY = 'BUY'

    id = Column(Integer, primary_key=True, autoincrement=True)

    timestamp = Column(DateTime, default=None)

    ticker = Column(String(5), nullable=False, default='')

    signal_type = Column(String(45), nullable=False, default='')

    action = Column(String(10), nullable=False, default='')  # buy or sell

    entry_price = Column(Integer, nullable=False, default=0)

    sl_price = Column(Integer, nullable=False, default=0)

    tp_price = Column(Integer, nullable=False, default=0)

    lot_size = Column(Integer, nullable=False, default=0)

    risk_rupiah = Column(Integer, nullable=False, default=0)

    rr_ratio = Column(DOUBLE, nullable=False, default=0.0)

    valid = Column(Boolean, nullable=False, default=True)

    reason = Column(String(255), nullable=False, default='')

    highest_since_entry = Column(Integer, nullable=True)

    trailing_stop_level = Column(Integer, nullable=True)

    status = Column(String(30), default="RUNNING")

    # Snapshot Kondisi Pasar
    price = Column(Integer, nullable=False, default=0)

    ma20 = Column(Integer, default=0)

    ma50 = Column(Integer, default=0)

    ma200 = Column(Integer, default=0)

    volume = Column(Integer, default=0)

    volume_ma20 = Column(Integer, default=0)

    supports = Column(LONGTEXT, nullable=False, default='')  # Simpan sebagai JSON string

    resistances = Column(LONGTEXT, nullable=False, default='')  # Simpan sebagai JSON string

    rsi = Column(DOUBLE, nullable=False, default=0.0)

    stoch_k = Column(DOUBLE, nullable=False, default=0.0)

    stoch_d = Column(DOUBLE, nullable=False, default=0.0)

    # Evaluasi Sinyal
    outcome = Column(String(20), nullable=False, default='pending')  # win, loss, pending

    exit_price = Column(Integer, nullable=False, default=0)

    exit_timestamp = Column(DateTime, default=None)

