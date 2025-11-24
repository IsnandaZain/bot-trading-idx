import datetime
import time
import config.base as bs
import config.configuration as cfg

import pandas as pd
import sqlalchemy

from src.strategy import build_trading_state as bts

def start():
    # create db_conn and db_session for pandas
    conn_string = (
        "mysql+mysqlconnector://{user}:{passwd}@{host}:{port}/{dbname}".format(
            user=cfg.USER_DB,
            passwd=cfg.PASSWORD_DB,
            host=cfg.HOST_DB,
            port=cfg.PORT_DB,
            dbname=cfg.NAME_DB
        )
    )
    db_conn = sqlalchemy.create_engine(conn_string, pool_recycle=30, pool_pre_ping=True)

    # get all tickers
    tickers = bs.session.query(bs.MasterTicker).filter(bs.MasterTicker.ticker == "TOBA").all()
    for ticker in tickers:
        start = time.time()

        # get data histories
        query = """
            SELECT * FROM data_histories 
            WHERE ticker = '{ticker}' 
            ORDER BY date
        """.format(ticker=ticker.ticker)
        df = pd.read_sql(query, db_conn)

        if len(df) < 50:
            print(f"Ticker {ticker.ticker} skipped, data kurang dari 50 hari")
            continue

        trading_state = bts.build(df, ticker.ticker)

        end = time.time()
        print(f"time elapsed for ticker {ticker.ticker} is {end - start}")

    exit(1)



if __name__ == "__main__":
    start()
    