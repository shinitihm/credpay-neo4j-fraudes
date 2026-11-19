// Padrao 4: anel de transferencias (ciclo de 3 a 5 contas) em ordem temporal crescente, sem repetir conta.
// A ordem temporal faz o anel ser reportado uma unica vez (comecando pela primeira transferencia).
// A coluna vinculos lista vinculos compartilhados entre titulares de contas diferentes do anel (Endereco, Dispositivo, IP, Cartao).
// Esperado: A001->A002->A003->A004->A001 com vinculos ['Endereco'] (C001 e C002 moram em E1): o anel e suspeito mesmo assim.
MATCH p = (a:Conta)-[:TRANSFERIU*3..5]->(a)
WITH a, relationships(p) AS rs, [n IN nodes(p)[0..-1] | n.id] AS ciclo
WHERE all(i IN range(1, size(rs) - 1) WHERE rs[i-1].data < rs[i].data)
  AND all(x IN ciclo WHERE single(y IN ciclo WHERE y = x))
OPTIONAL MATCH (x:Conta)<-[:TITULAR_DE]-(cx:Cliente)-[:MORA_EM]->(e:Endereco)<-[:MORA_EM]-(cy:Cliente)-[:TITULAR_DE]->(y:Conta)
WHERE x.id IN ciclo AND y.id IN ciclo AND cx <> cy
WITH a, ciclo, collect(DISTINCT CASE WHEN e IS NULL THEN null ELSE 'Endereco' END) AS v1
OPTIONAL MATCH (x2:Conta)-[]->(s)<-[]-(y2:Conta)
WHERE (s:Dispositivo OR s:IP OR s:Cartao) AND x2.id IN ciclo AND y2.id IN ciclo AND x2 <> y2
WITH a, ciclo, v1, collect(DISTINCT labels(s)[0]) AS v2
RETURN a.id AS chave, ciclo, v1 + v2 AS vinculos
