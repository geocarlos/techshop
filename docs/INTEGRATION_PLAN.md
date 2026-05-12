# Plano de Integração: Front-end Express Commerce + Back-end TechShop

## Visão Geral

Este documento mapeia como integrar o front-end Express Commerce (UI/HTML em Tailwind) com o back-end TechShop (API FastAPI com gerenciamento de cupons e carrinho).

## Estrutura Atual

```
techshop/
├── src/                        # Backend (Python/FastAPI)
│   ├── cart.py                # Lógica de carrinho com cupom
│   ├── main.py                # API FastAPI
│   └── models.py              # Modelos Pydantic
├── frontend/                  # Frontend (HTML/TailwindCSS)
│   └── index.html             # Home mockada
├── docs/
│   ├── diagrama-er.md         # ER do Express Commerce
│   ├── diagrama-fluxo.md      # Fluxo de usuário
│   ├── plan-expressCommerce.prompt.md  # ADR (Monólito Modular + Next.js)
│   └── prompts_express_commerce.md     # Prompts utilizados
└── tests/                     # Testes (Python/pytest)
```

## Etapas de Integração

### Fase 1: Construir Front-end em Next.js (Recomendado)

**Justificativa:** A ADR recomenda Next.js para unificar frontend + API Routes. No MVP, você pode usar a API FastAPI existente como backend e construir o frontend em Next.js separadamente.

**Estrutura proposta:**
```
express-commerce-frontend/    # Novo repositório (opcional)
├── app/                      # Next.js App Router
│   ├── page.tsx             # Home (baseado em index.html)
│   ├── cart/page.tsx        # Carrinho
│   └── api/                 # API Routes (proxy para FastAPI)
├── components/              # Componentes React
├── public/                  # Assets estáticos
└── styles/                  # Tailwind config
```

**Ações:**
1. Implementar components React baseados nos mockups do `frontend/index.html`
2. Criar API Routes em Next.js que chamam a API FastAPI
3. Integrar autenticação (NextAuth.js)

### Fase 2: Conectar Front-end ao Back-end FastAPI

**Endpoints de integração (já implementados):**
```
GET  /cart/summary
POST /cart/apply-coupon
DELETE /cart/coupon
```

**Exemplo de chamada do front-end (Next.js):**
```typescript
// app/api/cart/route.ts
import { CartSummary } from '@/types/cart';

export async function GET(): Promise<CartSummary> {
  const response = await fetch('http://localhost:8000/cart/summary');
  return response.json();
}

export async function POST(request: Request): Promise<CartSummary> {
  const { code } = await request.json();
  const response = await fetch('http://localhost:8000/cart/apply-coupon', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code }),
  });
  return response.json();
}
```

### Fase 3: Persistência de Carrinho (Futuro)

**Atual:** Carrinho em memória (não persiste entre requisições)

**Melhorias recomendadas:**
1. Carrinho persistido no PostgreSQL (via Prisma)
2. Associar carrinho a usuário logado
3. Migrar para Redis para performance em alta concorrência

### Fase 4: Autenticação e Usuários

**Recomendação:** Integrar NextAuth.js + Supabase Auth (conforme ADR)

**Passos:**
1. Adicionar tabela `users` no banco de dados
2. Implementar endpoints de autenticação no FastAPI
3. Conectar NextAuth.js ao backend

## Fluxo de Desenvolvimento Recomendado

1. **Semana 1:** Construir home em Next.js (baseado em `frontend/index.html`)
2. **Semana 2:** Integrar carrinho com cupom (chamar FastAPI)
3. **Semana 3:** Autenticação e persistência de usuário
4. **Semana 4:** Páginas de detalhe de produto e checkout

## Tecnologias Sugeridas

| Camada | Tecnologia | Status |
|---|---|---|
| Backend API | FastAPI (Python) | ✅ Implementado |
| Frontend | Next.js 14 (React) | 📋 Planejado |
| BD Relacional | PostgreSQL | 📋 A integrar |
| ORM Backend | N/A (fastapi puro) | 📋 Considerar SQLalchemy |
| ORM Frontend | Prisma | 📋 Futuro |
| Autenticação | NextAuth.js + Supabase | 📋 Futuro |

## Próximas Ações

- [ ] Criar repositório Next.js ou migrar `frontend/` para TypeScript
- [ ] Adicionar persistência de carrinho no FastAPI (BD)
- [ ] Implementar CORS no FastAPI para aceitar requisições do front
- [ ] Criar testes e2e para fluxos de carrinho + cupom

## Referências

- ADR: `docs/plan-expressCommerce.prompt.md`
- Diagramas: `docs/diagrama-er.md`, `docs/diagrama-fluxo.md`
- Mockup Home: `frontend/index.html`
- API Docs: `http://localhost:8000/docs` (swagger ao iniciar o backend)
