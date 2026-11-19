// Padrao 6: cadeia de 3 transferencias em sequencia, em ate 24h, entre contas sem nenhuma transferencia anterior ao inicio da cadeia.
// Esperado: cadeia A019->A020->A021->A022. A cadeia do enunciado (A001..A004) nao aparece: transferencias espacadas por 2 dias.
MATCH (a:Conta)-[t1:TRANSFERIU]->(b:Conta)-[t2:TRANSFERIU]->(c:Conta)-[t3:TRANSFERIU]->(d:Conta)
WHERE t1.data < t2.data AND t2.data < t3.data AND t3.data < t1.data + duration('P1D')
  AND a <> c AND a <> d AND b <> d
  AND NOT EXISTS { MATCH (x)-[t:TRANSFERIU]-() WHERE x IN [a, b, c, d] AND t.data < t1.data }
RETURN a.id AS chave, [a.id, b.id, c.id, d.id] AS cadeia
