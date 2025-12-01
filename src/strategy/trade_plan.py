from  src.strategy import risk_management as rm


def generate_trade_plan(state: dict, signal_name: str) -> dict:
    entry_price = state["price"]
    sl_price = rm.calculate_stop_loss(state, signal_name)
    tp_price = rm.calculate_take_profit(state, sl_price, signal_name)
    lot_size, actual_risk = rm.calculate_lot_size(
        entry_price=entry_price,
        sl_price=round(sl_price, 0) if sl_price else entry_price,
        risk_rupiah=100000
    )

    # validasi
    return {
        "ticker": state["ticker"],
        "signal_name": signal_name,
        "action": "BUY",
        "entry_price": entry_price,
        "sl_price": round(sl_price, 0) if sl_price else None,
        "tp_price": round(tp_price, 0) if tp_price else None,
        "lot_size": lot_size
    }