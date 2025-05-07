from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nlp-service")

# Lifespan 설정
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 NLP Service가 시작됩니다.")
    yield
    logger.info("🛑 NLP Service가 종료됩니다.")

# FastAPI 앱 생성
app = FastAPI(
    title="NLP Service",
    description="NLP Service for Text Analysis",
    version="1.0.0",
    lifespan=lifespan
)

# 테스트용 엔드포인트
@app.get("/test", summary="테스트 엔드포인트")
async def test():
    return {"message": "테스트 파일입니다 2."}

