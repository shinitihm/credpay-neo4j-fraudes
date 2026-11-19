# CredPay Neo4j Implementation Plan

> **For agentic workers:** use superpowers:subagent-driven-development. Steps use checkboxes.

**Goal:** protótipo Neo4j de detecção de fraude + relatório PDF.
**Architecture:** `src/db.py` conecta; `cypher/*.cypher` contém schema/carga/7 consultas; `src/run.py` aplica tudo e grava `report/resultados.json`; `src/relatorio.py` gera `.docx` e converte p/ PDF via Word.
**Tech Stack:** Python 3.14, neo4j driver, python-docx, docx2pdf (Word instalado), Aura.
**Spec:** docs/superpowers/specs/2026-11-19-credpay-neo4j-design.md

## Global Constraints
- Conexão: `neo4j://` host do `.env` com `encrypted=True, trusted_certificates=TrustCustomCAs(certifi.where())`; database = `NEO4J_DATABASE`.
- Nunca commitar `.env` nem `DECISOES.md`; nunca imprimir senha.
- Dados do enunciado intactos; carga idempotente (`MERGE`, ou `MATCH (n) DETACH DELETE n` antes).
- Paleta exata D8D8F6 B18FCF 978897 494850 2C2C34.

## Review Focus
- Rodar a carga duas vezes não duplica nós.
- Consulta 4 (ciclo) acha o ciclo A001→A004 do enunciado.
- Consulta de "recém-criada" não marca contas antigas legítimas (dataset inclui controle negativo).
- Consulta 7 não marca cadeia lenta (controle negativo).
- Relatório sem senha/URI com credencial.

### Task 1: Conexão + schema
Files: `src/db.py`, `cypher/01_schema.cypher`. Produces `get_driver()`, `run(query, **params) -> list[dict]`. Constraints de unicidade por id em cada label. Check: `python src/db.py` imprime contagem de nós.

### Task 2: Dataset + carga
Files: `cypher/02_carga.cypher`. Enunciado intacto + sintético cobrindo os 7 padrões **e controles negativos** (cliente normal, conta antiga, transferência lenta). Check: contagens esperadas; segunda execução não muda contagens.

### Task 3: Sete consultas
Files: `cypher/03_q1..q7.cypher` (um arquivo por padrão, comentário no topo com padrão e saída esperada), `src/run.py` (aplica schema+carga, roda consultas, grava `report/resultados.json`, `assert` do esperado por consulta). Check: `python src/run.py` termina sem AssertionError.

### Task 4: Relatório
Files: `src/relatorio.py`, `report/CredPay_Neo4j.docx|pdf`. Seções: contexto, modelo (diagrama simples), justificativa (grafo vs SQL), consultas+resultados, limitações; campo Integrantes em branco. Paleta aplicada em títulos/tabelas. Check: PDF existe e abre.

### Task 5: README + auditoria + professor
README.md (como rodar, sem segredos). Auditor ponytail revisa o repo; professor avalia o PDF; ajustes; commit/push.
