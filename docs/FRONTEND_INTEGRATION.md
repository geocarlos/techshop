# Plano de Integração Frontend-Backend

## 1. Visão Geral da Estratégia

**Objetivo:** Adaptar o frontend (Express Commerce) para se integrar completamente com o backend (TechShop API).

**Princípio:** Frontend se adapta ao backend - a API define o contrato.

---

## 2. Arquitetura de Integração

### Stack Frontend
- **HTML/Jinja2:** Rendering server-side (templates/)
- **Tailwind CSS:** Styling via CDN
- **Vanilla JavaScript:** Interatividade no cliente (sem framework)
- **Fetch API:** Comunicação com backend

### Stack Backend (Atual)
- **FastAPI:** Servidor HTTP + JSON API
- **Jinja2:** Rendering de páginas HTML
- **Pydantic:** Validação de modelos
- **Python:** Lógica de negócio (cart, discounts, coupons)

---

## 3. Endpoints da API Disponíveis

| Método | Endpoint | Response | Uso |
|--------|----------|----------|-----|
| `GET` | `/` | HTML | Página home renderizada |
| `GET` | `/cart` | HTML | Página do carrinho renderizada |
| `GET` | `/api/status` | JSON | Health check |
| `GET` | `/cart/summary` | JSON | Resumo do carrinho atual |
| `POST` | `/cart/apply-coupon` | JSON | Aplicar cupom ao carrinho |
| `DELETE` | `/cart/coupon` | JSON | Remover cupom aplicado |

---

## 4. Dados Mock no Backend

### Produtos em Destaque (FEATURED_PRODUCTS)
```python
[
  {id: 1, name: "iPhone 13 128GB — Meia-noite", price: 2499.00},
  {id: 2, name: "MacBook Air M1 8GB 256GB", price: 5800.00},
  {id: 3, name: "PlayStation 5 + 2 Controles", price: 3200.00},
  {id: 4, name: "Samsung Galaxy Tab S7 — 128GB", price: 1850.00},
  {id: 5, name: "Sony WH-1000XM5 — Noise Cancelling", price: 1100.00},
  {id: 6, name: "Canon EOS R50 + Lente 18-45mm", price: 4300.00},
]
```

### Cupons Disponíveis (COUPON_CATALOG)
```json
{
  "SAVE10": {"code": "SAVE10", "discount_percent": 10, "min_purchase": 100, "is_active": true},
  "VIP15": {"code": "VIP15", "discount_percent": 15, "min_purchase": 300, "expires_at": "+30 dias"},
  "INACTIVE5": {"code": "INACTIVE5", "discount_percent": 5, "is_active": false}
}
```

---

## 5. Fluxo de Integração por Página

### 5.1 Página Home (`/`)
**Renderização:** Server-side (GET /)
**Estrutura:**
- Header com logo, busca, carrinho
- Carousel de banners
- 6 categorias principais
- Grid de produtos em destaque (dados do backend)
- Footer com links

**Dados Dinamizados:**
- `featured_products` - loop sobre produtos do backend
- `cart_count` - número de itens no carrinho
- Links de busca para `/search?category=...`

**Interatividade:**
```javascript
// Adicionar item ao carrinho (POST via fetch)
async function addToCart(productId, quantity) {
  const response = await fetch('/cart/add', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({product_id: productId, quantity})
  });
  updateCartBadge();
}

// Buscar produtos (GET)
async function searchProducts(query) {
  const response = await fetch(`/api/search?q=${query}`);
  renderSearchResults(await response.json());
}
```

### 5.2 Página do Carrinho (`/cart`)
**Renderização:** Server-side (GET /cart)
**Estrutura:**
- Lista de itens no carrinho
- Subtotal, descontos, total
- Formulário para aplicar cupom
- Botão checkout

**Dados Dinamizados:**
- `cart_items` - items atuais
- `cart_summary` - breakdown de descontos
  - `subtotal`
  - `coupon_discount` (se aplicável)
  - `progressive_discount` (baseado em valor)
  - `total`

**Interatividade:**
```javascript
// Remover item do carrinho (DELETE)
async function removeFromCart(productId) {
  const response = await fetch(`/cart/remove/${productId}`, {method: 'DELETE'});
  location.reload();
}

// Aplicar cupom (POST)
async function applyCoupon(code) {
  const response = await fetch('/cart/apply-coupon', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({code})
  });
  const summary = await response.json();
  updateCartSummary(summary);
}
```

### 5.3 Página de Produto (FUTURA)
**Endpoint:** `GET /product/<id>`
**Renderização:** Server-side
**Estrutura:**
- Imagem do produto
- Descrição completa
- Avaliações
- Opções de compra (quantidade, variações)
- Botão "Adicionar ao carrinho"

### 5.4 Página de Busca (FUTURA)
**Endpoint:** `GET /search?q=...&category=...`
**Renderização:** Server-side
**Estrutura:**
- Formulário de busca refinada
- Filtros por categoria, preço, avaliação
- Grid de resultados

---

## 6. Mudanças Necessárias no Backend

### Phase 1 (Imediata)
✅ `GET /` renderizar HTML com produtos
✅ `GET /cart` renderizar HTML com resumo
✅ `GET /cart/summary` retornar JSON
✅ `POST /cart/apply-coupon` validar e aplicar
✅ `DELETE /cart/coupon` remover

### Phase 2 (Próxima)
⏳ `POST /cart/add` - adicionar item ao carrinho
⏳ `DELETE /cart/remove/<id>` - remover item
⏳ `GET /product/<id>` - detalhes do produto
⏳ `GET /search?q=...` - buscar produtos

### Phase 3 (Persistência)
📋 PostgreSQL + SQLAlchemy
📋 Autenticação de usuário (JWT)
📋 Sessões de carrinho

---

## 7. Estrutura de Pastas (Proposta)

```
frontend/                    # Referência (expressCommerce original)
├── index.html              # Mockup estático
├── assets/
│   └── images/            # Imagens locais

templates/                  # Renderizados pelo FastAPI
├── base.html              # Layout base (✅ pronto)
├── index.html             # Home com loop de produtos (✅ pronto)
├── cart.html              # Carrinho com cupom (✅ pronto)
├── product.html           # Detalhe do produto (⏳)
└── search.html            # Resultados de busca (⏳)

static/                     # Assets estáticos servidos
├── css/
│   └── custom.css         # Estilos adicionais (opcional)
├── js/
│   ├── cart.js            # Lógica do carrinho
│   ├── search.js          # Busca
│   └── utils.js           # Funções compartilhadas
└── images/
    └── products/          # Imagens de produtos
```

---

## 8. Estratégia de Adaptação

### Problema: Frontend tem muitos produtos mockados
**Solução:** Backend fornece dados via API

### Problema: Frontend é estático, backend é dinâmico
**Solução:** Usar Jinja2 para renderizar loops:
```html
{% for product in featured_products %}
  <article class="product-card">
    <h3>{{ product.name }}</h3>
    <p>R$ {{ "%.2f"|format(product.price) }}</p>
  </article>
{% endfor %}
```

### Problema: Carrinho é session, frontend é stateless
**Solução:** 
- Backend mantém estado em memória (Phase 1)
- Frontend envia requisições POST/DELETE
- Frontend atualiza UI com resposta JSON

### Problema: Cupons precisam validação
**Solução:** Backend valida (ativo, expirado, min_purchase)
- Frontend envia código
- Backend retorna erro ou CartSummary
- Frontend exibe mensagem ou atualiza resumo

---

## 9. Roadmap de Implementação

### Week 1: Integração Frontend ao Backend Existente
- [x] Criar templates base.html, index.html, cart.html
- [x] Integrar Jinja2 em FastAPI
- [ ] Adicionar JavaScript para interatividade (cart.js)
- [ ] Testar página home com produtos reais
- [ ] Testar página carrinho com cupom

### Week 2: Extensão de Endpoints
- [ ] POST /cart/add - adicionar ao carrinho
- [ ] DELETE /cart/remove/<id> - remover item
- [ ] GET /product/<id> - página de produto
- [ ] GET /search?q=... - busca básica
- [ ] Testes de integração

### Week 3: Persistência e Autenticação
- [ ] PostgreSQL setup + SQLAlchemy models
- [ ] Migrations com Alembic
- [ ] JWT autenticação
- [ ] Sessions de carrinho por usuário

### Week 4: Refinamento
- [ ] SEO + Open Graph
- [ ] Performance (caching, CDN)
- [ ] Analytics
- [ ] Documentação de API

---

## 10. Contrato de Dados

### CartSummary (JSON Response)
```json
{
  "subtotal": 2500.00,
  "coupon_discount": -250.00,
  "progressive_discount": -125.00,
  "total": 2125.00
}
```

### ApplyCouponRequest (JSON Body)
```json
{
  "code": "SAVE10"
}
```

### ErrorResponse (JSON Body)
```json
{
  "detail": "Cupom não encontrado" // ou outro mensagem
}
```

---

## 11. Checklist de Validação

- [ ] Frontend carrega página home sem erros
- [ ] Produtos em destaque exibem dados do backend
- [ ] Carrinho exibe produtos adicionados
- [ ] Cupom aplicado atualiza resumo corretamente
- [ ] Progressos de descontos são calculados
- [ ] Links de navegação funcionam
- [ ] Responsivo em mobile/tablet
- [ ] Testes E2E passam

---

## 12. Notas Importantes

1. **Jinja2 vs React:** Decidimos por SSR (Jinja2) para simplificar - sem JavaScript bundle, sem Node.js
2. **Estado do Carrinho:** Atualmente em memória - usuários compartilham carrinho
3. **Autenticação:** Futura - por enquanto sem login
4. **Performance:** Sem cache por enquanto - adicionar após Phase 2
5. **Imagens:** Usando Unsplash no mockup - usar CDN próprio em produção
