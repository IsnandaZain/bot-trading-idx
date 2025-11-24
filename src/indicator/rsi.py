import pandas as pd
import pandas_ta as ta


def calculate_rsi(data_histories: pd.DataFrame, period: int = 14, lookback_days: int = 180):

    """
    Ambil data dari DB, hitung RSI dan StochRSI, kembalikan baris terbaru.

    Parameters:
        db_session: SQLAlchemy session
        ticker: str (misal: 'BBCA')
        period: int (default 14 untuk RSI/StochRSI)
        lookback_days: int (berapa hari data yang diambil)

    Returns:
        dict: {
            'rsi': float,
            'stoch_rsi': float,
            'stoch_rsi_k': float,  # fast line
            'stoch_rsi_d': float,  # slow line (SMA dari K)
            'close': float,
            'date': date
        }
    """

    
    
