from enum import Enum
import os

# ✅ 서비스 타입 정의
class ServiceType(str, Enum):
    TITANIC = "titanic"
    CRIME = "crime"
    NLP = "nlp"
    TF = "tf"

# ✅ 환경 변수에서 서비스 URL 가져오기
DOMAIN = os.getenv("DOMAIN")

TITANIC_SERVICE_URL = os.getenv("TITANIC_SERVICE_URL")
CRIME_SERVICE_URL = os.getenv("CRIME_SERVICE_URL")
NLP_SERVICE_URL = os.getenv("NLP_SERVICE_URL")
TF_SERVICE_URL = os.getenv("TF_SERVICE_URL")

# ✅ 서비스 URL 매핑
SERVICE_URLS = {
    ServiceType.TITANIC: TITANIC_SERVICE_URL,
    ServiceType.CRIME: CRIME_SERVICE_URL,
    ServiceType.NLP: NLP_SERVICE_URL,
    ServiceType.TF: TF_SERVICE_URL,
}

# (선택) 필요하다면 도메인도 별도로 활용 가능
# 예시
print(f"도메인: {DOMAIN}")
print(f"TITANIC 서비스 URL: {SERVICE_URLS[ServiceType.TITANIC]}")
