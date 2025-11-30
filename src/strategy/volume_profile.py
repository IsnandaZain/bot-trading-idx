from typing import Optional

def get_volume_threshold(
    sector: Optional[str] = None,
    signal_type: Optional[str] = None,
    base_threshold: float = 0.8
) -> float:
    """
    Tentukan threshold volume minimum berdasarkan sektor dan jenis sinyal.
    
    Returns:
        float: multiplier untuk vol_ma20 (misal: 0.6 berarti volume >= 60% dari rata-rata)
    """
    # Normalisasi input
    sector = (sector or "Others").strip().title()
    signal_type = (signal_type or "").strip()

    # Default threshold
    threshold = base_threshold

    # === 1. Sesuaikan berdasarkan SEKTOR ===
    SECTOR_THRESHOLDS = {
        'Banking': 0.85,      # Volume tinggi → jangan terlalu longgar
        'Consumer': 0.80,     # Stabil → pertahankan standar
        'Automotive': 0.80,
        'Telecommunication': 0.80,
        'Property': 0.60,     # Volume rendah → longgarkan
        'Mining': 0.60,       # Volatile + volume fluktuatif
        'Infrastructure': 0.70,
        'Manufacturing': 0.70,
        'Others': 0.75
    }

    threshold = SECTOR_THRESHOLDS.get(sector, base_threshold)

    # === 2. Sesuaikan berdasarkan JENIS SINYAL ===
    if signal_type:
        # Sinyal yang boleh lebih longgar (akumulasi, mean reversion)
        if signal_type in [
            "Mean Reversion Blue-Chip",
            "Accumulation Zone",
            "Support Reversal"
        ]:
            threshold = min(threshold, 0.65)  # maksimal longgar sampai 0.65
        
        # Sinyal yang butuh volume tinggi → jangan turunkan!
        elif signal_type in [
            "Breakout",
            "Triple Confirmation"
        ]:
            threshold = max(threshold, 0.90)  # minimal 90%

    # === 3. Batasan akhir ===
    # Jangan pernah terlalu ekstrem
    threshold = max(0.5, min(1.0, threshold))

    return round(threshold, 2)