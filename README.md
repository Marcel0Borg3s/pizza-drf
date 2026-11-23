# Pizza DRF API

![Python](https://img.shields.io/badge/python-3.13-blue)
![Django](https://img.shields.io/badge/django-6.1-092E20)
![DRF](https://img.shields.io/badge/DRF-3.18-A30000)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-orange)

API REST de estudo para uma pizzaria: cardápio de pizzas, cadastro de clientes e
avaliações. Construída com Django + Django REST Framework, usa SQLite e foi pensada para ser consumida por um front separado (padrão BFF, o navegador fala com o front e o front fala com esta API).

O objetivo é praticar modelagem, serialização e rotas REST com o mínimo de código
possível: cada recurso usa as views genéricas do DRF e um `ModelSerializer`.

## Índice

- [O que a API faz](#o-que-a-api-faz)
- [Arquitetura](#arquitetura)
- [Modelo de dados](#modelo-de-dados)
- [Endpoints](#endpoints)
- [Exemplos com curl](#exemplos-com-curl)
- [Regras de negócio](#regras-de-negócio)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Como rodar](#como-rodar)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Testes](#testes)
- [Decisões técnicas](#decisões-técnicas)
- [Limitações e próximos passos](#limitações-e-próximos-passos)
- [Segurança](#segurança)
- [Licença](#licença)

## O que a API faz

Três recursos, todos com CRUD completo:

| Recurso   | O que guarda 

| `pizzas`  | sabor, descrição e preço do cardápio 
| `clients` | nome, apelido, telefone e endereço de entrega 
| `reviews` | nota de 1 a 5, comentário e a pizza avaliada 

A API não tem telas: ela devolve e recebe JSON. A interface fica no front, que consome
estas rotas no servidor (nunca direto do navegador, o que dispensa CORS).

## Arquitetura

```
navegador  ──HTTP──▶  pizza_frontend (Django + templates)
                            │
                            └── HTTP servidor-a-servidor ──▶  pizza_drf (esta API)
                                                                  /api/v1/pizzas/
                                                                  /api/v1/clients/
                                                                  /api/v1/reviews/
```

Consequências desse desenho:

- sem CORS, porque o navegador nunca chama a API;
- nenhum token ou credencial aparece no HTML;
- o front decide o que mostrar, a API só entrega dado.

## Modelo de dados

### Pizza

| Campo         | Tipo          | Observação 
| `id`          | UUID          | chave primária, gerada automaticamente 
| `flavor`      | texto (50)    | sabor, ex.: "Margherita" 
| `description` | texto longo   | ingredientes 
| `price`       | decimal (6,2) | preço em reais 
| `created_at`  | data/hora     | preenchido na criação 
| `updated_at`  | data/hora     | atualizado a cada `save()` 

### Client

| Campo      | Tipo        | Observação 
| `id`       | UUID        | chave primária 
| `name`     | texto (200) | nome completo 
| `nickname` | texto (30)  | apelido, **único** 
| `phone`    | texto (20)  | telefone 
| `address`, `number`, `neighborhood`, `city` | texto     | endereço de entrega 
| `created_at`, `updated_at`                  | data/hora | auditoria 

### Review

| Campo        | Tipo            | Observação 
| `id`         | inteiro         | chave primária sequencial |
| `pizza`      | FK para `Pizza` | `PROTECT`, ver [regras](#regras-de-negócio) 
| `stars`      | inteiro         | validado entre 1 e 5 
| `comment`    | texto longo     | opcional (`null`/`blank`) 
| `created_at` | data/hora       | usado para ordenar a lista 

## Endpoints

Tudo fica sob o prefixo `/api/v1/`. Base local: `http://127.0.0.1:8000`

| Método       | Rota                            | Ação 
| `GET`        | `/api/v1/pizzas/`               | lista todas as pizzas 
| `POST`       | `/api/v1/pizzas/`               | cria uma pizza 
| `GET`        | `/api/v1/pizzas/<uuid>/`        | detalhe de uma pizza 
| `PATCH`/`PUT`| `/api/v1/pizzas/<uuid>/`        | atualiza (parcial ou completa) 
| `DELETE`     | `/api/v1/pizzas/<uuid>/`        | exclui, se não houver avaliações 
| `GET`        | `/api/v1/clients/`              | lista clientes 
| `POST`       | `/api/v1/clients/`              | cria cliente 
| `GET`        | `/api/v1/clients/<uuid>/`       | detalhe do cliente 
| `PATCH`/`PUT`| `/api/v1/clients/<uuid>/`       | atualiza cliente 
| `DELETE`     | `/api/v1/clients/<uuid>/`       | exclui cliente 
| `GET`        | `/api/v1/reviews/`              | lista avaliações, mais novas primeiro 
| `GET`        | `/api/v1/reviews/?pizza=<uuid>` | avaliações de uma pizza 
| `POST`       | `/api/v1/reviews/`              | cria avaliação 
| `GET`        | `/api/v1/reviews/<uuid>/`       | detalhe da avaliação (ver aviso abaixo) 
| `PATCH`/`PUT`| `/api/v1/reviews/<uuid>/`       | atualiza avaliação (ver aviso abaixo) 
| `DELETE`     | `/api/v1/reviews/<uuid>/`       | exclui avaliação (ver aviso abaixo) 
| `GET`        | `/admin/` | admin do Django (requer `createsuperuser`), fora do prefixo da API 

Aviso sobre o detalhe de review: `reviews/urls.py` declara a rota como `<uuid:pk>`, mas
`Review` usa chave primária inteira. A URL resolve, o lookup não: hoje
`GET /api/v1/reviews/<id>/` responde `404`. Para funcionar, a rota precisa voltar a
`<int:pk>`.

Detalhes de contrato:

- `id`, `created_at` e `updated_at` são somente leitura, o DRF ignora se forem enviados;
- não há paginação configurada: `GET` em lista devolve um array JSON direto;
- não há autenticação: qualquer requisição pode ler e escrever;
- `POST /api/v1/reviews/` recebe o UUID da pizza no campo `pizza`.

## Exemplos com curl

### Listar o cardápio

```bash
curl http://127.0.0.1:8000/api/v1/pizzas/
```

```json
[
  {
    "id": "b28ef626-7db8-443b-8e16-cd038e42f35e",
    "flavor": "Catuperu",
    "description": "Molho de tomate, catupiry e fatias de peito de peru defumado",
    "price": "49.90",
    "created_at": "2026-11-19T12:50:51.011337-03:00",
    "updated_at": "2026-11-19T12:50:51.011370-03:00"
  }
]
```

### Criar uma pizza

```bash
curl -X POST http://127.0.0.1:8000/api/v1/pizzas/ \
  -H "Content-Type: application/json" \
  -d '{
    "flavor": "Margherita",
    "description": "Molho de tomate, mozzarella de búfala e manjericão.",
    "price": "49.90"
  }'
```

```json
{
  "id": "e2cab6ee-548f-4408-894b-c158242a5076",
  "flavor": "Margherita",
  "description": "Molho de tomate, mozzarella de búfala e manjericão.",
  "price": "49.90",
  "created_at": "2026-11-19T14:51:36.137541-03:00",
  "updated_at": "2026-11-19T14:51:36.137563-03:00"
}
```

### Alterar só o preço

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/pizzas/e2cab6ee-548f-4408-894b-c158242a5076/ \
  -H "Content-Type: application/json" \
  -d '{"price": "54.90"}'
```

### Avaliar uma pizza

```bash
curl -X POST http://127.0.0.1:8000/api/v1/reviews/ \
  -H "Content-Type: application/json" \
  -d '{
    "pizza": "e2cab6ee-548f-4408-894b-c158242a5076",
    "stars": 5,
    "comment": "Massa leve, borda crocante."
  }'
```

```json
{
  "id": 3,
  "stars": 5,
  "comment": "Massa leve, borda crocante.",
  "created_at": "2026-11-19T14:51:36.249159-03:00",
  "pizza": "e2cab6ee-548f-4408-894b-c158242a5076"
}
```

### Avaliações de uma pizza

```bash
curl "http://127.0.0.1:8000/api/v1/reviews/?pizza=e2cab6ee-548f-4408-894b-c158242a5076"
```

### Erros esperados

```bash
# excluir pizza que já tem avaliação
curl -i -X DELETE http://127.0.0.1:8000/api/v1/pizzas/e2cab6ee-548f-4408-894b-c158242a5076/
# HTTP/1.1 409 Conflict
# {"detail":"Esta pizza já possui avaliações e não pode ser excluída."}

# nota fora da faixa
curl -X POST http://127.0.0.1:8000/api/v1/reviews/ -H "Content-Type: application/json" \
  -d '{"pizza":"e2cab6ee-548f-4408-894b-c158242a5076","stars":9}'
# HTTP/1.1 400 Bad Request
# {"stars":["Certifique-se de que este valor seja inferior ou igual a 5."]}

# id inexistente
curl http://127.0.0.1:8000/api/v1/pizzas/00000000-0000-0000-0000-000000000000/
# HTTP/1.1 404 Not Found
# {"detail":"No Pizza matches the given query."}
```

## Regras de negócio

- **Nota de 1 a 5**: `stars` tem `MinValueValidator(1)` e `MaxValueValidator(5)`, o DRF
  devolve `400` com a mensagem do campo.
- **Comentário é opcional**: `comment` aceita `null`.
- **Pizza com avaliação não é excluída**: a FK usa `on_delete=PROTECT`, e a view traduz
  o `ProtectedError` em `409 Conflict` com uma mensagem em português. Para tirar uma
  pizza do cardápio sem perder avaliações, o caminho é editar/desativar no front, não
  apagar aqui.
- **Lista de avaliações**: ordenada por `created_at` decrescente, e aceita
  `?pizza=<uuid>`; um UUID inválido no filtro devolve lista vazia em vez de erro.
- **Apelido de cliente é único**: `nickname` tem `unique=True`, o `POST` duplicado
  devolve `400`.

## Requisitos

- Python 3.13 (o projeto usa `pyproject.toml` com `requires-python = ">=3.13"`)
- [uv](https://docs.astral.sh/uv/) para instalar as dependências (recomendado)
- **PostgreSQL 14+** para o banco principal (SQLite continua como fallback local)

Dependências declaradas:

| Pacote | Versão | Para quê |
| --- | --- | --- |
| `django` | `>=6.1.3` | framework |
| `djangorestframework` | `>=3.18.3` | camada REST |
| `psycopg[binary]` | `>=3.3.9` | driver do PostgreSQL |
| `python-dotenv` | `>=1.2.4` | ler o `.env` no `settings.py` |

## Instalação

```bash
# 1. clonar
git clone https://github.com/Marcel0Borg3s/pizza-drf.git
cd pizza-drf

# 2. criar o ambiente e instalar as dependências (lê o uv.lock)
uv sync

# 3. configuração do banco
cp .env.example .env
# edite .env com DB_NAME, DB_USER, DB_PASSWORD, DB_HOST e DB_PORT
# (ou deixe DB_NAME vazio para rodar em SQLite)

# 4. criar o banco no PostgreSQL
createdb -U postgres pizza_drf
# sem o cliente psql:
#   psql -U postgres -c "CREATE DATABASE pizza_drf;"

# 5. criar as tabelas
uv run python manage.py migrate

# 6. usuário para o /admin/
uv run python manage.py createsuperuser

# 7. subir o servidor
uv run python manage.py runserver
```

A API fica em `http://127.0.0.1:8000/api/v1/` (o admin, em `http://127.0.0.1:8000/admin/`).

Se preferir `pip` e `venv` em vez do `uv`:

```bash
python3.13 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install "django>=6.1.3" "djangorestframework>=3.18.3" "psycopg[binary]>=3.3.9" "python-dotenv>=1.2.4"
python manage.py migrate
python manage.py runserver
```

O banco é escolhido pelo `.env`: com `DB_NAME` preenchido o Django usa PostgreSQL, sem
`DB_NAME` ele cai no SQLite (`db.sqlite3` na raiz). O `.env` e o `db.sqlite3` locais não
devem ser versionados: cada pessoa gera os seus.

## Como rodar

```bash
uv run python manage.py runserver              # porta 8000
uv run python manage.py runserver 8001         # outra porta
uv run python manage.py migrate                # aplica migrations
uv run python manage.py makemigrations         # depois de mudar um model
uv run python manage.py shell                  # REPL com o Django carregado
uv run python manage.py check                  # checagem de configuração
```

Com o servidor no ar:

- `http://127.0.0.1:8000/api/v1/pizzas/` responde a lista do cardápio;
- `http://127.0.0.1:8000/admin/` abre o admin, onde `Pizza`, `Client` e `Review` estão
  registrados e podem ser editados por formulário.

Administração pelo Django admin: cada model tem `list_display` gerado a partir dos
próprios campos, então qualquer campo novo aparece na listagem automaticamente.

### Configuração atual

Tudo em `app/settings.py`, sem variáveis de ambiente nesta fase:

| Item | Valor |
| --- | --- |
| Banco | PostgreSQL via `DB_*` no `.env` (SQLite se `DB_NAME` estiver vazio) |
| Idioma | `pt-br` |
| Fuso | `America/Sao_Paulo` |
| `DEBUG` | `True` |
| Email | backend de console (`MAILERS`) |
| `ALLOWED_HOSTS` | vazio (só funciona em `127.0.0.1`/`localhost`) |

### Migrando dados de um SQLite antigo

O `db.sqlite3` não é lido quando o `.env` aponta para o PostgreSQL. Para levar os dados:

```bash
# 1. com o .env atual, exporte apenas as tabelas de negócio
uv run python manage.py dumpdata pizzas clients reviews --indent 2 -o dump.json

# 2. comente as variáveis DB_* no .env (volta para SQLite) e importe o dump
#    do banco antigo para o novo, invertendo a ordem:
#    - gere o dump com o .env sem DB_* (SQLite)
#    - restaure o DB_* e rode:
uv run python manage.py loaddata dump.json
```

Em resumo: o `dumpdata` roda no banco de origem e o `loaddata` no de destino, então
alterne o `.env` entre as duas etapas.

## Estrutura do projeto

```
pizza_drf/
├── manage.py
├── pyproject.toml / uv.lock      # dependências e versões travadas
├── app/                          # configuração do projeto
│   ├── settings.py
│   ├── urls.py                   # admin + include com o prefixo /api/v1/
│   └── asgi.py / wsgi.py
├── clients/                      # cadastro de clientes
│   ├── models.py / serializers.py / views.py / admin.py
│   ├── urls.py                   # rotas de clients
│   └── migrations/
├── pizzas/                       # cardápio
│   ├── models.py / serializers.py / views.py / admin.py
│   ├── urls.py                   # rotas de pizzas
│   ├── exceptions.py             # erro 409 de pizza em uso
│   └── migrations/
└── reviews/                      # avaliações
    ├── models.py / serializers.py / views.py / admin.py
    ├── urls.py                   # rotas de reviews
    └── migrations/
```

Cada app segue sempre o mesmo trio: `models.py` (tabela), `serializers.py` (contrato
JSON) e `views.py` (views). O `app/urls.py` só registra o `admin/` e faz `include` do
`urls.py` de cada app sob o prefixo `api/v1/`, então o caminho final de cada recurso é
`/api/v1/<recurso>/`.

## Testes

Ainda não há testes escritos: os arquivos `tests.py` dos apps são os stubs gerados pelo
Django, então `uv run python manage.py test` roda zero testes.

Ideias para o próximo passo, em ordem de valor:

1. `POST /api/v1/reviews/` com nota 0, 6 e 5 (limites);
2. `DELETE /api/v1/pizzas/<uuid>/` com e sem avaliação (200/204 versus 409);
3. `?pizza=` com UUID válido, inválido e pizza sem avaliações;
4. `nickname` duplicado em `POST /api/v1/clients/`;
5. detalhe de review em `/api/v1/reviews/<id>/`, que hoje responde `404` por causa do
   `<uuid:pk>` na rota.

## Decisões técnicas

- **UUID como chave em `Pizza` e `Client`**, inteiro em `Review`: ids de recurso não
  ficam enumeráveis, e a avaliação ganha uma PK barata, já que é o registro mais
  numeroso. Por isso a rota de detalhe de review precisa de `<int:pk>`, enquanto as
  outras usam `<uuid:pk>`. Hoje ela está declarada como `<uuid:pk>` e responde `404`.
- **`on_delete=PROTECT`** em `Review.pizza`: apagar uma pizza nunca leva avaliação junto.
  O preço é responder `409` em vez de deixar o banco estourar erro 500.
- **Views genéricas do DRF** (`ListCreateAPIView`, `RetrieveUpdateDestroyAPIView`): CRUD
  completo com poucas linhas e comportamento padrão previsível. Só a listagem de
  reviews tem `get_queryset` próprio, por causa do filtro `?pizza=`.
- **`ModelSerializer` com `fields = '__all__'`**: contrato direto do model, sem
  duplicação. Quando a API expuser dado sensível, o caminho é trocar por `fields`
  explícito.
- **Sem autenticação nesta fase**, o foco do estudo é modelagem e rotas REST.

## Limitações e próximos passos

- **Média de avaliações**: ainda não existe. Um endpoint de resumo
  (`GET /api/v1/pizzas/<uuid>/reviews/summary/`) com `Avg`/`Count` resolveria, junto com a nota
  média por pizza no serializer.
- **Autenticação e permissões**: hoje qualquer um escreve. `IsAuthenticatedOrReadOnly`
  para leitura pública e escrita autenticada é o passo natural, com token ou JWT.
- **Paginação, busca e filtros**: sem paginação, a lista cresce sem limite. Um
  `DEFAULT_PAGINATION_CLASS` no DRF e `django-filter` para `?flavor=`, `?min_price=`.
- **Mais campos de pizza**: categoria, imagem e disponibilidade não existem no model,
  então todo cardápio hoje é uma lista plana.
- **CORS**: só é necessário se algum dia o navegador chamar a API direto.
- **Configuração por ambiente**: `SECRET_KEY`, `DEBUG` e `ALLOWED_HOSTS` no
  `settings.py` precisam virar variáveis de ambiente antes de qualquer deploy.
- **Empacotamento**: um `Dockerfile`/`docker compose` deixaria a execução reproduzível.

## Segurança

Este é um projeto de estudo e a configuração atual **não é segura para produção**:

- `SECRET_KEY` está fixa no `settings.py` e `DEBUG = True`, o que expõe tracebacks;
- `ALLOWED_HOSTS` vazio e ausência de HTTPS/HSTS;
- não há autenticação, então qualquer cliente consegue criar, alterar e apagar dados;
- `db.sqlite3` guarda os dados locais e não deve ser versionado.

Antes de expor na internet: mover segredo para `.env`, desligar `DEBUG`, definir
`ALLOWED_HOSTS`, restringir escrita por autenticação e adicionar rate limiting.

## Licença

Nenhuma licença definida até o momento. Para um repositório público, uma licença
permissiva como a MIT (arquivo `LICENSE` na raiz) deixa claro o que outros podem fazer
com o código.
