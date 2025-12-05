import pandas as pd
from datetime import timedelta

from src.strategy import buy_signal as bs
from src.strategy import risk_management as rm
from src.strategy import profit_management as pm

from backtest import strategy_wrapper as sw

def run_backtest_for_ticker(df, ticker, initial_capital=20000000):
    trades = []
    capital = initial_capital
    active_trades = 0
    daily_loss = 0
    max_trades_per_day = 3
    max_daily_loss = 300000

    # iterasi setiap hair
    i = 200
    while i < len(df):
        today = df.index[i]
        df_slice = df.iloc[:i+1]
        print(f"{i} Memproses {ticker} untuk tanggal {today.date()} length data : {len(df_slice)}")
        # print(df_slice.head())

        # reset daily loss jika hari baru
        if i == 200 or df.index[i].date() != df.index[i-1].date():
            daily_loss = 0

        # bangun state trading
        state = sw.simulate_build_trading_state(df_slice, ticker)
        if not state or not state["has_enough_data"]:
            print(f"Data tidak cukup untuk {ticker} pada tanggal {today.date()} \n")
            i += 1
            continue

        # evaluasi sinyal
        should_buy, signal_name, _ = bs.evaluate_buy_signals(state)
        if not should_buy:
            print(f"Tidak ada sinyal beli untuk {ticker} pada tanggal {today.date()} \n")
            i += 1
            continue

        # Hitung SL/TP
        sl_price = int(rm.calculate_stop_loss(state, signal_name))
        tp_price = int(rm.calculate_take_profit(state, sl_price, signal_name))
        lot_size, actual_risk = rm.calculate_lot_size(
            entry_price=state["price"],
            sl_price=round(sl_price, 0) if sl_price else state["price"],
            risk_rupiah=100000
        )

        if lot_size < 1 or actual_risk == 0:
            i += 1
            continue

        # Simulasi eksekusi: entry di close hari ini
        entry_price = state["price"]

        # Cari kapan TP/SL tersentuh di masa depan
        exit_price = None
        exit_date = None
        outcome = "HOLD"

        print(f"Memasuki posisi untuk {ticker} pada tanggal {today.date()} \n \
              berdasarkan sinyal {signal_name} \n \
              dengan lot size {lot_size}, SL: {sl_price}, TP: {tp_price} \n \
              entry_price: {entry_price}")

        # Enhance masa tunggu exit: maksimal 10hari dari penentuan TP
        j = i+1
        max_hold_days = 10
        days_held = 0

        while j < len(df) and days_held <= max_hold_days:
            # update indeks agar tidak double count hari yang sama
            i = j

            future_price = df['close'].iloc[j]
            future_high = df['high'].iloc[j]
            future_low = df['low'].iloc[j]
            # print(f"  Memeriksa harga di tanggal {df.index[j].date()} : close {future_price}, high {future_high}, low {future_low}")

            # Cek SL/TP diharga high/low (lebih realistis)
            if future_low <= sl_price:
                exit_price = sl_price
                exit_date = df.index[j]
                outcome = "SL"

                i = j
                break
            
            elif tp_price and future_high >= tp_price:

                # penerapan extend TP
                # generate state untuk kebutuhan extended TP dan trailing stop
                state = sw.simulate_build_trading_state(df.iloc[:j+1], ticker)
                print(f"state untuk extended TP {state['date']}: {state['price']}, {state['ma20']}, {state['vol_ma20']}, {state['is_uptrend']}")
                if pm.should_extended_tp(state, tp_price):
                    tp_price = pm.calculate_extended_tp(state, entry_price, sl_price)
                    sl_price = pm.calculate_trailing_stop(state, entry_price, sl_price)
                    print(f"Memperpanjang TP untuk {ticker} pada tanggal {df.index[j].date()} menjadi {tp_price} dan trailing_stop menjadi {sl_price}")
                    
                    max_hold_days = days_held + 10

                else:
                    exit_price = tp_price
                    exit_date = df.index[j]
                    outcome = "TP"
                    break

            j += 1
            days_held += 1

        # Jika tidak exit dalam 10 hari, exit di close hari ke 10
        if not exit_price:
            j = min(i+10, len(df)-1)
            exit_price = df['close'].iloc[j]
            exit_date = df.index[j]
            outcome = "TIME_EXIT"

            # update indeks agar tidak double count hari yang sama
            i = j

        # Hitung PnL
        pnl = (exit_price - entry_price) * lot_size * 100
        daily_loss += abs(pnl) if pnl < 0 else 0
        active_trades += 1

        trades.append({
            "ticker": ticker,
            "entry_date": today,
            "exit_date": exit_date,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "sl_price": sl_price,
            "signal": signal_name,
            "lot_size": lot_size,
            "porto_value": entry_price * lot_size * 100,
            "outcome": outcome,
            "pnl": pnl,
            "risk": actual_risk
        })

    return trades

