from fastapi import FastAPI


app = FastAPI(title="ML Model API", description="Machine Learning Model Prediction API")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 