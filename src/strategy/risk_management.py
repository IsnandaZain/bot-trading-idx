import math
from typing import Tuple, Optional

def calculate_stop_loss(state: dict, signal_name: str) -> float:
    """Tentukan SL berdasarkan jenis sinyal buy"""
    price = state["price"]
    
    # Confluence Zone
    if signal_name == "Confluence Zone":
        if state["nearest_support"] and state["ma50"]:
            confluence_level = min(state["nearest_support"], state["ma50"])
            return confluence_level * 0.98
        elif state["nearest_support"]:
            return state["nearest_support"] * 0.98
        else:
            return price * 0.97
        
    # Breakout
    elif signal_name == "Breakout":
        if state["resistances"]:
            breakout_level = state["resistances"][0]
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
        if state["nearest_support"]:
            return state["nearest_support"] * 0.98
        else:
            return price * 0.97
        
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
        if len(state["resistance"]) > 1:
            next_resistance = state["resistances"][1]
            if next_resistance > price:
                return next_resistance
            
        # Fallback
        return price + (risk * 3)
    
    # Confluence Zone atau Triple Confirmation
    elif signal_name in ["Confluence Zone", "Triple Confirmation"]:
        if state["resistances"]:
            resistance = state["resistance"][0]
            if resistance > price:
                return resistance
            
        # Fallback
        return price + (risk * 2)
    
    # Pullback Strong Trend
    elif signal_name == "Pullback Strong Trend":
        if state["resistances"]:
            resistance = state["resistances"][0]
            if resistance > price:
                min_tp = price + (risk * 2)
                return max(resistance, min_tp)
            
        # Fallback
        return price + (risk * 2)
    
    # Default
    else:
        if state["resistances"]:
            resistance = state["resistances"][0]
            if resistance > price:
                return resistance
            
        return price + (risk * 2)
    
    