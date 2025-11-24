import datetime
from datetime import date

import pymysql
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey
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
