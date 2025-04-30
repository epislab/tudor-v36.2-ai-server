from app.domain.service.crime_service import CrimeService
from app.domain.model.crime_schema import CrimeSchema
class CrimeController:
    def __init__(self):
        self.dataset = CrimeSchema()
        self.service = CrimeService()

    def preprocess(self, *args):
        this = self.service.preprocess(*args)
        self.print_this(this)
        return this

    def print_this(self, this):
        print('*' * 100)
