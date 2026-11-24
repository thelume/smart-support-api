from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.article import KnowledgeArticle
from app.schemas.article import ArticleCreate


def create_article(db: Session, article_data: ArticleCreate) -> KnowledgeArticle:
    db_article = KnowledgeArticle(**article_data.model_dump())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


def get_articles(db: Session, skip: int = 0, limit: int = 100) -> List[KnowledgeArticle]:
    return db.query(KnowledgeArticle).offset(skip).limit(limit).all()


def search_articles(db: Session, query_text: str) -> List[KnowledgeArticle]:
    keywords = [word.strip() for word in query_text.split() if len(word.strip()) > 2]
    if not keywords:
        return []
    filters = []
    for word in keywords:
        pattern = f"%{word}%"
        filters.append(KnowledgeArticle.title.ilike(pattern))
        filters.append(KnowledgeArticle.content.ilike(pattern))
        filters.append(KnowledgeArticle.tags.ilike(pattern))
    return db.query(KnowledgeArticle).filter(or_(*filters)).limit(5).all()
