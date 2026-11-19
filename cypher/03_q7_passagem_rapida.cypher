// Padrao 7: conta que recebe e repassa em ate 10 minutos (valor repassado entre 80% e 100% do recebido).
// Esperado: A027 (recebe de A028 as 10:00, repassa a A029 as 10:04). A030 nao aparece: repassa 2h depois (controle lento).
MATCH (x:Conta)-[t1:TRANSFERIU]->(m:Conta)-[t2:TRANSFERIU]->(y:Conta)
WHERE x <> y AND t2.data > t1.data
  AND t2.data <= t1.data + duration('PT10M')
  AND t2.valor <= t1.valor AND t2.valor >= 0.8 * t1.valor
RETURN m.id AS chave, x.id AS origem, y.id AS destino
