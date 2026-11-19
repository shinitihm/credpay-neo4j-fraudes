// Padrao 5: mesmo cartao em contas de clientes diferentes.
// Esperado: K1 (A015 e A016, C015/C016). K2 nao aparece: duas contas do mesmo cliente C017. K3 so tem um cliente.
MATCH (c:Cliente)-[:TITULAR_DE]->(a:Conta)-[:USA_CARTAO]->(k:Cartao)
WITH k, collect(DISTINCT c.id) AS clientes, collect(DISTINCT a.id) AS contas
WHERE size(clientes) >= 2
RETURN k.id AS chave, clientes, contas
