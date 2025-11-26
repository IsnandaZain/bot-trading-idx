import datetime

import pandas as pd

from src.indicator import support_resistance as sr
from src.indicator import ma, rsi, helper




def build(df: pd.DataFrame, ticker: str):
    detail = {
        "ticker": ticker,
        "price": df['close'].iloc[-1],
        "volume": df['volume'].iloc[-1],
        "volume_spike": False,

        # Support & Resistance
        # supports : 500, 400, 300
        # resistances : 300, 400, 500
        "major_supports": [],
        "major_resistances": [],
        "minor_supports": [],
        "minor_resistances": [],
        "nearest_support": None,
        "nearest_resistance": None,

        # Moving Average
        "ma20": 0,
        "ma50": 0,
        "ma200": 0,
        "is_uptrend": False,
        "is_downtrend": False,
        
        # Volume Average
        "vol_ma20": 0,
        "vol_ma50": 0,
        "vol_ma200": 0,
        
        # Konteks
        "date": datetime.date.today(),
    }

    # columns = ['id', 'ticker', 'open', 'high', 'low', 'close', 'volume', 'date']
    # generate support-resistance
    major_supports, major_resistances = sr.detect_support_resistance_robust(
        df=df.tail(200),
        current_price=df['close'].iloc[-1],
    )

    detail["major_supports"] = major_supports
    detail["major_resistances"] = major_resistances

    # get minor support
    minor_supports, minor_resistances = sr.detect_support_resistance_robust(
        df=df.tail(50),
        current_price=df['close'].iloc[-1],
    )

    detail["minor_supports"] = minor_supports
    detail["minor_resistances"] = minor_resistances

    # get nearest support & resistance
    nearest_supports = []
    if detail["major_supports"]:
        nearest_supports.append(detail["major_supports"][-1])

    if detail["minor_supports"]:
        nearest_supports.append(detail["minor_supports"][-1])

    nearest_resistances = []
    if detail["major_resistances"]:
        nearest_resistances.append(detail["major_resistances"][0])

    if detail["minor_resistances"]:
        nearest_resistances.append(detail["minor_resistances"][0])

    detail["nearest_support"] = min(nearest_supports)
    detail["nearest_resistance"] = min(nearest_resistances)

    # generate moving average dan volume average
    detail["ma20"], detail["ma50"], detail["ma200"], detail["vol_ma20"], detail["vol_ma50"], detail["vol_ma200"] = ma.calculate_ma_va(
        df=df,
        current_price=df['close'].iloc[-1]
    )

    detail["volume_spike"] = helper.is_volume_spike(
        volume_today=detail["volume"],
        volume_ma20=detail["vol_ma20"]
    )

    # validasi candle
    prev_close = df['close'].iloc[-2]
    prev_low = df['low'].iloc[-2]
    current_open = df['open'].iloc[-1]
    current_close = df['close'].iloc[-1]
    current_low = df['low'].iloc[-1]

    # Hammer: lower shadow panjang
    is_hammer = (current_close > current_open) and \
                (current_low < min(prev_close, current_open) - (current_close - current_open) * 2)
    detail['is_bullish_candle'] = is_hammer or (current_close > prev_close)

    return detail