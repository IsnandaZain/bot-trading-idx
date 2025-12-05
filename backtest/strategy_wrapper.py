import pandas as pd

from src.strategy import buy_signal as bs
from src.strategy import risk_management as rm
from src.strategy import build_trading_state as bts

from src.indicator import support_resistance as sr
from src.indicator import ma as ma_indicator
from src.indicator import helper


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

    state = {
        "ticker": ticker,
        "price": current_price,
        "price_prev": df['close'].iloc[-2] if len(df) >=2 else df['close'].iloc[-1],
        "high": df['high'].iloc[-1],
        "low": df['low'].iloc[-1],
        "volume": df["volume"].iloc[-1],
        "volume_spike": False,

        # Support & Resistance
        "major_supports": supports,
        "major_resistances": resistances,
        "minor_supports": [],
        "minor_resistances": [],
        "nearest_support": max(supports) if supports else None,
        "nearest_resistance": min(resistances) if resistances else None,

        # Moving Avearge
        "ma20": ma20,
        "ma50": ma50,
        "ma200": ma200,
        "is_uptrend": bts.is_uptrend(ma20, ma50, ma200),
        "is_downtrend": bts.is_downtrend(ma20, ma50, ma200),
        "is_ma200_uptrend": False,
        
        # Volume Average
        "vol_ma20": vol_ma20,
        "vol_ma50": 0,
        "vol_ma200": 0,

        # Konteks
        "date": df.index[-1],
        "has_enough_data": len(df) >= 200,
    }

    # validasi volume spike
    state["volume_spike"] = helper.is_volume_spike(
        volume_today=state["volume"],
        volume_ma20=state["vol_ma20"]
    )

    # validasi candle
    prev_close = df['close'].iloc[-2]
    prev_low = df['low'].iloc[-2]
    current_open = df['open'].iloc[-1]
    current_close = df['close'].iloc[-1]
    current_low = df['low'].iloc[-1]

    # Update is_ma200_uptrend
    state["is_ma200_uptrend"] = ma_indicator.is_ma200_uptrend(
        df=df,
        ma_col="ma200",
        lookback_ma=200,
        lookback_days=30,
        min_slope_pct=0.05
    )

    # Hammer: lower shadow panjang
    is_hammer = (current_close > current_open) and \
                (current_low < min(prev_close, current_open) - (current_close - current_open) * 2)
    state['is_bullish_candle'] = is_hammer or (current_close > prev_close)

    # print(f"Supports: {supports}, Resistances: {resistances} - nearest_support: {state['nearest_support']}, nearest_resistance: {state['nearest_resistance']}")
    # print(f"MA20: {ma20}, MA50: {ma50}, MA200: {ma200}, VolMA20: {vol_ma20}")
    # print(f"is_bullish_candle: {state['is_bullish_candle']}, volume_spike: {state['volume_spike']}")

    return state

