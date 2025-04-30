from app.domain.service.crime_service import CrimeService
from app.domain.model.crime_schema import CrimeSchema
class CrimeController:
    def __init__(self):
        self.dataset = CrimeSchema()
        self.service = CrimeService()

    def preprocess(self, *args):
        self.service.preprocess(*args)

    def correlation(self): #상관계수 분석
        print("Controller: Calling correlation_service.load_and_analyze...")
        results = self.correlation_service.load_and_analyze()
        print("Controller: Correlation analysis completed")
        return results
    
    def get_correlation_results(self):
        """상관계수 분석 결과를 반환하는 함수"""
        return self.correlation()

    def draw_crime_map(self):
        result = self.service.draw_crime_map()
        if result.get("status") == "success":
            print(f"Controller: Crime map created successfully at {result.get('file_path')}")
        else:
            print(f"Controller: Failed to create crime map - {result.get('message')}")
        return result

        
