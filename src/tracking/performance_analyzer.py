import pandas as pd
from datetime import datetime

from config import base as bs

def update_trade_logs(df: pd.DataFrame):
    # ambil semua sinyal buy yang masih aktif
    pending_trades = bs.session.query(bs.TradeLog).filter(
        bs.TradeLog.action == bs.TradeLog.ACTION_BUY,
        bs.TradeLog.valid == True,
        bs.TradeLog.outcome == None
    ).all()

    if not pending_trades:
        print("ℹ️ tidak ada sinyal aktif")
        return
    
    for trade in pending_trades:
        try:
            # Ambil harga terbaru dari dataframe
            current_price = df.loc[df['ticker'] == trade.ticker, 'close'].values[0]

            # Cek apakah sudah hit SL atau TP
            sl_hit = current_price <= trade.sl_price
            tp_hit = current_price >= trade.tp_price if trade.tp_price else False

            # Update outcome
            if sl_hit:
                trade.outcome = "SL"
                trade.exit_price = current_price
                trade.exit_timestamp = datetime.now()

            elif tp_hit:
                trade.outcome = "TP"
                trade.exit_price = current_price
                trade.exit_timestamp = datetime.now()

            # Simpan harga tertinggi sejak entry (untuk trailing stop di masa depan)
            if not hasattr(trade, 'highest_since_entry') or trade.highest_since_entry is None:
                trade.highest_since_entry = current_price
            else:
                trade.highest_since_entry = max(trade.highest_since_entry, current_price)

        except Exception as e:
            print(f"⚠️ Gagal memperbarui trade log untuk {trade.ticker}: {e}")
            continue

    # Simpan semua perubahan
    try:
        bs.session.commit()
        print("✅ Trade logs diperbarui")
    except Exception as e:
        bs.session.rollback()
        print(f"❌ Gagal menyimpan perubahan trade logs: {e}")




