from fastapi import FastAPI
from app.core.config import settings
from app.database.session import engine, Base
from app.models import ticket, article

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API REST de Gestão de Tickets de TI e Base de Conhecimento com RAG.",
)


@app.get("/health", tags=["Health Check"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }
