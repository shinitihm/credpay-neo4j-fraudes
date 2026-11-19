// Padrao 6: cadeia de 3 transferencias em sequencia, em ate 24h, entre pares que nunca se relacionaram antes (so 1 transferencia por par).
// Esperado: cadeia A019->A020->A021->A022. A cadeia do enunciado (A001..A004) nao aparece: transferencias espacadas por 2 dias.
MATCH (a:Conta)-[t1:TRANSFERIU]->(b:Conta)-[t2:TRANSFERIU]->(c:Conta)-[t3:TRANSFERIU]->(d:Conta)
WHERE t1.data < t2.data AND t2.data < t3.data AND t3.data < t1.data + duration('P1D')
  AND a <> c AND a <> d AND b <> d
  AND COUNT { (a)-[:TRANSFERIU]-(b) } = 1 AND COUNT { (b)-[:TRANSFERIU]-(c) } = 1 AND COUNT { (c)-[:TRANSFERIU]-(d) } = 1
RETURN a.id AS chave, [a.id, b.id, c.id, d.id] AS cadeia
