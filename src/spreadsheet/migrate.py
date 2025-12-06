import datetime
import pandas as pd

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from src.spreadsheet import normalize_price as np

from config import base as bs

def read(save: bool = False, date: str = None):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Autentikasi
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    # Buka Spreadsheet
    sheet = client.open("dataset").sheet1 # atau .worksheet("Nama Sheet")
    data = sheet.get_all_records()


    """
    [
        {
            'ticker': 'ANTM', 
            'close': 3030, 
            'high': 3100, 
            'open': 3070, 
            'low': 3010, 
            'volume': 70391800
        }
        
    ]
    """
    if save:
        for dt in data:
            # simpan ke database
            if dt['open'] in ['#N/A', 0]:
                dt['open'] = dt['close']

            if dt['high'] in ['#N/A', 0]:
                dt['high'] = dt['close']

            if dt['low'] in ['#N/A', 0]:
                dt['low'] = dt['close']

            price_history = db.DataHistories(
                ticker=dt['ticker'],
                open=dt['open'],
                high=dt['high'],
                low=dt['low'],
                close=dt['close'],
                volume=dt['volume'],
                date=datetime.date.today() if not date else datetime.datetime.strptime(date, '%Y-%m-%d').date()
            )

            bs.session.add(price_history)
            bs.session.commit()
    
    return data

"""
Digunakan untuk menambahkan data historis dari saham tertentu kedalam database
Data diambil dari file excel yang didownload dari spreadsheet google
"""
def generate_data_histories(filename: str = "dataset.xlsx"):
    df = pd.read_excel(filename, sheet_name="historis")

    """
    Column Index :
    date - 1
    open - 2
    high - 3
    low - 4
    close - 5
    volume - 6
    """

    # get ticker
    ticker = df.columns[2]
    print(f'Migrating data for ticker: {ticker}')

    # change columns name
    new_columns = [
        "Index",
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]
    df.columns = new_columns

    for index, row in df.iloc[1:].iterrows():
        # get existing data
        exist_data = bs.session.query(bs.DataHistories).filter(
            bs.DataHistories.ticker == ticker,
            bs.DataHistories.date == row["Date"].strftime("%Y-%m-%d")
        ).first()

        if exist_data:
            continue

        # pengkondisian saham suspend
        if row['Open'] in ['#N/A', 0]:
            row['Open'] = row['Close']

        if row['High'] in ['#N/A', 0]:
            row['High'] = row['Close']
            
        if row['Low'] in ['#N/A', 0]:
            row['Low'] = row['Close']

        # save data to database
        data = bs.DataHistories(
            ticker=ticker,
            open=np.normalize_price(row["Open"]),
            high=np.normalize_price(row["High"]),
            low=np.normalize_price(row["Low"]),
            close=np.normalize_price(row["Close"]),
            volume=np.normalize_price(row["Volume"]),
            date=row["Date"].strftime("%Y-%m-%d") if type(row["Date"]) != str else row["Date"]
        )

        bs.session.add(data)

    bs.session.commit()
    print('Data successfully migrated to database.')
