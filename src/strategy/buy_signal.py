from typing import Tuple, Optional


"""
Penjelasan Signal Buy Berdasarkan Prioritas
Prioritas - Sinyal - Alasan
1 - Confluence Zone - Paling akurat, risk-reward terbaik, jarang muncul -> utamakan
2 - Triple Confirmation - Seimbang antara keamanan dan frekuensi
3 - Pullback Strong Trend - Cocok untuk saham konglomerasi yang sering tren kuat
4 - Support Reversal - Lebih reaktif, tapi butuh konfirmasi candle / RSI
5 - Breakout - Paling beresiko -> hanya jika tidak ada sinyal lain

OPSIONAL
6 - Accumulation - Deteksi akumulasi institutional
7 - Catalyst - Gabung Fundamental + Teknikal
8 - Mean Reversion Blue-Chip - Khusus saham konglomerasi
"""

def buy_signal_confluence(state: dict) -> bool:
    """Opsi 1: Confluence Zone (Presisi Tinggi)"""
    if not state["nearest_support"]:
        return False
    
    # Support minor dekat MA50 (dalam 1%)
    ma50 = state["ma50"]
    support = state["nearest_support"]
    confluence = abs(support - ma50) / ma50 <= 0.05

    # Tren menengah bullish
    trend_ok = state["ma50"] >= state["ma200"]

    # Volume spike + RSI / Stoch oversold
    # rsi_ok = state["rsi"] is not None and state["rsi"] < 30
    # stoch_ok = (
    #     state['stoch_k'] is not None and 
    #     state['stoch_k'] < 30 and 
    #     state['stoch_k'] > (state['stoch_d'] or 0)
    # )

    return (
        confluence and
        trend_ok and
        state['volume_spike']
    )

def buy_signal_triple_confirmation(state: dict) -> bool:
    """Opsi 2: Triple Confirmation"""
    return (
        state["is_uptrend"] and
        state['volume_spike'] and
        state["nearest_support"] and
        state["price"] > state["ma20"]
    )

def buy_signal_pullback_strong_trend(state: dict) -> bool:
    """Opsi 3: Pullback dalam Tren Kuat"""
    # Tren sangat kuat
    strong_trend = state["is_uptrend"]

    if not state["major_resistances"]: # jika tidak ada resistance maka auto tidak valid
        return False

    # Pullback ke MA20
    near_ma20 = (
        state["price"] >= state["ma20"] and           # harga di atas MA20
        state["price"] <= state["ma20"] * 1.05        # tapi tidak lebih dari 3% di atas
    )

    # Belum dekat resistance
    not_near_resistance = state["price"] <= state["major_resistances"][0] * 0.95

    # Volume tidak anjlok
    volume_ok = state["volume"] >= state["vol_ma20"] * 0.5

    return strong_trend and near_ma20 and not_near_resistance and volume_ok

def buy_signal_support_reversal(state: dict) -> bool:
    """Opsi 4: Reversal di Support"""
    # Asumsi: candle bullish sudah diverifikasi diluar (misal: via OHLC)
    # Disini kita fokus pada support
    if not state["is_bullish_candle"]:
        return False
    
    if not state["nearest_support"]:
        return False
    
    near_support = (
        state["price"] >= state["nearest_support"] and
        state["price"] <= state["nearest_support"] * 1.05
    )
    
    return (
        near_support and
        state["volume_spike"]
    )

def buy_signal_breakout(state: dict) -> bool:
    """Opsi 5: Breakout"""
    if not state["major_resistances"] and not state["minor_resistances"]:
        return False
    
    # Harga sudah tembus resistance terdekat
    resistance = state["nearest_resistance"]
    breakout = state["price"] > resistance * 1.01

    # volume sangat tinggi
    high_volume = state["volume"] >= state["vol_ma20"] * 1.25

    # filter tren jangka panjang
    trend_ok = state["ma20"] > state["ma200"]
    return breakout and high_volume and trend_ok


# Prioritas
BUY_SIGNAL_PRIORITIES = [
    ("Confluence Zone", buy_signal_confluence),
    ("Tiple Confirmation", buy_signal_triple_confirmation),
    ("Pullback Strong Trend", buy_signal_pullback_strong_trend),
    ("Support Reversal", buy_signal_support_reversal),
    ("Breakout", buy_signal_breakout),
]

# SIGNAL HIGH RISK
def buy_signal_false_breakdown_reversal(state: dict) -> bool:
    """Opsi 6: False Breakdown Reversal"""
    # Asumsi: candle bullish sudah diverifikasi diluar (misal: via OHLC)
    # Disini kita fokus pada support
    if not (state["ma200"] >= state["ma50"] > state["ma20"]):
        return False
    
    if state["price"] <= state["ma20"]:
        return False
    
    # volume rebound kuat
    if not state["volume_spike"]:
        return False
    
    return True


BUY_SIGNAL_HIGH_RISK = [
    ("Breakdown Reversal", buy_signal_false_breakdown_reversal),
]

def evaluate_buy_signals(state: dict) -> Tuple[bool, str, Optional[str]]:
    """
    Evaluasi semua sinyal buy dengan prioritas
    Returns:
        (should_buy: bool, signal_name: str, reason: str)
    """
    # Cek setiap sinyal sesuai prioritas
    for signal_name, signal_func in BUY_SIGNAL_PRIORITIES:
        if signal_func(state):
            return True, signal_name, f"Buy signal: {signal_name} detected."
        
    for signal_name, signal_func in BUY_SIGNAL_HIGH_RISK:
        if signal_func(state):
            return True, signal_name, f"High Risk Buy signal: {signal_name} detected."
        
    return False, "", "Tidak ada sinyal buy yang valid"