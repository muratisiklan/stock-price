from fastapi import FastAPI
from .routers import metrics,charts,recommendation
from fastapi.middleware.cors import CORSMiddleware
from .config import settings_api

app = FastAPI()
# About CORS
# list of URLs api can talk. if all origins = ["*"]
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(metrics.router)
app.include_router(charts.router)
app.include_router(recommendation.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app,host=f"{settings_api.app_host}",port=settings_api.app_port)