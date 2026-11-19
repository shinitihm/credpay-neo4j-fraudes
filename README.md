# CredPay Neo4j: detecção de fraudes em grafo

Protótipo acadêmico (Banco de Dados) que modela clientes, contas, cartões, dispositivos, IPs e endereços da fintech fictícia CredPay Digital em um grafo Neo4j e usa consultas Cypher para achar sete padrões de fraude. Os dados são sintéticos.

## Estrutura

- `cypher/`: `01_schema` (constraints), `02_carga` (dados) e `03_q*` (as sete consultas).
- `src/run.py`: carrega o grafo, roda as consultas, confere os resultados esperados (asserts) e grava `report/resultados.json`.
- `src/relatorio.py`: gera `report/CredPay_Neo4j.docx` e `.pdf` a partir do JSON e dos `.cypher` (não acessa o banco).
- `src/db.py`: conexão com o Neo4j.

## Como rodar

```
python -m venv .venv
.venv\Scripts\activate        # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

Crie um `.env` na raiz (use os dados da sua instância Aura, sem versionar):

```
NEO4J_URI=...
NEO4J_USERNAME=...
NEO4J_PASSWORD=...
NEO4J_DATABASE=...
```

```
python src/run.py        # carga + consultas + asserts
python src/relatorio.py  # relatório (o PDF usa o Word, via docx2pdf)
```

**Atenção:** `python src/run.py` apaga TODO o banco da instância antes de recarregar. Use só uma instância de demonstração.

**Certificado:** `src/db.py` troca `neo4j+s` por `neo4j` com `encrypted=True` e `TrustCustomCAs(certifi.where())`, contornando erros de certificado em redes que interceptam TLS.

## Padrões e consultas

| # | Padrão | Arquivo |
|---|--------|---------|
| 1 | Dispositivo compartilhado (3+ contas, 2+ clientes) | `03_q1_dispositivo_compartilhado.cypher` |
| 2 | IP compartilhado | `03_q2_ip_compartilhado.cypher` |
| 3 | Conta nova recebendo de 3+ origens | `03_q3_conta_nova_recebendo.cypher` |
| 4 | Anel de transferências (ciclo) | `03_q4_ciclo.cypher` |
| 5 | Cartão compartilhado entre clientes | `03_q5_cartao_compartilhado.cypher` |
| 6 | Cadeia entre contas sem histórico | `03_q6_cadeia_sem_historico.cypher` |
| 7 | Passagem rápida (recebe e repassa em minutos) | `03_q7_passagem_rapida.cypher` |
