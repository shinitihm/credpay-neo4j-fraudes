# CredPay Neo4j — Design

## Intenção
Protótipo Neo4j para detectar fraude na fintech fictícia CredPay Digital (atividade avaliativa "Neo4j em Fintechs"). Entrega: PDF (Word→PDF) + repositório.

## Metas / não-metas
- Meta: modelo de grafo, dataset sintético, 7 consultas Cypher (uma por padrão do enunciado), resultados reais, justificativa, comparação com SQL.
- Não-meta: GDS/PageRank (Aura Free não tem), API, front-end, escala de 2M clientes.
- Anti-meta: consulta que "acha" fraude só por dado forjado sem exercitar o padrão; segredo no git.

## Abordagens
A) Cypher puro + Python de apoio **(escolhida pelo usuário)**; B) só documento sem executar; C) GDS (inviável no Aura Free).

## Modelo
Nós: Cliente, Conta, Cartao, Dispositivo, IP, Endereco. Transação = relação `(:Conta)-[:TRANSFERIU {id,valor,data}]->(:Conta)` (aresta direta simplifica cadeias/ciclos; nó Transacao só se precisássemos de propriedades-nó). Outras: TITULAR_DE, USA_CARTAO, ACESSOU_DE (Conta→Dispositivo), USOU_IP (Conta→IP), MORA_EM (Cliente→Endereco). Conta tem `criada_em`.
Dados do enunciado (C001–C004, A001–A004, T001–T004, ciclo) entram intactos; o resto é sintético.

## Os 7 padrões → consultas
1 vários clientes/contas no mesmo dispositivo; 2 clientes distintos no mesmo IP; 3 conta recém-criada recebendo de várias origens; 4 anel/ciclo de transferências; 5 mesmo cartão em contas de clientes diferentes; 6 cadeia de transferências entre pares sem histórico prévio; 7 passagem rápida (recebe e repassa em < N min).

## Restrições
Segredos só em `.env` (ignorado). TLS verificado via certifi. `DECISOES.md` local, ignorado. Paleta: D8D8F6, B18FCF, 978897, 494850, 2C2C34. Idioma pt-BR.

## Agentes
Orquestrador (Opus: decide), Executor (Sonnet: constrói), Auditor ponytail (Opus: corta excesso e valida consultas), Professor (Opus: avalia como especialista em BD).
