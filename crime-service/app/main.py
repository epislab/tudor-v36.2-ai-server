from fastapi import FastAPI
from controller.predict_controller import router as predict_router

app = FastAPI(title="ML Model API", description="Machine Learning Model Prediction API")

app.include_router(predict_router, prefix="/api", tags=["predictions"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 