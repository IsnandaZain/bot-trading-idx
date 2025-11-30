import json
from datetime import datetime
from typing import Dict, Optional

from config import base as bs

def log_trade_decision(state: Dict, trade_plan: Dict):
    # Siapkan data snapshot
    log_entry = bs.TradeLog(
        timestamp=datetime.now(),
        ticker=state["ticker"],
        signal_type=trade_plan.get("signal_name", ""),
        action=trade_plan.get("action", "BUY"),
        entry_price=int(trade_plan.get("entry_price", 0)),
        sl_price=int(trade_plan.get("sl_price", 0)),
        tp_price=int(trade_plan.get("tp_price", 0)),
        lot_size=int(trade_plan.get("lot_size", 0)),

        # Snapshot Kondisi Pasar
        price=int(state.get("price", 0)),
        ma20=int(state.get("ma20", 0)),
        ma50=int(state.get("ma50", 0)),
        ma200=int(state.get("ma200", 0)),
        volume=int(state.get("volume", 0)),
        volume_ma20=int(state.get("vol_ma20", 0)),
        supports=",".join(str(st) for st in state.get("major_supports", [])),
        resistances=",".join(str(st) for st in state.get("major_resistances", []))
    )

    bs.session.add(log_entry)
    bs.session.commit()
    