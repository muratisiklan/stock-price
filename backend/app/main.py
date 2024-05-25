from fastapi import FastAPI
from .database import engine,Base
from .routers import auth, investments, admin, users,divestments

app = FastAPI()
Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(investments.router)
app.include_router(admin.router)
app.include_router(users.router)
# app.include_router(divestments.router)

