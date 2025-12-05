import math
from typing import Tuple, Optional

def calculate_stop_loss(state: dict, signal_name: str) -> float:
    """Tentukan SL berdasarkan jenis sinyal buy"""
    price = state["price"]
    
    # Confluence Zone
    if signal_name == "Confluence Zone":
        return find_valid_sl_level(state, max_depth_pct=0.06)
        
    # Breakout
    elif signal_name == "Breakout":
        if state["major_resistances"]:
            breakout_level = state["major_resistances"][0]
            return breakout_level * 0.98
        
        else:
            return price * 0.97
        
    # Pullback Strong Trend
    elif signal_name == "Pullback Strong Trend":
        if state["ma20"]:
            return state["ma20"] * 0.98
        else:
            return price * 0.97
        
    # Triple Confirmation atau Support Reversal
    elif signal_name in ["Triple Confirmation", "Support Reversal"]:
        return find_valid_sl_level(state, max_depth_pct=0.06)
        
    # Untuk HIGH RISK
    # Breakdown Reversal
    elif signal_name == "Breakdown Reversal":
        return state["ma20"] * 0.99
        
    else:
        if state["nearest_support"]:
            return state["nearest_support"] * 0.98
        return price * 0.97
    


def calculate_take_profit(state: dict, sl_price: float, signal_name: str):
    """Tentukan TP berdasarkan jenis sinyal buy"""
    price = state["price"]
    risk = price - sl_price
    if risk <= 0:
        return None
    
    # Breakout
    if signal_name == "Breakout":
        if len(state["major_resistances"]) > 1:
            next_resistance = state["major_resistances"][1]
            if next_resistance > price:
                return next_resistance
            
        # Fallback
        return price + (risk * 3)
    
    # Confluence Zone atau Triple Confirmation
    elif signal_name in ["Confluence Zone", "Triple Confirmation"]:
        if state["major_resistances"]:
            resistance = state["major_resistances"][0]
            if resistance > price:
                return resistance
            
        # Fallback
        return price + (risk * 2)
    
    # Pullback Strong Trend
    elif signal_name == "Pullback Strong Trend":
        if state["major_resistances"]:
            resistance = state["major_resistances"][0]
            if resistance > price:
                min_tp = price + (risk * 2)
                return max(resistance, min_tp)
            
        # Fallback
        return price + (risk * 2)
    
    # Default
    else:
        if state["major_resistances"]:
            resistance = state["major_resistances"][0]
            if resistance > price:
                return resistance
            
        return price + (risk * 2)
    

def calculate_lot_size(entry_price: int, sl_price: int, risk_rupiah: int = 100000):
    """
    Hitung lot size berdasarkan fixed risk Rp. 100.000
    Returns:
        (lot_size: int, actual_risk: float)
    """
    if sl_price >= entry_price:
        return 0, 0.0
    
    risk_per_share = entry_price - sl_price
    if risk_per_share <= 0:
        return 0, 0.0
    
    # 1 lot = 100 saham
    lot_size = risk_rupiah / (risk_per_share * 100)
    lot_size = math.floor(lot_size)

    actual_risk = lot_size * risk_per_share * 100
    return max(0, int(lot_size)), actual_risk
    

def find_valid_sl_level(state: dict, max_depth_pct: float = 0.05) -> int:
    """
    Cari level SL valid dalam radius max_depth_pct dibawah harga
    Kandidat: support, MA20, MA50, MA200
    """
    price = state["price"]
    min_level = int(price * (1 - max_depth_pct))
    candidates = []

    print(f"Finding SL level below {price} down to {min_level}")

    # Tambahkan semua supports
    if state['major_supports']:
        for support in state['major_supports']:
            if min_level <= support < price:
                candidates.append(support)

    # Tambahkan MA yang dalam radius
    for ma in ['ma20', 'ma50', 'ma200']:
        ma_val = state.get(ma)
        if ma_val and min_level <= ma_val < price:
            candidates.append(ma_val)

    if candidates:
        return min(candidates) * 0.99
    
    return round(price * (1 - max_depth_pct), 0)