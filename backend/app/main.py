from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings_api
from .database import Base, engine
from .routers import (
    admin,
    auth,
    company_analytics,
    divestments,
    investments,
    user_analytics,
    users,
)
from .scripts.comp_init import init_companies
from .scripts.country_init import init_countries
from .scripts.market_init import init_markets

app = FastAPI()
Base.metadata.create_all(bind=engine)


# Initialize markets
try:
    init_markets()
except Exception as e:
    print(f"Error during market initialization: {e}")

# Initialize companies
try:
    init_companies()
except Exception as e:
    print(f"Error during company initialization: {e}")

# Initialize countries
try:
    init_countries()
except Exception as e:
    print(f"Error during country initialization: {e}")


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


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(investments.router)
app.include_router(divestments.router)
app.include_router(user_analytics.router)
app.include_router(company_analytics.router)
app.include_router(admin.router)



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=f"{settings_api.app_host}",
                port=settings_api.app_port)
