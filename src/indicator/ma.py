import pandas as pd
from datetime import date
from sqlalchemy import text


def calculate_ma_va(df: pd.DataFrame, current_price: int):
    """
    Hitung MA harga & volume untuk semua ticker atau satu ticker.
    Simpan hanya jika data cukup.
    """
    n = len(df)

    # hitung MA harga
    ma20 = df['close'].tail(20).mean() if n >= 20 else current_price
    ma50 = df['close'].tail(50).mean() if n >= 50 else ma20
    ma200 = df['close'].tail(200).mean() if n >= 200 else ma50

    # hitung VA volume
    vol_ma20 = int(df['volume'].tail(20).mean()) if n >= 20 else int(df['volume'].mean())
    vol_ma50 = int(df['volume'].tail(50).mean()) if n >= 50 else vol_ma20
    vol_ma200 = int(df['volume'].tail(200).mean()) if n >= 200 else vol_ma50

    # print(f"MA20: {ma20}, MA50: {ma50}, MA200: {ma200}")
    # print(f"VA20: {vol_ma20}, VA50: {vol_ma50}, VA200: {vol_ma200}")

    return [round(ma20), round(ma50), round(ma200)], [vol_ma20, vol_ma50, vol_ma200]