from fastapi import APIRouter, Request
import logging
from app.domain.controller.crime_controller import CrimeController
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# 로거 설정
logger = logging.getLogger("crime_router")
logger.setLevel(logging.INFO)
router = APIRouter()

# GET
@router.get("/details", summary="모든 회사 목록 조회")
async def get_all_companies():
    controller = CrimeController()
    controller.preprocess('cctv_in_seoul.csv', 'crime_in_seoul.csv', 'pop_in_seoul.xls')
    return {"message": 'SUCCESS'}