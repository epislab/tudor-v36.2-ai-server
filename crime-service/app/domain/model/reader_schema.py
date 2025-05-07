from dataclasses import dataclass
from abc import *
import json
import pandas as pd
import googlemaps
from app.domain.model.abstracts import ReaderBase

class ReaderSchema(ReaderBase):

    def new_file(self, file) -> str:
        return file.context + file.fname

    def csv_to_dframe(self, file) -> object:
        return pd.read_csv(f'{self.new_file(file)}.csv', encoding='UTF-8', thousands=',')

    def xls_to_dframe(self, file, header, usecols) -> object:
        return pd.read_excel(f'{self.new_file(file)}.xls', header=header, usecols=usecols)

    def load_json(self, file) -> object:
        return json.load(open(f'{self.new_file(file)}.json', encoding='UTF-8'))

    def gmaps(self) -> object:
        return googlemaps.Client(key='AIzaSyBuXsJSJyGqNFXToPx9STCCfMLfghiU7cI')