```markdown
<div align="center">

# Smart Support API

**Plataforma Backend de Service Desk & Triagem Inteligente de Incidentes Orientada por RAG (Retrieval-Augmented Generation)**

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge)](https://www.sqlalchemy.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge)](https://docs.pydantic.dev/)
[![Pytest](https://img.shields.io/badge/Pytest-Integration_Tested-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Architecture](https://img.shields.io/badge/Architecture-Layered_%26_Repository-1F2937?style=for-the-badge)](#arquitetura-e-fluxo-de-dados)

[Visão Geral](#-visão-geral) •
[Arquitetura](#-arquitetura-e-fluxo-de-dados) •
[Motor RAG](#-funcionamento-do-motor-rag) •
[Modelagem de Dados](#-modelagem-de-dados) •
[Referência da API](#-referência-da-api-apiv1) •
[Setup e Execução](#-instalação-e-execução-local) •
[Testes](#-estratégia-de-testes-automatizados)

</div>

---

## Visão Geral

A **Smart Support API** é um serviço RESTful de alta performance projetado para automatizar o ciclo de vida de chamados técnicos (ITSM / Service Desk) e reduzir o **MTTR (Mean Time To Resolution)** nas camadas de atendimento N1 e N2.

Em sistemas tradicionais de suporte, analistas perdem tempo significativo diagnosticando incidentes recorrentes que já possuem procedimentos documentados. A **Smart Support API** resolve esse gargalo acoplando um motor de **RAG (Retrieval-Augmented Generation)** diretamente ao fluxo de ingestão de tickets: no momento em que um chamado é registrado, o sistema extrai termos-chave, consulta a Base de Conhecimento corporativa, calcula a relevância contextual e anexa sugestões acionáveis de resolução antes mesmo da alocação humana.

### Diferenciais Técnicos
* **Desacoplamento Estrito:** Separação rigorosa entre roteamento HTTP (`API`), regras de negócio (`Services`), acesso a dados (`Repositories`), entidades relacionais (`Models`) e contratos de validação (`Schemas`).
* **Triagem Contextual Síncrona:** Enriquecimento automático de tickets no momento da criação (`POST /api/v1/tickets/`) sem intervenção manual.
* **Isolamento de Testes de Integração:** Suíte `pytest` configurada com `dependency_overrides` e banco SQLite efêmero, garantindo testes determinísticos e zero poluição no ambiente local.
* **Documentação Viva (OpenAPI 3.1):** Geração automática de especificações interativas via Swagger UI e ReDoc.

---

## Arquitetura e Fluxo de Dados

A aplicação adota uma **Arquitetura em Camadas (Layered Architecture)** combinada ao **Repository Pattern**, garantindo que regras de negócio permaneçam agnósticas ao mecanismo de persistência.

```text
┌───────────────────────────────────────────────────────────────────────────────────┐
│                          Camada de Consumo (HTTP / JSON)                          │
│               Swagger UI  •  ReDoc  •  Clientes REST  •  Webhooks                 │
└─────────────────────────────────────────┬─────────────────────────────────────────┘
                                          │ HTTP Request (JSON)
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│  1. Camada de Apresentação (`app/api/v1/`)                                        │
│     • Versionamento explícito de rotas (`/api/v1`)                                │
│     • Validação estrita de payload e serialização via Pydantic v2 (`Schemas`)     │
│     • Mapeamento semântico de códigos HTTP (`200`, `201`, `204`, `404`, `422`)    │
└─────────────────────────────────────────┬─────────────────────────────────────────┘
                                          │ Validated DTOs
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│  2. Camada de Domínio & Orquestração (`app/services/`)                            │
│     • `ticket_service.py`: Gerencia ciclo de vida, estados e regras de SLA        │
│     • `article_service.py`: Valida e indexa procedimentos técnicos                │
│     • `rag_service.py`: Motor de recuperação, tokenização e ranking de soluções   │
└───────────────────┬───────────────────────────────────────────┬───────────────────┘
                    │                                           │
                    ▼                                           ▼
┌───────────────────────────────────────┐   ┌───────────────────────────────────────┐
│  3a. `ticket_repository.py`           │   │  3b. `article_repository.py`          │
│      • Operações CRUD encapsuladas    │   │      • Consultas filtradas por termo, │
│      • Paginação (`skip` / `limit`)   │   │        categoria e tags               │
└───────────────────┬───────────────────┘   └───────────────────┬───────────────────┘
                    │                                           │
                    └─────────────────────┬─────────────────────┘
                                          │ SQLAlchemy Session (`Depends(get_db)`)
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│  4. Camada de Persistência (`app/models/` & `app/database/`)                      │
│     • Mapeamento Objeto-Relacional declarativo (SQLAlchemy 2.0 ORM)               │
│     • Ciclo de vida de transação controlado por requisição HTTP                   │
└───────────────────────────────────────────────────────────────────────────────────┘

```

### Decisões Arquiteturais

1. **Repository Pattern:** Isola completamente as instruções SQLAlchemy da camada de serviço. Caso o projeto escale de SQLite para PostgreSQL com `pgvector`, apenas a camada de repositório e a string de conexão sofrem alteração.
2. **DTOs Imutáveis / Tipados (Pydantic v2):** Modelos de banco (`SQLAlchemy`) nunca são expostos diretamente na borda HTTP. Cada operação possui schemas dedicados (`Create`, `Update`, `Response`), impedindo *mass assignment* e vazamento de atributos internos.
3. **Injeção de Dependências Nativa:** O gerenciamento de sessões (`get_db`) utiliza geradores Python (`yield`), assegurando o fechamento determinístico da conexão mesmo em cenários de exceção.

---

## Funcionamento do Motor RAG

O fluxo de enriquecimento automático de chamados ocorre em quatro estágios determinísticos durante a criação de um ticket:

```text
[Novo Ticket: Título + Descrição]
               │
               ▼
   1. Extração e Normalização
      (Tokenização, lowercase e remoção de stopwords)
               │
               ▼
   2. Recuperação na Base de Conhecimento
      (Consulta multi-campo: título, tags e corpo técnico)
               │
               ▼
   3. Pontuação e Ordenação Contextual
      (Priorização de correspondências por relevância técnica)
               │
               ▼
   4. Injeção no Payload de Resposta
      (Preenchimento automático do campo `suggested_solution`)

```

---

## Modelagem de Dados

### Entidade `Ticket` (`tickets`)

| Campo | Tipo | Restrições / Padrão | Descrição |
| --- | --- | --- | --- |
| `id` | `Integer` | `PK, Auto-increment` | Identificador único do chamado |
| `title` | `String(200)` | `Not Null, Indexed` | Resumo objetivo do incidente |
| `description` | `Text` | `Not Null` | Detalhamento técnico do problema relatado |
| `category` | `String(100)` | `Default: "Geral"` | Área técnica (`Redes`, `Acessos`, `Infraestrutura`, etc.) |
| `priority` | `String(20)` | `low | medium | high | critical` | Nível de criticidade operacional |
| `status` | `String(20)` | `open | in_progress | resolved | closed` | Estado atual no fluxo de atendimento |
| `suggested_solution` | `Text` | `Nullable` | Recomendação gerada automaticamente pelo motor RAG |
| `created_at` | `DateTime` | `UTC Now` | Timestamp de abertura do chamado |
| `updated_at` | `DateTime` | `UTC Now (On Update)` | Timestamp da última modificação |

### Entidade `KnowledgeArticle` (`knowledge_articles`)

| Campo | Tipo | Restrições / Padrão | Descrição |
| --- | --- | --- | --- |
| `id` | `Integer` | `PK, Auto-increment` | Identificador único do artigo |
| `title` | `String(200)` | `Not Null, Indexed` | Título do procedimento operacional padrão (POP) |
| `content` | `Text` | `Not Null` | Passo a passo técnico para resolução |
| `category` | `String(100)` | `Default: "Geral"` | Domínio técnico associado |
| `tags` | `String(255)` | `Nullable` | Palavras-chave separadas por vírgula para indexação |
| `created_at` | `DateTime` | `UTC Now` | Timestamp de publicação do artigo |

---

## Estrutura de Diretórios

```text
smart-support-api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── articles.py          # Rotas HTTP para Base de Conhecimento
│   │       ├── tickets.py           # Rotas HTTP para Ciclo de Vida de Tickets
│   │       └── router.py            # Roteador agregador da versão v1
│   ├── core/
│   │   └── config.py                # Gestão centralizada de configurações (BaseSettings)
│   ├── database/
│   │   └── session.py               # Configuração do Engine, SessionLocal e Base ORM
│   ├── models/
│   │   ├── article.py               # Modelo relacional KnowledgeArticle
│   │   └── ticket.py                # Modelo relacional Ticket
│   ├── repositories/
│   │   ├── article_repository.py    # Queries e persistência de artigos
│   │   └── ticket_repository.py     # Queries, filtros e persistência de tickets
│   ├── schemas/
│   │   ├── article.py               # Contratos Pydantic (ArticleCreate, ArticleResponse)
│   │   └── ticket.py                # Contratos Pydantic (TicketCreate, TicketUpdate, TicketResponse)
│   ├── services/
│   │   ├── article_service.py       # Regras de negócio da Base de Conhecimento
│   │   ├── rag_service.py           # Motor de recuperação e recomendação RAG
│   │   └── ticket_service.py        # Orquestração de tickets e exceções HTTP
│   └── main.py                      # Instância FastAPI, metadados OpenAPI e rotas raiz
├── tests/
│   └── test_api.py                  # Suíte de testes de integração automatizados
├── .env.example                     # Modelo de variáveis de ambiente
├── .gitignore                       # Regras de exclusão de artefatos locais
├── requirements.txt                 # Dependências fixadas do ambiente
└── README.md

```

---

## Referência da API (`/api/v1`)

### Health & Observabilidade

| Método | Endpoint | Descrição | Códigos HTTP |
| --- | --- | --- | --- |
| `GET` | `/health` | Verifica status operacional, nome da aplicação e versão | `200 OK` |

### Base de Conhecimento (`Knowledge Base`)

| Método | Endpoint | Descrição | Códigos HTTP |
| --- | --- | --- | --- |
| `POST` | `/api/v1/articles/` | Registra um novo procedimento técnico na base | `201 Created`, `422 Unprocessable Entity` |
| `GET` | `/api/v1/articles/` | Lista artigos cadastrados com suporte a paginação (`skip`, `limit`) | `200 OK` |

### Gestão de Chamados (`Tickets`)

| Método | Endpoint | Descrição | Códigos HTTP |
| --- | --- | --- | --- |
| `POST` | `/api/v1/tickets/` | Cria um ticket e executa busca contextual RAG automaticamente | `201 Created`, `422 Unprocessable Entity` |
| `GET` | `/api/v1/tickets/` | Lista tickets com paginação e filtro opcional (`?status=open`) | `200 OK` |
| `GET` | `/api/v1/tickets/{ticket_id}` | Recupera os detalhes completos de um ticket específico | `200 OK`, `404 Not Found` |
| `PATCH` | `/api/v1/tickets/{ticket_id}` | Atualização parcial de status, prioridade ou descrição | `200 OK`, `404 Not Found`, `422` |
| `DELETE` | `/api/v1/tickets/{ticket_id}` | Remove permanentemente um ticket da base | `204 No Content`, `404 Not Found` |

---

## Exemplos de Uso (`cURL`)

### 1. Indexar um Procedimento na Base de Conhecimento

```bash
curl -X POST "[http://127.0.0.1:8000/api/v1/articles/](http://127.0.0.1:8000/api/v1/articles/)" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Erro de autenticação na VPN Corporativa",
    "content": "Verificar sincronização do token MFA no dispositivo móvel e reiniciar o cliente FortiClient. Caso o erro persista, limpar o cache DNS com ipconfig /flushdns.",
    "category": "Redes",
    "tags": "vpn, forticlient, mfa, rede"
  }'

```

### 2. Abrir um Ticket com Sugestão Automática via RAG

```bash
curl -X POST "[http://127.0.0.1:8000/api/v1/tickets/](http://127.0.0.1:8000/api/v1/tickets/)" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Falha ao conectar na VPN",
    "description": "O cliente FortiClient apresenta erro ao tentar autenticar na rede corporativa.",
    "category": "Redes",
    "priority": "high"
  }'

```

**Resposta (`201 Created`):**

```json
{
  "title": "Falha ao conectar na VPN",
  "description": "O cliente FortiClient apresenta erro ao tentar autenticar na rede corporativa.",
  "category": "Redes",
  "priority": "high",
  "id": 1,
  "status": "open",
  "suggested_solution": "Sugestões encontradas na Base de Conhecimento:\n\n1. [Redes] Erro de autenticação na VPN Corporativa: Verificar sincronização do token MFA no dispositivo móvel e reiniciar o cliente FortiClient. Caso o erro persista, limpar o cache DNS com ipconfig /flushdns.",
  "created_at": "2026-11-24T18:26:33.795147",
  "updated_at": "2026-11-24T18:26:33.795158"
}

```

### 3. Atualizar o Status de um Chamado

```bash
curl -X PATCH "[http://127.0.0.1:8000/api/v1/tickets/1](http://127.0.0.1:8000/api/v1/tickets/1)" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "resolved"
  }'

```

---

## Instalação e Execução Local

### Pré-requisitos

* **Python 3.12+**
* **Git** e **pip**

### Passo a passo

```bash
# 1. Clonar o repositório
git clone [https://github.com/seu-usuario/smart-support-api.git](https://github.com/seu-usuario/smart-support-api.git)
cd smart-support-api

# 2. Criar e ativar o ambiente virtual isolado
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env

# 5. Iniciar o servidor ASGI (Uvicorn)
uvicorn app.main:app --reload

```

Com o servidor ativo, acesse os painéis interativos da API:

* **Swagger UI:** `http://127.0.0.1:8000/docs`
* **ReDoc:** `http://127.0.0.1:8000/redoc`
* **OpenAPI Schema (JSON):** `http://127.0.0.1:8000/openapi.json`

---

## Estratégia de Testes Automatizados

A suíte de testes (`tests/test_api.py`) utiliza o `TestClient` do FastAPI combinado com sobrescrita de injeção de dependência (`app.dependency_overrides[get_db]`). Isso permite validar o comportamento ponta a ponta dos endpoints HTTP e do motor RAG contra um banco de dados SQLite isolado, garantindo zero impacto sobre os dados de desenvolvimento.

```bash
# Executar toda a suíte com saída detalhada
pytest -v

```

---

## Roadmap Técnico

* [ ] **Busca Semântica Vetorial:** Substituir a busca léxica por embeddings densos (`sentence-transformers` + `pgvector` ou `FAISS`) para recuperação baseada em similaridade semântica.
* [ ] **Segurança & RBAC:** Implementar autenticação OAuth2 com tokens JWT e controle de acesso baseado em papéis (`requester`, `agent`, `admin`).
* [ ] **Containerização & Banco Relacional:** Adicionar `Dockerfile` multi-stage e `docker-compose.yml` orquestrando a API com PostgreSQL.
* [ ] **Observabilidade & Logs Estruturados:** Integrar logging em formato JSON com correlation IDs por requisição e métricas Prometheus.
* [ ] **Integrações Orientadas a Eventos:** Disparar webhooks assíncronos para Slack, Microsoft Teams ou fluxos n8n na abertura de incidentes de prioridade `critical`.

---
