// Padrao 1: varias contas (3+) de clientes distintos (2+) acessando de um mesmo dispositivo.
// Esperado: D1 (A005, A006, A007 / C005-C007). Controles: D4 (duas contas do mesmo cliente C011) e D5 (tres contas do
// mesmo cliente C040) nao aparecem; D5 isola o criterio de 2+ clientes, pois ja tem 3 contas.
MATCH (c:Cliente)-[:TITULAR_DE]->(a:Conta)-[:ACESSOU_DE]->(d:Dispositivo)
WITH d, collect(DISTINCT c.id) AS clientes, collect(DISTINCT a.id) AS contas
WHERE size(clientes) >= 2 AND size(contas) >= 3
RETURN d.id AS chave, clientes, contas
