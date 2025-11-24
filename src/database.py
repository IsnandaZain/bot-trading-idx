

import datetime

import config.spreadsheet as spreadsheet
import config.base as bs


def input_data_sheet():
    data = spreadsheet.read_sheet()
    for dt in data:
        # pengkondisian untuk saham suspend
        if dt['open'] in ['#N/A', 0]:
            dt['open'] = dt['close']

        if dt['high'] in ['#N/A', 0]:
            dt['high'] = dt['close']

        if dt['low'] in ['#N/A', 0]:
            dt['low'] = dt['close']

        price = bs.DataHistories(
            ticker=dt['ticker'],
            open=dt['open'],
            high=dt['high'],
            low=dt['low'],
            close=dt['close'],
            volume=dt['volume'],
            date=datetime.date.today()
        )

        bs.session.add(price)
        bs.session.commit()
        
    return data