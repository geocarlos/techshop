# Prompts — Express Commerce (Desafio A Gênese)

## Passo 1 — ADR (Arquitetura e Stack)

```
Você é um arquiteto de software sênior. Preciso de uma recomendação arquitetural para um marketplace simplificado de eletrônicos usados (estilo OLX/Mercado Livre enxuto), com as seguintes funcionalidades: cadastro de usuários, listagem de produtos, carrinho de compras e fluxo de checkout.

Recomende:
1. A arquitetura mais adequada para um MVP (ex: Monólito Modular, Serverless, MVC clássico)
2. A stack tecnológica (linguagem, framework, banco de dados, hospedagem)
3. Justifique cada escolha considerando: simplicidade, velocidade de desenvolvimento e custo baixo

Formate a resposta como um arquivo ADR (Architecture Decision Record) em Markdown, com as seções: Título, Status, Contexto, Decisão, Consequências.
```

---

## Passo 2 — Diagramas Mermaid

### Diagrama ER

```
Gere o código Mermaid para um Diagrama Entidade-Relacionamento (ER) de um marketplace de eletrônicos usados com as seguintes entidades e relacionamentos:

- Usuário: id, nome, email, senha, telefone, criado_em
- Produto: id, titulo, descricao, preco, categoria, status (disponível/vendido), foto_url, criado_em
- Pedido: id, status (pendente/pago/cancelado), total, criado_em
- Relacionamentos: Um Usuário pode anunciar vários Produtos. Um Usuário pode fazer vários Pedidos. Um Pedido pode conter vários Produtos (tabela intermediária ItemPedido com quantidade e preco_unitario).

Use a sintaxe erDiagram do Mermaid.
```

### Diagrama de Fluxo

```
Gere o código Mermaid para um Diagrama de Fluxo (flowchart) descrevendo a jornada do usuário no seguinte cenário:

1. Usuário acessa a Home
2. Digita um termo na barra de busca
3. Sistema exibe lista de produtos
4. Usuário clica em um produto
5. Visualiza a página de detalhes
6. Clica em "Adicionar ao Carrinho"
7. Sistema verifica se o usuário está logado
   - Se não: redireciona para login → após login, volta ao produto
   - Se sim: adiciona ao carrinho e exibe confirmação
8. Usuário pode continuar comprando ou ir ao checkout

Use a sintaxe flowchart TD do Mermaid.
```

---

## Passo 3 — Home Page (HTML + Tailwind)

```
Crie o código HTML de uma página inicial (Home) para um marketplace de eletrônicos usados chamado "Express Commerce". Use Tailwind CSS via CDN.

A página deve conter:
1. Header com logo "Express Commerce", links de navegação (Home, Categorias, Vender, Entrar) e ícone de carrinho com contador
2. Hero section com uma barra de busca centralizada e destaque da proposta de valor
3. Seção de categorias em ícones (Celulares, Notebooks, Tablets, Games, Áudio, Câmeras)
4. Grid de cards de produtos (mínimo 6 cards mockados) com: foto placeholder, título, preço, localização, botão "Ver mais"
5. Footer simples com links e copyright

Requisitos visuais:
- Esquema de cores: fundo branco, destaque em azul (#2563EB) e laranja (#F97316)
- Design limpo, responsivo e moderno
- Placeholders de imagem usando https://placehold.co/

Retorne apenas o código HTML completo, pronto para salvar como index.html.
```
