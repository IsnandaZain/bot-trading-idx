import datetime
import time
import config.base as bs
import config.configuration as cfg

import pandas as pd
import sqlalchemy

from src.spreadsheet import migrate

from src.strategy import build_trading_state as bts
from src.strategy import buy_signal as bsg
from src.strategy import trade_plan as tp

from src.tracking import log_trade as lt
from src.tracking import performance_analyzer as pa

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
            WHERE ticker = '{ticker}' AND date <= '2025-06-26'
            ORDER BY date
        """.format(ticker=ticker.ticker)
        df = pd.read_sql(query, db_conn)

        if len(df) < 50:
            print(f"Ticker {ticker.ticker} skipped, data kurang dari 50 hari")
            continue

        trading_state = bts.build(df, ticker.ticker)
        should_buy, signal_name, reason = bsg.evaluate_buy_signals(trading_state)
        
        if should_buy:
            print(f"✅ BUY SIGNAL for {ticker.ticker}: {signal_name} | {reason}")
            trade_plan = tp.generate_trade_plan(trading_state, signal_name)
            
            # save trade_log
            lt.log_trade_decision(trading_state, trade_plan)

        else:
            print(f"❌ No Buy Signal for {ticker.ticker}: {reason}")


        end = time.time()
        print(f"time elapsed for ticker {ticker.ticker} is {end - start}")

    realtime_data = migrate.read(save=False)
    realtime_data = pd.DataFrame(realtime_data)
    pa.update_trade_logs(realtime_data)

    exit(1)



if __name__ == "__main__":
    start()
    