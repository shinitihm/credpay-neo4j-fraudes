// Padrao 6: cadeia de 3 transferencias em sequencia, em ate 24h, entre pares de contas sem historico:
// para cada par consecutivo (a,b), (b,c), (c,d) nao existe transferencia anterior ao inicio da cadeia
// (t1) entre as duas contas, em qualquer direcao. A verificacao e POR PAR, nao global.
// Esperado: cadeia A019->A020->A021->A022. A cadeia do enunciado (A001..A004) nao aparece: transferencias
// espacadas por 2 dias. A cadeia A033..A036 (controle) nao aparece: A034 e A035 ja transacionaram antes.
MATCH (a:Conta)-[t1:TRANSFERIU]->(b:Conta)-[t2:TRANSFERIU]->(c:Conta)
      -[t3:TRANSFERIU]->(d:Conta)
WHERE t1.data < t2.data AND t2.data < t3.data
  AND t3.data < t1.data + duration('P1D')
  AND a <> c AND a <> d AND b <> d
  AND NOT EXISTS { MATCH (a)-[t:TRANSFERIU]-(b) WHERE t.data < t1.data }
  AND NOT EXISTS { MATCH (b)-[t:TRANSFERIU]-(c) WHERE t.data < t1.data }
  AND NOT EXISTS { MATCH (c)-[t:TRANSFERIU]-(d) WHERE t.data < t1.data }
RETURN a.id AS chave, [a.id, b.id, c.id, d.id] AS cadeia
