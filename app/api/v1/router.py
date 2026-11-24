from fastapi import APIRouter
from app.api.v1 import tickets, articles

api_router = APIRouter()
api_router.include_router(tickets.router)
api_router.include_router(articles.router)
