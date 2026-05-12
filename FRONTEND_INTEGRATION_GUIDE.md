# Frontend Integration Guide

## 📋 Visão Geral

Este guia descreve como o frontend Express Commerce se integra com o backend TechShop.

**Princípio Fundamental:** O **frontend se adapta ao backend**. A API define o contrato.

---

## 🎯 Arquivos Criados

### 1. `docs/FRONTEND_INTEGRATION.md`
Plano estratégico completo de integração, incluindo:
- Arquitetura de integração
- Endpoints da API disponíveis
- Dados mock no backend
- Fluxo de integração por página
- Roadmap de implementação
- Contrato de dados

### 2. `static/js/api.js`
Módulo JavaScript com 4 classes para comunicação com API:

#### `CartManager`
```javascript
CartManager.addItem(productId, quantity)        // POST /cart/add
CartManager.removeItem(productId)               // DELETE /cart/remove/<id>
CartManager.getSummary()                        // GET /cart/summary
CartManager.applyCoupon(couponCode)             // POST /cart/apply-coupon
CartManager.removeCoupon()                      // DELETE /cart/coupon
```

#### `SearchManager`
```javascript
SearchManager.search(query, category)           // GET /api/search?q=...
SearchManager.isValidQuery(query)               // Validação (min 2 chars)
```

#### `NotificationManager`
```javascript
NotificationManager.success(message)            // Toast verde
NotificationManager.error(message)              // Toast vermelho
```

#### `FormatManager`
```javascript
FormatManager.formatCurrency(value)             // R$ 1.234,56
FormatManager.formatPercent(value)              // 25,5%
FormatManager.truncate(text, length)            // "texto..."
```

### 3. `static/js/cart.js`
Inicialização de event listeners e handlers:
- `initCartForm()` - Formulário de cupom
- `initRemoveButtons()` - Remover do carrinho
- `initSearchForm()` - Busca de produtos
- `updateCartSummary(summary)` - Atualizar UI
- `addProductToCart(productId)` - Adicionar ao carrinho
- `applyCouponAction(code)` - Aplicar cupom
- `removeCouponAction()` - Remover cupom

### 4. `frontend/index.html` (Atualizado)
Adicionados links aos scripts de integração:
```html
<script src="/static/js/api.js"></script>
<script src="/static/js/cart.js"></script>
```

---

## 🔌 Como Usar

### No Frontend (Página HTML)

#### Adicionar ao Carrinho
```html
<button onclick="addProductToCart(1, 'iPhone')">
  Adicionar ao Carrinho
</button>
```

#### Remover do Carrinho
```html
<button data-remove-product="1">Remover</button>
```

#### Formulário de Cupom
```html
<form id="couponForm">
  <input type="text" name="coupon_code" placeholder="Código do cupom">
  <button type="submit">Aplicar</button>
</form>
```

#### Exibir Resumo do Carrinho
```html
<div id="cartSubtotal">R$ 0,00</div>
<div id="cartCouponDiscount" data-coupon-row>-R$ 0,00</div>
<div id="cartProgressiveDiscount" data-progressive-row>-R$ 0,00</div>
<div id="cartTotal">R$ 0,00</div>
```

---

## 📊 Contrato de Dados

### GET /cart/summary
```json
{
  "subtotal": 2500.00,
  "coupon_discount": 250.00,
  "progressive_discount": 125.00,
  "total": 2125.00
}
```

### POST /cart/apply-coupon
**Request:**
```json
{"code": "SAVE10"}
```

**Response:** CartSummary (acima) ou erro 400/404

---

## 🚀 Roadmap

### Phase 1: Integração Atual ✅
- [x] Plano de integração documentado
- [x] JavaScript API client criado
- [x] Event listeners configurados
- [x] Frontend linkado aos scripts

### Phase 2: Endpoints Faltando ⏳
- [ ] `POST /cart/add` - adicionar ao carrinho
- [ ] `DELETE /cart/remove/<id>` - remover item
- [ ] `GET /product/<id>` - página de produto
- [ ] `GET /search?q=...` - busca de produtos

### Phase 3: Persistência 📋
- [ ] PostgreSQL + SQLAlchemy
- [ ] Autenticação (JWT)
- [ ] Sessões de usuário

---

## 💡 Exemplo Completo

### Frontend (HTML)
```html
<!-- Campo de busca -->
<form data-search-form>
  <input data-search-input type="text" placeholder="Buscar...">
  <button type="submit">Buscar</button>
</form>

<!-- Produto -->
<article>
  <h3>iPhone 13</h3>
  <p>R$ 2.499,00</p>
  <button onclick="addProductToCart(1, 'iPhone 13')">
    Adicionar ao Carrinho
  </button>
</article>

<!-- Carrinho -->
<div id="cartSubtotal">R$ 0,00</div>
<form id="couponForm">
  <input type="text" name="coupon_code" placeholder="SAVE10">
  <button type="submit">Aplicar Cupom</button>
</form>
<div id="cartTotal">R$ 0,00</div>

<!-- Scripts -->
<script src="/static/js/api.js"></script>
<script src="/static/js/cart.js"></script>
```

### Fluxo de Execução
1. Usuário digita "SAVE10" no formulário de cupom
2. Clica "Aplicar Cupom"
3. `initCartForm()` intercepta o submit
4. Chama `CartManager.applyCoupon("SAVE10")`
5. Fetch POST para `/cart/apply-coupon`
6. Backend valida e retorna CartSummary
7. `updateCartSummary(summary)` atualiza UI
8. Toast exibe "Cupom aplicado com sucesso!"

---

## 🛠️ Próximos Passos

1. **Testar página home**
   ```bash
   uv run uvicorn src.main:app --reload
   # Visitar http://localhost:8000/
   ```

2. **Testar página carrinho**
   - Visitar http://localhost:8000/cart
   - Aplicar cupom "SAVE10"
   - Verificar resumo

3. **Implementar endpoints faltando** (Phase 2)
   - `POST /cart/add`
   - `DELETE /cart/remove/<id>`
   - etc.

4. **Adicionar testes E2E** com Playwright
   - Testar fluxo completo de carrinho
   - Testar aplicação de cupom
   - Testar validações

---

## ❓ FAQ

### P: Por que Jinja2 e não React?
**R:** Simplicidade! SSR reduz complexidade, sem Node.js/TypeScript, sem bundle JavaScript grande.

### P: O carrinho é compartilhado entre usuários?
**R:** Sim, atualmente em memória. Phase 3 adiciona persistência com autenticação.

### P: Como adicionar novos produtos?
**R:** Atualmente mockados em `src/main.py`. Phase 3 integra com banco de dados.

### P: E se um cupom expirar enquanto o usuário está usando?
**R:** Backend valida na aplicação - retorna erro 400 se expirado.

---

## 📚 Referências

- [FRONTEND_INTEGRATION.md](docs/FRONTEND_INTEGRATION.md) - Plano estratégico
- [src/main.py](src/main.py) - API FastAPI
- [tests/test_main.py](tests/test_main.py) - Testes de integração
