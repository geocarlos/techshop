# Plano de Integração: Front-end Express Commerce + Back-end TechShop

## Visão Geral

Este documento mapeia como integrar o front-end Express Commerce (UI/HTML em Tailwind) com o back-end TechShop (API FastAPI com gerenciamento de cupons e carrinho) usando **Jinja2** como template engine.

## Estrutura Atual

```
techshop/
├── src/                        # Backend (Python/FastAPI)
│   ├── cart.py                # Lógica de carrinho com cupom
│   ├── main.py                # API FastAPI + rotas renderizadas com Jinja2
│   └── models.py              # Modelos Pydantic
├── templates/                 # Templates Jinja2 (renderização servidor)
│   ├── base.html              # Template base com header/footer
│   ├── index.html             # Home com produtos em destaque
│   └── cart.html              # Página do carrinho
├── frontend/                  # Frontend mockups (referência)
│   └── index.html             # Home mockada em HTML puro
├── docs/
│   ├── diagrama-er.md         # ER do Express Commerce
│   ├── diagrama-fluxo.md      # Fluxo de usuário
│   ├── plan-expressCommerce.prompt.md  # ADR (Monólito Modular + Next.js)
│   └── prompts_express_commerce.md     # Prompts utilizados
└── tests/                     # Testes (Python/pytest)
```

## Etapas de Integração

### Fase 1: Renderizar Templates com Jinja2 (✅ Em Progresso)

**Justificativa:** Usar Jinja2 permite renderização servidor (SSR) nativa no FastAPI, eliminando complexidade de cliente JavaScript e facilitando integração com lógica de backend (carrinho, cupom).

**Estrutura implementada:**
```
templates/
├── base.html              # Template base com Tailwind CSS
│   ├── Header com logo, menu, carrinho
│   ├── Footer com links e copyright
│   └── Bloco {% block content %} para herança
├── index.html             # Home herdando de base.html
│   ├── Hero section com barra de busca
│   ├── Categorias (6 ícones)
│   └── Grid de produtos (loop Jinja2)
└── cart.html              # Carrinho herdando de base.html
    ├── Lista de itens do carrinho
    ├── Resumo com cupom aplicado
    └── Totais (subtotal, descontos, total)
```

**Rotas implementadas:**
```
GET  /              → renderiza index.html (home)
GET  /cart          → renderiza cart.html (carrinho)
```

**Exemplo de uso de Jinja2 em templates:**
```html
{% for product in featured_products %}
  <div class="product-card">
    <h3>{{ product.name }}</h3>
    <p class="price">R$ {{ "%.2f"|format(product.price) }}</p>
  </div>
{% endfor %}
```

### Fase 2: Persistência de Carrinho no Banco de Dados

**Atual:** Carrinho em memória (não persiste entre requisições/usuários)

**Melhorias necessárias:**
1. Criar tabela `cart` no PostgreSQL (com user_id, product_id, quantity)
2. Implementar camada de persistência em `src/cart.py`
3. Adicionar SQLAlchemy para ORM
4. Associar carrinho a sessão de usuário (cookies/sessão HTTP)

**Estrutura de banco (recomendada):**
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cart_items (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  product_id INTEGER,
  quantity INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Fase 3: Autenticação e Gerenciamento de Sessão

**Recomendação:** Integrar autenticação simples com sessões HTTP (cookies)

**Passos:**
1. Implementar endpoints de login/logout
2. Adicionar middleware de sessão (FastAPI-Sessions)
3. Associar carrinho a user_id via sessão
4. Adicionar template de login

### Fase 4: Páginas Adicionais e E-commerce Completo

**Páginas a implementar:**
1. Página de detalhes do produto (`/product/<id>`)
2. Página de busca e filtros (`/search?q=...&category=...`)
3. Página de checkout
4. Página de confirmação de pedido

## Fluxo de Desenvolvimento Recomendado

1. **Sprint 1:** ✅ Templates com Jinja2 (home + carrinho)
2. **Sprint 2:** 📋 Persistência de carrinho em BD + Autenticação
3. **Sprint 3:** 📋 Página de detalhes + Busca de produtos
4. **Sprint 4:** 📋 Checkout e confirmação de pedido

## Tecnologias Stack Atual

| Camada | Tecnologia | Status |
|---|---|---|
| **Backend** | FastAPI (Python 3.12+) | ✅ Implementado |
| **Template Engine** | Jinja2 | ✅ Implementado |
| **CSS Framework** | Tailwind CSS (CDN) | ✅ Implementado |
| **BD Relacional** | PostgreSQL | 📋 A integrar |
| **ORM Backend** | SQLAlchemy | 📋 Futuro |
| **Sessão/Auth** | FastAPI-Sessions | 📋 Futuro |
| **Testes** | pytest + Jinja2 rendering | ✅ Em progresso |

## Mudança de Abordagem: Por que Jinja2 em vez de Next.js?

**Razões:**
- **Velocidade de MVP:** Renderização no servidor elimina complexidade de cliente/servidor separado
- **Integração simplificada:** Estado do carrinho vive no backend, não precisa de API REST complexa
- **Menos dependências:** Python + Jinja2 contra TypeScript + Node.js + React
- **Fácil escalabilidade:** Se crescer, sempre é possível migrar para SPA com React/Vue consumindo API do FastAPI

**Trade-offs:**
- Sem interatividade client-side nativa (usa HTML forms + POST/GET)
- Sem SSR complexo de React (mas Jinja2 é mais simples)
- Melhor performance em produção com cache de templates

## Próximas Ações

- [ ] Adicionar dependência `jinja2` no pyproject.toml
- [ ] Testar renderização de templates no servidor (`uv run uvicorn src.main:app --reload`)
- [ ] Implementar persistência de carrinho em BD (PostgreSQL + SQLAlchemy)
- [ ] Integrar autenticação com FastAPI-Sessions
- [ ] Criar página de detalhes de produto
- [ ] Implementar busca e filtros de categoria
- [ ] Criar testes de renderização com Jinja2 (test_templates.py)

## Referências

- **Jinja2 Docs:** https://jinja.palletsprojects.com/
- **FastAPI + Jinja2:** https://fastapi.tiangolo.com/advanced/templates/
- **Tailwind CSS:** https://tailwindcss.com/
- **ADR (Alternativa Next.js):** `docs/plan-expressCommerce.prompt.md`
- **Diagramas:** `docs/diagrama-er.md`, `docs/diagrama-fluxo.md`
- **API Docs:** `http://localhost:8000/docs` (swagger ao iniciar o backend)
