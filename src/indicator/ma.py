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

    return round(ma20), round(ma50), round(ma200), vol_ma20, vol_ma50, vol_ma200



def is_ma200_uptrend(df: pd.DataFrame, ma_col: str = "ma200",  lookback_ma: int = 200,
                     lookback_days: int = 30, min_slope_pct: float = 0.05) -> bool:
    """
    Deteksi apakah MA200 sedang dalam tren naik.
    
    Parameters:
        df (pd.DataFrame): DataFrame yang berisi kolom MA200
        ma_col (str): Nama kolom MA200 (default: 'ma200')
        lookback_days (int): Periode evaluasi tren (default: 30 hari)
        min_slope_pct (float): Minimal kenaikan persentase dalam periode (default: 2%)
    
    Returns:
        bool: True jika MA200 uptrend, False jika tidak
    """

    # Butuh data minimal: lookback_ma + lookback_trend
    min_data = lookback_ma + lookback_days
    if len(df) < min_data:
        return False
    
    # Hitung MA200 untuk seluruh data
    ma200_series = df["close"].rolling(window=lookback_ma, min_periods=lookback_ma).mean()
    
    # Ambil MA200 untuk periode trend
    recent_ma200 = ma200_series.tail(lookback_days).dropna()
    if len(recent_ma200) < lookback_days:
        return False
    
    # Bandingkan MA200 diawal vs akhir periode
    start_ma = recent_ma200.iloc[0]
    end_ma = recent_ma200.iloc[-1]

    if start_ma <= 0:
        return False
    
    growth_pct = (end_ma - start_ma) / start_ma
    print(growth_pct)
    return growth_pct >= min_slope_pct

