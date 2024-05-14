from fastapi import FastAPI
from .models import Base
from .database import engine
from .routers import auth, investments, admin, users

app = FastAPI()
Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(investments.router)
app.include_router(admin.router)
app.include_router(users.router)
