import pandas as pd

from src.strategy import buy_signal as bs
from src.strategy import risk_management as rm
from src.strategy import build_trading_state as bts

from src.indicator import support_resistance as sr


def simulate_build_trading_state(df: pd.DataFrame, ticker: str):
    current_price = df["close"].iloc[-1]
    
    # price ma
    ma20 = int(df["close"].tail(20).mean())
    ma50 = int(df["close"].tail(50).mean()) if len(df) >= 50 else ma20
    ma200 = int(df["close"].tail(200).mean()) if len(df) >= 200 else ma50

    # volume ma
    vol_ma20 = int(df["volume"].tail(20).mean())
    
    # support resistance
    supports, resistances = sr.detect_support_resistance_robust(
        df=df.tail(200),
        current_price=current_price,
    )

    print(f"Supports: {supports}, Resistances: {resistances}")

    state = {
        "ticker": ticker,
        "price": current_price,
        "volume": df["volume"].iloc[-1],
        "volume_spike": False,

        # Support & Resistance
        "major_supports": supports,
        "major_resistances": resistances,
        "minor_supports": [],
        "minor_resistances": [],
        "nearest_support": min(supports) if supports else None,
        "nearest_resistance": min(resistances) if resistances else None,

        # Moving Avearge
        "ma20": ma20,
        "ma50": ma50,
        "ma200": ma200,
        "is_uptrend": bts.is_uptrend(ma20, ma50, ma200),
        "is_downtrend": bts.is_downtrend(ma20, ma50, ma200),
        
        # Volume Average
        "vol_ma20": vol_ma20,
        "vol_ma50": 0,
        "vol_ma200": 0,

        # Konteks
        "date": df.index[-1],
        "has_enough_data": len(df) >= 200,
    }

    # validasi candle
    prev_close = df['close'].iloc[-2]
    prev_low = df['low'].iloc[-2]
    current_open = df['open'].iloc[-1]
    current_close = df['close'].iloc[-1]
    current_low = df['low'].iloc[-1]

    # Hammer: lower shadow panjang
    is_hammer = (current_close > current_open) and \
                (current_low < min(prev_close, current_open) - (current_close - current_open) * 2)
    state['is_bullish_candle'] = is_hammer or (current_close > prev_close)

    return state

