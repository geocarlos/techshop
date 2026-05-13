# Melhorias Necessarias para o Checkout

## 1. Objetivo

Documentar as melhorias obrigatorias identificadas em [ia_analise.md](../ia_analise.md) aplicando shift-left, para prevenir falhas de seguranca, arquitetura e tipagem o mais cedo possivel no ciclo.

## 2. Escopo e Contexto

- Base de analise: [ia_analise.md](../ia_analise.md)
- Requisitos de produto: [docs/PRD.md](PRD.md)
- Diretrizes de engenharia: [docs/DIRETRIZES_IA.md](DIRETRIZES_IA.md)
- Modulo principal impactado: [src/checkout.py](../src/checkout.py)

## 3. Estrategia Shift-Left

Objetivo do shift-left neste contexto:
1. Detectar defeitos em design e contratos antes da implementacao.
2. Bloquear regressao de seguranca e tipagem antes de abrir PR.
3. Padronizar qualidade com gates objetivos por fase.

### Fase A - Design e modelagem (antes de codificar)

Acoes obrigatorias:
1. Definir contratos Pydantic de entrada e saida de checkout.
2. Definir interfaces de dominio (CheckoutService, PricingService, StockService, PaymentGateway).
3. Mapear ameacas e requisitos de seguranca (dados sensiveis, logs, criptografia/tokenizacao).
4. Registrar politicas de frete e desconto sem numeros magicos no codigo.

Gate de saida da fase:
- Nao iniciar implementacao sem contrato tipado aprovado e responsabilidades separadas por componente.

### Fase B - Implementacao guiada por contratos

Acoes obrigatorias:
1. Implementar por camadas, sem funcoes monoliticas.
2. Validar payloads exclusivamente com modelos tipados.
3. Recalcular preco no backend com fonte confiavel de catalogo.
4. Substituir prints por logging estruturado sem dados sensiveis.

Gate de saida da fase:
- Nenhum retorno ambiguo (string/dict) e nenhuma dependencia externa concreta no dominio.

### Fase C - Validacao automatizada pre-PR

Acoes obrigatorias:
1. Rodar testes unitarios no padrao AAA para regras de checkout.
2. Rodar validacao de tipo estatica para o modulo.
3. Garantir testes de cenarios negativos (fraude de preco, estoque insuficiente, payload invalido).

Gate de saida da fase:
- PR so pode ser aberto com evidencias de testes e validacao de tipos sem erros.

### Fase D - Revisao de PR e merge

Acoes obrigatorias:
1. Revisar aderencia ao PRD com foco em seguranca e escalabilidade.
2. Revisar SOLID e acoplamento entre dominio e infraestrutura.
3. Confirmar ausencia de secrets, mocks de treino e dados sensiveis hardcoded.

Gate de saida da fase:
- Merge bloqueado se qualquer item P0 estiver pendente.

## 4. Melhorias Bloqueantes (P0)

### P0.1 Seguranca de dados de pagamento

Problema:
- Presenca de informacao sensivel hardcoded e fluxo sem criptografia/tokenizacao.

Acoes necessarias:
1. Remover qualquer dado sensivel hardcoded do codigo.
2. Garantir tokenizacao/abstracao para dados de pagamento.
3. Substituir prints por logging estruturado sem exposicao de dados sensiveis.
4. Definir contrato de seguranca para payloads de pagamento.
5. Incluir checklist de seguranca na fase de design (shift-left).

Criterios de aceite:
- Nao existe campo de cartao hardcoded no repositorio.
- Logs nao exibem dados pessoais ou de pagamento.
- Checkout atende o requisito de seguranca definido em [docs/PRD.md](PRD.md).

### P0.2 Integridade de preco

Problema:
- Valor de item e total sao derivados de entrada do cliente, permitindo manipulacao de preco.

Acoes necessarias:
1. Resolver preco no servidor a partir de catalogo confiavel.
2. Validar consistencia de itens/quantidades recebidas.
3. Recalcular total integralmente no backend.
4. Cobrir tentativa de manipulacao de preco com testes negativos pre-PR.

Criterios de aceite:
- Nenhum preco vindo do cliente e usado como fonte de verdade.
- Tentativas de manipulacao de preco resultam em erro de validacao.

### P0.3 Refatoracao arquitetural (SOLID)

Problema:
- Funcao unica concentrando validacao, calculo, estoque, pagamento e retorno.

Acoes necessarias:
1. Separar responsabilidades em servicos/componentes:
   CheckoutService (orquestracao), StockService (disponibilidade), PricingService (subtotal/descontos/frete), PaymentGateway (abstracao de pagamento).
2. Aplicar inversao de dependencia para gateway de pagamento.
3. Isolar regras de negocio em politicas extensaveis.
4. Aprovar desenho de componentes antes da implementacao (shift-left de arquitetura).

Criterios de aceite:
- Nao existe funcao monolitica com responsabilidades cruzadas.
- Gateway pode ser trocado sem alterar regra de negocio.

## 5. Melhorias Importantes (P1)

### P1.1 Tipagem estrita e contratos consistentes

Problema:
- Ausencia de type hints e retorno inconsistente (string/dict).

Acoes necessarias:
1. Definir modelos Pydantic para request/response:
   CheckoutRequest, CheckoutItemRequest e CheckoutResult.
2. Tipar 100% das assinaturas publicas de checkout.
3. Padronizar erros com modelo unico (ex.: ErrorResponse).
4. Incluir validacao de tipos como gate obrigatorio antes de abrir PR.

Criterios de aceite:
- API de checkout nao retorna tipos ambiguos.
- Codigo de checkout passa validacao estatica de tipos.

### P1.2 Regras de negocio configuraveis

Problema:
- Numeros magicos e regras hardcoded para frete/desconto.

Acoes necessarias:
1. Externalizar limites e percentuais para configuracao.
2. Documentar politicas de desconto/frete.
3. Cobrir regras com testes unitarios.
4. Definir exemplos de contrato de regra ainda na fase de design.

Criterios de aceite:
- Nao ha numeros magicos no fluxo de checkout.
- Alteracao de politica nao exige reescrita da orquestracao.

### P1.3 Integracao com fluxo oficial da aplicacao

Problema:
- Fluxo de checkout atual esta desconectado da camada FastAPI e dos modelos existentes.

Acoes necessarias:
1. Expor endpoint de checkout em [src/main.py](../src/main.py).
2. Integrar com modelos Pydantic ja adotados no projeto.
3. Garantir resposta de API consistente para frontend.
4. Validar contrato da API com testes de integracao antes do merge.

Criterios de aceite:
- Existe endpoint funcional de checkout com contrato tipado.
- Fluxo de checkout usa os mesmos padroes arquiteturais do projeto.

## 6. Melhorias Desejaveis (P2)

### P2.1 Escalabilidade e desempenho

Acoes necessarias:
1. Preparar interfaces para persistencia e filas/eventos futuros.
2. Evitar acoplamento com mocks no codigo de producao.
3. Definir pontos de observabilidade (metrica de latencia e taxa de erro).
4. Definir SLOs iniciais de checkout ainda na fase de desenho tecnico.

Criterios de aceite:
- Componentes podem evoluir para integracoes reais sem refatoracao estrutural.
- Metricas basicas de checkout estao definidas.

## 7. Plano de Implementacao Recomendado (Shift-Left)

1. Fase A: fechar contratos, arquitetura e ameacas antes de codificar.
2. Fase B: implementar componentes coesos com inversao de dependencia.
3. Fase C: executar testes AAA, validacao de tipos e cenarios negativos pre-PR.
4. Fase D: revisar PR com gates de seguranca, PRD e SOLID antes de merge.
5. Pos-merge: monitorar metricas de checkout e ajustar politicas sem refatoracao estrutural.

## 8. Checklist para liberar merge

- [ ] Sem dados sensiveis hardcoded.
- [ ] Precos calculados exclusivamente no backend.
- [ ] Checkout refatorado em componentes coesos.
- [ ] Dependencias externas acessadas por abstracao.
- [ ] Request/response 100% tipados.
- [ ] Erros padronizados.
- [ ] Endpoint de checkout integrado ao app.
- [ ] Testes cobrindo cenarios principais e falhas.
- [ ] Testes negativos de seguranca e fraude executados antes do PR.
- [ ] Validacao de tipos executada antes do PR.
- [ ] Evidencia de revisao arquitetural na fase de design.
- [ ] Evidencia de aderencia a [docs/PRD.md](PRD.md).

## 9. Definicao de pronto por fase

Definicao de pronto para codificar:
- Contratos de entrada/saida definidos e revisados.
- Modelo de componentes aprovado com SOLID e DIP.
- Requisitos de seguranca mapeados para implementacao.

Definicao de pronto para abrir PR:
- Testes unitarios e de integracao relevantes executados.
- Validacao de tipos sem erros no modulo de checkout.
- Sem logs sensiveis, sem dados hardcoded e sem retorno ambiguo.
