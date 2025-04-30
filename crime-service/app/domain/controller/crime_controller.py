from app.domain.service.crime_service import CrimeService
from app.domain.model.crime_schema import CrimeSchema
class CrimeController:
    def __init__(self):
        self.dataset = CrimeSchema()
        self.service = CrimeService()

    def preprocess(self, *args):
        self.service.preprocess(*args)

    def draw_crime_map(self):
        self.service.draw_crime_map()

        
