from dataclasses import dataclass
from abc import *
import json
import pandas as pd
import googlemaps
import numpy as np
from sklearn import preprocessing

class ReaderBase(metaclass=ABCMeta):

    @abstractmethod
    def new_file(self):
        pass

    @abstractmethod
    def csv_to_dframe(self):
        pass

    @abstractmethod
    def xls_to_dframe(self):
        pass

    @abstractmethod
    def load_json(self):
        pass

class PrinterBase(metaclass=ABCMeta):
    @abstractmethod
    def dframe(self):
        pass
