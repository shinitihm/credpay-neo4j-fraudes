// Padrao 2: clientes distintos usando o mesmo IP.
// Esperado: 203.0.113.10 (C009, C010). 198.51.100.7 nao aparece: mesmo cliente (C011) em duas contas.
MATCH (c:Cliente)-[:TITULAR_DE]->(a:Conta)-[:USOU_IP]->(p:IP)
WITH p, collect(DISTINCT c.id) AS clientes, collect(DISTINCT a.id) AS contas
WHERE size(clientes) >= 2
RETURN p.id AS chave, clientes, contas
