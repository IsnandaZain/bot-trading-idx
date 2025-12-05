
def should_extended_tp(state: dict, original_tp: float) -> bool:
    """Tentukan apakah perlu menaikkan TP berdasarkan kondisi pasar saat ini"""

    price = state["price"]

    # if price <= original_tp:
    #     return False
    
    if not state.get("is_uptrend", False) and not price >= max(state["ma20"], state["ma50"], state["ma200"]) : # memastikan masih uptrend (ini terlalu kaku)
        return False
    
    if state["volume"] < state["vol_ma20"] * 0.6: # volume tidak cukup kuat
        return False
    
    if price < state["ma20"]:
        return False
    
    return True


def calculate_extended_tp(state: dict, original_entry: float, original_sl: float) -> bool:
    """
    Hitung TP lanjutan berdasarkan risk awal dan kekuatan tren
    Strategi: naikkan TP ke resistance berikutnya
    """
    print("major Resistances:", state["major_resistances"])
    # risk = original_entry - original_sl
    # if risk <= 0:
    #     return round(original_entry * 1.3, 0) # fallback
    
    # Opsi 1: gunakan resistance berikutnya
    if state["major_resistances"]:
        for res in state["major_resistances"]:
            if res > original_entry:
                return round(res, 0)
            

# def calculate_trailing_stop(state: dict, original_entry: float, original_sl: float) -> float:
#     """
#     Hitung ulang SL terbaru atau trailing stop berdasarkan kondisi pasar saat ini
#     Strategi: naikkan SL ke MA20 atau support terdekat
#     """
#     price = state["price"]
#     risk = original_entry - original_sl
#     if risk <= 0:
#         return original_sl
    
#     # Tentukan level SL baru
#     new_sl_candidates = []
#     max_ma = max(state["ma20"], state["ma50"], state["ma200"])
#     if max_ma and max_ma > original_sl:
#         new_sl_candidates.append(max_ma)

#     if state["nearest_support"] and state["nearest_support"] > original_sl:
#         new_sl_candidates.append(state["nearest_support"])

#     if new_sl_candidates:
#         return min(new_sl_candidates)

#     return original_sl

def calculate_trailing_stop(state: dict, original_entry: float, original_sl: float) -> float:
    from src.strategy import risk_management as rm

    # hitung jarak dari harga sekarang ke original_sl
    price = state["price"]
    perc_gain = (price - original_entry) / original_entry
    max_depth_pct = original_sl if perc_gain <= 0.05 else perc_gain * 0.5

    # untuk mencegah bias, hapus resistance yang menjadi support
    state["major_supports"] = state["major_supports"][1:]
    return rm.find_valid_sl_level(state, max_depth_pct=max_depth_pct)