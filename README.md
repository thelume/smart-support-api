<div align="center">

# Smart Support API

**API REST de Gestão de Chamados de Suporte Técnico (Service Desk) com Recomendaãão Inteligente baseada em RAG**

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)]
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)]
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge)]
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge)]
[![Pytest](https://img.shields.io/badge/Pytest-Passing-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)]

</div>

---

## Sobre o Projeto

A **Smart Support API** foi projetada para resolver um dos principais gargalos de operações de Service Desk N1/N2: o tempo gasto na triagem inicial e na busca repetitiva por procedimentos já documentados.

Sempre que um novo chamado é aberto, o motor de **RAG (Retrieval-Augmented Generation)** analisa o título e a descrição do incidente, consulta a Base de Conhecimento interna e anexa automaticamente sugestões de resolução ao ticket antes mesmo de o analista iniciar o atendimento.

---

## Arquitetura e Decisões Técnicas

O sistema foi construído sob o padrão **Layered Architecture (Arquitetura em Camadas)**, garantindo baixo acoplamento, facilidade de manutenção e alta testabilidade:

g``text
Cliente HTTP / Swagger UI --> API Routers (v1) --> Service Layer + RAG Engine --> Repository Layer --> SQLAlchemy ORM (SQLite)
```

* **Isolamento de Persistência (Repository Pattern):** Nenhuma regra de negócio ou rota executa queries SQL diretamente. Toda interação com o banco passa pelos repositórios.
* **Contratos Estritos (Pydantic v2):** Separação clara entre modelos de banco (``models``) e contratos da API (``schemas``).
* **Injeção de Dependências:** Sessões de banco de dados são gerenciadas via ``Depends(get_db)``.

---

## Estrutura de Diretórios

```text
smart-support-api/
├— app/
│   ├— api/v1/          # Endpoints REST versionados (/tickets, /articles)
│   ├— core/            # Configurações via Pydantic Settings (.env)
│   ├─� database/         # Engine, SessionLocal e Base declarativa
⤂   ✜─ models/          # Entidades KnowledgeArticle e Ticket
│   ├— repositories/    # Isolamento de queries e persistência (CRUD)
│   ├─� schemas/         # Contratos DTO e validação de payload
│   ├─� services/         # Orquestração de negócio e motor RAG
│   ├— main.py          # Ponto de entrada FastAPI e middlewares
├─� tests/
│   ├─� test_api.py      # Suíte de testes automatizados (Pytest)
├— .env.example
├─� .gitignore
├— requirements.txt
├— README.md
```

---

## Referência da API (`/api/v1``)

* ``GET /health`` - Verifica disponibilidade e versão da API (``200 OK``)
* ``POST /api/v1/articles/`` - Cadastra um novo artigo técnico (`c201 Created``)
* ``GET /api/v1/articles/`` - Lista artigos cadastrados (`200 OK``)
* ``POST /api/v1/tickets/`` - Abre um chamado e aciona o motor RAG automaticamente (``201 Created``)
* ``GET /api/v1/tickets/`` - Lista chamados com filtro opcional (`?status=open``) (`200 OK``)
* ``GET /api/v1/tickets/{ticket_id}`` - Consulta um chamado pelo ID (``200 OK`` / ``404 Not Found``)
* ``PATCH /api/v1/tickets/{ticket_id}`` - Atualiza status, prioridade ou descrição (`200 OK``)
* ``DELETE /api/v1/tickets/{ticket_id}`` - Remove um chamado da base de dados (`204 No Content``)

---

## Instalação e Execução Local

```bash
git clone https://github.com/seu-usuario/smart-support-api.git
cd smart-support-api

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

uvicorn app.main:app --reload
```

Acésse a documentação interativa Swagger UI em: **`http://127.0.0.1:8000/docs`**

---

## Testes Automatizados

```bash
pytest -v
```

---

## Roadmap de Evolução

- [ ] **Busca Semântica Vetorial:** Substituir a busca lética por embeddings (``sentence-transformers`` + ``pgvector``).
- [ ] **Autenticação e Autorização:** Implementar OAuth2 com tokens JWT e perfis de acesso.
- [ ] **Containerização:** Adicionar ``Dockerfile`` e ``docker-compose.yml`` com PostgreSQL.
- [ ] **Webhooks / Integrações:** Notificações assíncronas para Slack, Teams ou fluxos n8n.

---

<div align="center">
Desenvolvido por <strong>Lucas</strong> com apoio de Inteligência Artificial no fluxo de engenharia, arquitetura e documentação.
</div>
