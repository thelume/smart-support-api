from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.article import ArticleCreate, ArticleResponse
from app.services import article_service

router = APIRouter(prefix="/articles", tags=["Knowledge Base"])


@router.post("/", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
def create_knowledge_article(article: ArticleCreate, db: Session = Depends(get_db)):
    return article_service.register_article(db=db, article_data=article)


@router.get("/", response_model=List[ArticleResponse])
def read_knowledge_articles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return article_service.list_articles(db=db, skip=skip, limit=limit)
