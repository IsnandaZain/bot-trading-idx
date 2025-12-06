

def normalize_price(price: float) -> float:
    # Aturan BEI untuk tick size
    if price <= 200:
        tick_size = 1
    elif price <= 500:
        tick_size = 2
    elif price <= 2000:
        tick_size = 5
    elif price <= 5000:
        tick_size = 10
    else:
        tick_size = 25

    # Gunakan round() untuk pembulatan ke terdekat
    normalized = round(price / tick_size) * tick_size
    return int(normalized)