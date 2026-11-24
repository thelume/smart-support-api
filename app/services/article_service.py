from typing import List
from sqlalchemy.orm import Session
from app.models.article import KnowledgeArticle
from app.schemas.article import ArticleCreate
from app.repositories import article_repository


def register_article(db: Session, article_data: ArticleCreate) -> KnowledgeArticle:
    return article_repository.create_article(db, article_data)


def list_articles(db: Session, skip: int = 0, limit: int = 100) -> List[KnowledgeArticle]:
    return article_repository.get_articles(db, skip=skip, limit=limit)
