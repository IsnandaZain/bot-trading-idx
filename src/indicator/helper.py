
SECTOR_VOLUME_MULTIPLIER = {
    'Banking': 1.8,       # Volume tinggi → butuh spike besar
    'Consumer': 1.5,
    'Automotive': 1.5,
    'Property': 2.5,      # Volume rendah → spike lebih ekstrem
    'Mining': 2.0,
    'Others': 1.5
}

def is_volume_spike_adaptive(
    volume_today: int, 
    volume_ma20: int, 
    sector: str = "Others",
    base_multiplier: float = 1.5
) -> bool:
    multiplier = SECTOR_VOLUME_MULTIPLIER.get(sector, base_multiplier)
    return volume_today >= volume_ma20 * multiplier


def is_volume_spike_volatility_based(
    volume_today: int,
    volume_ma20: int,
    price_change_pct: float,  # perubahan harga hari ini (%)
    min_vol_ratio: float = 1.2
) -> bool:
    """
    Jika harga bergerak >2%, volume harus >1.2x.
    Jika harga sideways, volume harus >2x untuk dianggap spike.
    """
    if abs(price_change_pct) > 2.0:
        required_mult = 1.2
    elif abs(price_change_pct) < 0.5:
        required_mult = 2.0  # sideways but volume spike = akumulasi
    else:
        required_mult = 1.5
    
    return volume_today >= volume_ma20 * required_mult

# Menentukan apakah volume saat ini spike atau tidak
def is_volume_spike(volume_today: int, volume_ma20: int, multiplier: float = 1.5) -> bool:
    """
    Volume spike jika > 1.5x rata-rata 20 hari.
    """
    return volume_today >= volume_ma20 * multiplier