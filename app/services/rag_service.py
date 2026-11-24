from sqlalchemy.orm import Session
from app.repositories import article_repository


def generate_suggested_solution(db: Session, title: str, description: str) -> str:
    query_text = f"{title} {description}"
    matching_articles = article_repository.search_articles(db, query_text)

    if not matching_articles:
        return "Nenhum artigo correspondente encontrado na base de conhecimento. Encaminhar para análise técnica N1."

    suggestions = ["Sugestões encontradas na Base de Conhecimento:\n"]
    for idx, article in enumerate(matching_articles, start=1):
        snippet = article.content[:250] + ("..." if len(article.content) > 250 else "")
        suggestions.append(f"{idx}. [{article.category}] {article.title}: {snippet}")

    return "\n".join(suggestions)
