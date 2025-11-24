from src.spreadsheet import migrate
from os import getenv

filename = getenv("FILENAME_DATA_HISTORIS", "data_historis.xlsx")
migrate.generate_data_histories(filename)