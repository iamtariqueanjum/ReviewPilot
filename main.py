from fastapi import FastAPI
from app.routers.webhook_router import router as github_webhook_router
from app.routers.review_router import router as review_router

app = FastAPI()
app.include_router(github_webhook_router)
app.include_router(review_router)

@app.get('/')
def home():
    return {'message': 'Welcome to ReviewPilot!'}


# TODO exception handling, logging, metrics, etc.
