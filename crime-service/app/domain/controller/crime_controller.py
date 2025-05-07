from app.domain.service.crime_preprocessor import CrimePreprocessor
class CrimeController:
    def __init__(self):
        self.service = CrimePreprocessor()

    def preprocess(self, *args):
        self.service.preprocess(*args)

 

        
