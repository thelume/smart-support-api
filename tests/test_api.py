from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.session import Base, get_db

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_temp.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_rag_ticket_flow():
    article_payload = {
        "title": "Reset de Senha no Active Directory",
        "content": "Solicitar confirmação de identidade e redefinir a senha via console ADUC.",
        "category": "Acessos",
        "tags": "senha, ad, login"
    }
    res_article = client.post("/api/v1/articles/", json=article_payload)
    assert res_article.status_code == 201

    ticket_payload = {
        "title": "Esqueci minha senha",
        "description": "Não consigo fazer login no sistema e preciso resetar minha senha.",
        "category": "Acessos",
        "priority": "medium"
    }
    res_ticket = client.post("/api/v1/tickets/", json=ticket_payload)
    assert res_ticket.status_code == 201
    data = res_ticket.json()
    assert "Active Directory" in data["suggested_solution"]
