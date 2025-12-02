import pandas as pd
import sqlalchemy

from config import configuration as cfg

from backtest import backtest_engine as be
from backtest import performance_analyzer as pa

# Konfigurasi
TICKERS = ["TOBA"]
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


def main():
    all_trades = []
    for ticker in TICKERS:
        print(f"🔄 Memulai backtest untuk {ticker}...")
        df = pd.read_sql(
            f"SELECT date, open, high, low, close, volume FROM data_histories WHERE ticker = '{ticker}' ORDER BY date",
            db_conn,
            parse_dates=["date"],
            index_col="date"
        )

        print(df.head())
        print("\n")
        print(df.tail())

        if df.empty:
            print(f"⚠️  Tidak ada data untuk {ticker}")
            continue

        trades = be.run_backtest_for_ticker(df=df, ticker=ticker)
        all_trades.append(trades)
        print(f"✅ Backtest selesai untuk {ticker}, total trades: {len(trades)}")

    # generate laporan akhir
    pa.generate_performance_report(all_trades[0])



if __name__ == "__main__":
    main()