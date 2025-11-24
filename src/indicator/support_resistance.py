import pandas as pd
import json
from datetime import date, timedelta
from sqlalchemy import text
from typing import List, Tuple, Optional


def is_support(df: pd.DataFrame, i: int, window: int = 2) -> bool:
    """Cek apakah titik ke-i adalah support"""
    if i < window or i + window >= len(df):
        return False
    left_min = df['low'].iloc[i - window:i].min()
    right_min = df['low'].iloc[i + 1:i + 1 + window].min()
    return df['low'].iloc[i] <= min(left_min, right_min)


def is_resistance(df: pd.DataFrame, i: int, window: int = 2) -> bool:
    """Cek apakah titik ke-i adalah resistance"""
    if i < window or i + window >= len(df):
        return False
    left_max = df['high'].iloc[i - window:i].max()
    right_max = df['high'].iloc[i + 1:i + 1 + window].max()
    return df['high'].iloc[i] >= max(left_max, right_max)


def merge_levels(levels: List[float], threshold_pct: float = 0.01) -> List[float]:
    """Gabungkan level-level yang berdekatan berdasarkan threshold persentase"""
    if not levels:
        return []

    levels = sorted(set(levels))
    merged = []
    current_group = [levels[0]]

    for price in levels[1:]:
        last_in_group = current_group[-1]
        if (price - last_in_group) / last_in_group <= threshold_pct:
            current_group.append(price)
        else:
            # Simpan rata-rata kelompok
            merged.append(sum(current_group) / len(current_group))
            current_group = [price]

    merged.append(sum(current_group) / len(current_group))
    return merged


def get_price_volatility(df: pd.DataFrame) -> float:
    """Hitung volatilitas harga sebagai standar deviasi perubahan harga"""
    df = df.copy()
    df['tr'] = df['high'] - df['low']
    return df['tr'].mean()


def detect_support_resistance_robust(
    tickers: str,
    df: pd.DataFrame,
    current_price: float,
    days: int = 200, 
    min_volume_multiplier: float = 1.0
) -> Tuple[Optional[float], Optional[float]]:
    """Deteksi level support dan resistance menggunakan metode robust"""
    
    # Hitung rata-rata volume untuk filter
    avg_volume = df['volume'].mean()
    window = 2
    supports, resistances = [], []

    for i in range(window, len(df) - window):
        vol_ok = df['volume'].iloc[i] >= avg_volume * min_volume_multiplier

        if vol_ok and is_support(df, i, window):
            supports.append(int(df['low'].iloc[i]))
        if vol_ok and is_resistance(df, i, window):
            resistances.append(int(df['high'].iloc[i]))

    # Threshold dinamis berdasarkan volatilitas (~1% default, tapi bisa disesuaikan)
    volatility = get_price_volatility(df)
    current_price = df['close'].iloc[-1]
    threshold_pct = max(0.005, volatility / current_price)

    # gabung level berdekatan
    all_levels = merge_levels(supports + resistances, threshold_pct=threshold_pct)

    # Pisahkan berdasarkan harga saat ini
    supports = [round(level) for level in all_levels if level < current_price]
    resistances = [round(level) for level in all_levels if level > current_price]

    # Urutkan: supports dari tinggi ke rendah, resistances dari rendah ke tinggi
    supports = sorted(supports, reverse=True)
    resistances = sorted(resistances)

    return supports, resistances


def update_support_resistance_in_db(
        ticker: str, 
        supports: List[float], 
        resistances: List[float], 
        db_session
):
    """Simpan hasil ke database sebagai json"""
    from config.base import SupportResistance

    today = date.today()
    existing = db_session.query(SupportResistance).filter(
        SupportResistance.ticker == ticker
    ).first()

    data = {
        "supports": [round(p, 2) for p in supports],
        "resistances": [round(p, 2) for p in resistances],
        "last_updated": today.isoformat()
    }

    if existing:
        existing.support = json.dumps(data)
        existing.data = today
    else:
        new_record = SupportResistance(
            ticker=ticker,
            support=json.dumps(data),
            data=today
        )
        db_session.add(new_record)

    db_session.commit()


def detect_support_resistance(db_conn, db_session, select_ticker: Optional[str] = None, days: int = 200):
    """Fungsi utama: deteski S/R untuk semua ticker atau satu ticker"""
    if select_ticker:
        tickers = [select_ticker]
    else:
        from config.base import MasterTicker
        tickers = [mt.ticker for mt in db_session.query(MasterTicker).all()]

    print(f"🔍 Memproses {len(tickers)} ticker untuk Support & Resistance...")

    for ticker in tickers:
        try:
            supports, resistances = detect_support_resistance_robust(
                tickers, db_conn, days=days
            )
            update_support_resistance_in_db(ticker, supports, resistances, db_session)
            print(f"✅ {ticker}: S({len(supports)}) R({len(resistances)})")
        except Exception as e:
            print(f"❌ Gagal memproses {ticker}: {str(e)}")
            continue


    print("✅ Support & Resistance telah diperbarui.")