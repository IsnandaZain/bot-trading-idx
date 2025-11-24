
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def read_sheet(date: str = None):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Autentikasi
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    # Buka Spreadsheet
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
    sheet = client.open("dataset").sheet1 # atau .worksheet("Nama Sheet")
    data = sheet.get_all_records()
    return data




