# TechShop

Uma API de e-commerce desenvolvida com FastAPI para gerenciar produtos e carrinhos de compra.

## Descrição

Este projeto implementa a base para uma plataforma de e-commerce chamada TechShop. Ele inclui a estrutura inicial do projeto, modelos de dados com Pydantic, e a lógica de negócio para um carrinho de compras.

A aplicação é construída utilizando FastAPI, garantindo alta performance e uma documentação de API interativa (via Swagger UI).

## Funcionalidades Implementadas

- Gerenciamento de carrinho:
    - Adicionar item
    - Remover item
    - Calcular subtotal
- Desconto progressivo:
    - 10% para totais acima de R$ 500
    - 20% para totais acima de R$ 1000
- Cupons percentuais:
    - Aplicar cupom com validação de ativo/expiração/compra mínima
    - Remover cupom aplicado
    - Ordem de cálculo: cupom -> desconto progressivo
- Resumo detalhado do carrinho:
    - subtotal
    - coupon_discount
    - progressive_discount
    - total

## Estrutura do Projeto

```
techshop/
├── frontend/
│   └── index.html            # Home mockada em HTML + Tailwind
├── src/
│   ├── cart.py              # Lógica de carrinho com cupom
│   ├── main.py              # API FastAPI
│   └── models.py            # Modelos Pydantic
├── tests/
│   ├── test_cart.py         # Testes unitários do carrinho
│   └── test_main.py         # Testes de integração da API
├── docs/
│   ├── BACKLOG.md
│   ├── DIRETRIZES_IA.md
│   ├── PRD.md
│   ├── INTEGRATION_PLAN.md
│   ├── plan-expressCommerce.prompt.md
│   ├── diagrama-er.md
│   └── diagrama-fluxo.md
├── .gitignore
├── pyproject.toml
├── README.md
└── uv.lock
```

### Descrição dos Diretórios

- `src/`: Código-fonte do backend (FastAPI).
  - `main.py`: Ponto de entrada da API FastAPI com endpoints de carrinho e cupom.
  - `models.py`: Modelos Pydantic (Product, CartItem, Coupon, CartSummary).
  - `cart.py`: Lógica de negócio do carrinho com gerenciamento de cupons.

- `frontend/`: Código-fonte do frontend (mockups iniciais em HTML + Tailwind).
  - `index.html`: Home page responsiva com barra de busca, categorias e grid de produtos.

- `tests/`: Suíte de testes automatizados.
  - `test_cart.py`: Testes unitários da lógica de carrinho e cupom (padrão AAA).
  - `test_main.py`: Testes de integração da API FastAPI.

- `docs/`: Documentação e especificações.
  - `PRD.md`: Documento de Requisitos do Produto.
  - `BACKLOG.md`: User Stories.
  - `DIRETRIZES_IA.md`: Diretrizes para desenvolvimento com IA.
  - `INTEGRATION_PLAN.md`: Plano de integração entre front-end e back-end.
  - `plan-expressCommerce.prompt.md`: ADR com recomendações arquiteturais.
  - `diagrama-er.md`: ER do marketplace de eletrônicos usados.
  - `diagrama-fluxo.md`: Fluxo de jornada do usuário.

## Dependências

O projeto utiliza as seguintes bibliotecas:

-   `fastapi`: Framework web para a construção da API.
-   `httpx`: Cliente HTTP utilizado nos testes da API (TestClient).
-   `pydantic`: Para validação e modelagem de dados.
-   `uvicorn`: Servidor ASGI para rodar a aplicação FastAPI.

As dependências de desenvolvimento incluem `mypy`, `pytest`, `ruff`, entre outras, e estão listadas no arquivo `pyproject.toml`.

## Instalação e Uso com `uv`

Este projeto utiliza `uv` como gerenciador de pacotes e ambiente virtual, por ser extremamente rápido.

### Pré-requisitos

Certifique-se de que você tem o `uv` instalado. Se não tiver, você pode instalá-lo com:

```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Passos para Instalação

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-repositorio>
    cd techshop
    ```

2.  **Crie o ambiente virtual e instale as dependências:**
    O `uv` pode criar o ambiente e instalar as dependências de uma só vez.

    ```bash
    uv sync
    ```
    Este comando irá ler o `pyproject.toml`, criar um ambiente virtual `.venv` no diretório atual e instalar todas as dependências necessárias.

### Executando a Aplicação

1.  **Ative o ambiente virtual:**
    ```bash
    # Windows
    .venv\Scripts\activate

    # macOS / Linux
    source .venv/bin/activate
    ```

2.  **Inicie o servidor:**
    A aplicação principal está em `src/main.py`. Para executá-la com `uv`:

    ```bash
    uv run uvicorn src.main:app --reload
    ```
    -   `src.main:app`: Aponta para a instância `app` do FastAPI no arquivo `src/main.py`.
    -   `--reload`: Faz com que o servidor reinicie automaticamente após alterações no código.

3.  **Acesse a API:**
    A API estará disponível em `http://127.0.0.1:8000`.
    A documentação interativa (Swagger UI) pode ser acessada em `http://127.0.0.1:8000/docs`.

## Executando Testes

Para rodar os testes com `uv`:

```bash
uv run pytest -q
```

## Endpoints de Carrinho e Cupom

- `GET /`: Status da aplicação.
- `GET /cart/summary`: Retorna o resumo atual do carrinho com descontos aplicados.
- `POST /cart/apply-coupon`: Aplica um cupom percentual.
- `DELETE /cart/coupon`: Remove o cupom aplicado.

### Exemplo: Aplicar Cupom

Request:

```http
POST /cart/apply-coupon
Content-Type: application/json

{
    "code": "SAVE10"
}
```

Response (exemplo):

```json
{
    "subtotal": 600.0,
    "coupon_discount": 60.0,
    "progressive_discount": 54.0,
    "total": 486.0
}
```
