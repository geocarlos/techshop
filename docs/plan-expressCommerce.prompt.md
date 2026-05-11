# ADR-001: Arquitetura e Stack Tecnológica — Express Commerce MVP

## Título
Adoção de Monólito Modular com stack Node.js/Next.js para MVP de marketplace de eletrônicos usados

## Status
Proposto

## Contexto

O Express Commerce é um marketplace simplificado de eletrônicos usados (escopo OLX/Mercado Livre enxuto) com as seguintes funcionalidades para o MVP:

- Cadastro e autenticação de usuários
- Listagem e busca de produtos
- Carrinho de compras
- Fluxo de checkout

**Restrições:**
- Time pequeno (provável 1–3 devs)
- Prazo curto de entrega (MVP)
- Orçamento limitado para infraestrutura
- Necessidade de iteração rápida com base em feedback

Foram avaliadas três abordagens:
1. **Monólito Modular** — código único organizado por domínios (users, products, orders)
2. **Microserviços** — serviços independentes por domínio
3. **Serverless (FaaS)** — funções individuais por endpoint

## Decisão

### 1. Arquitetura: Monólito Modular

Adotar um **Monólito Modular** com separação clara por domínio de negócio:

```
src/
├── modules/
│   ├── users/
│   ├── products/
│   ├── cart/
│   └── orders/
├── shared/
└── infra/
```

**Justificativa:**
- **Microserviços** introduzem overhead operacional (orquestração, comunicação entre serviços, múltiplos deploys) inviável para MVP com time pequeno.
- **Serverless** impõe cold starts, limites de execução e dificulta operações transacionais (checkout), além de elevar complexidade de debug local.
- O Monólito Modular entrega a **velocidade de um monólito** com a **organização que permite extrair microsserviços futuramente** sem reescrita.

---

### 2. Stack Tecnológica

| Camada | Tecnologia | Justificativa |
|---|---|---|
| **Frontend + BFF** | Next.js 14 (App Router) | SSR nativo, roteamento file-based, API Routes eliminam a necessidade de backend separado no MVP |
| **Backend (API)** | Next.js API Routes / Node.js | Unifica frontend e backend em um único repositório e deploy |
| **ORM** | Prisma | Type-safe, migrations automáticas, integração direta com PostgreSQL |
| **Banco de dados** | PostgreSQL (Supabase) | Relacional adequado para o modelo de dados (usuários, produtos, pedidos); Supabase oferece tier gratuito generoso + Auth integrado |
| **Autenticação** | NextAuth.js (Auth.js v5) | Integração nativa com Next.js, suporte a OAuth e credenciais, sessão gerenciada sem backend adicional |
| **Storage de imagens** | Cloudinary (tier free) | Upload direto do cliente, CDN automático, transformações de imagem; free tier cobre o MVP |
| **Hospedagem** | Vercel | Deploy automático via Git, tier gratuito cobre o MVP, integração zero-config com Next.js |
| **Pagamento** | Stripe (modo test → produção) | SDK bem documentado, webhooks confiáveis para atualizar status de pedidos, sem custo até transacionar |

**Custo estimado no MVP:**
- Vercel: **$0** (Hobby plan)
- Supabase: **$0** (Free tier: 500 MB DB, 1 GB storage)
- Cloudinary: **$0** (Free tier: 25 créditos/mês)
- Stripe: **$0** até processar pagamentos reais

---

### 3. Fluxo Arquitetural Resumido

```
Browser
  └── Next.js (Vercel)
        ├── Pages / App Router (UI)
        └── API Routes (BFF)
              ├── NextAuth.js  ──► Supabase (users)
              ├── Products     ──► Supabase via Prisma
              ├── Cart         ──► Supabase via Prisma (ou Redis futuramente)
              └── Orders       ──► Supabase via Prisma + Stripe Webhook
```

## Consequências

### Positivas
- **Velocidade de desenvolvimento alta**: um único repositório, um único deploy, sem orquestração de serviços.
- **Custo zero** para validar o MVP com usuários reais.
- **DX elevado**: Prisma + TypeScript + Next.js oferecem autocompletar e type-safety ponta a ponta.
- **Escalabilidade futura viável**: módulos isolados facilitam extração para microserviços se o produto crescer.
- **Supabase** elimina a necessidade de gerenciar servidor de banco de dados.

### Negativas / Trade-offs
- **Deploy único** significa que um bug crítico derruba todas as funcionalidades (mitigado com testes e feature flags).
- **Vercel Hobby** tem limitações de execução (10s timeout em Serverless Functions) — checkout deve ser implementado com cuidado para não estourar esse limite.
- O **carrinho em banco de dados** (vs. Redis/localStorage) é mais lento para operações de alta frequência, mas é aceitável para o volume de um MVP.
- À medida que o produto cresce, o monólito precisará de disciplina de módulos para não se tornar um "big ball of mud".

### Dívidas técnicas conhecidas e plano de endereçamento

| Dívida | Quando endereçar |
|---|---|
| Carrinho persistido em BD relacional | Migrar para Redis ao atingir concorrência relevante |
| Sem fila de mensagens para notificações | Implementar BullMQ ou Supabase Realtime na fase pós-MVP |
| Auth apenas por email/senha | Adicionar OAuth (Google) na fase de crescimento |
| Stripe em modo test | Ativar modo produção antes do lançamento público |
