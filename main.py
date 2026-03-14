from fastapi import FastAPI
from app.routers.github_webhook import router as github_webhook_router

app = FastAPI()
app.include_router(github_webhook_router)


@app.get('/')
def home():
    return {'message': 'Hello World'}
