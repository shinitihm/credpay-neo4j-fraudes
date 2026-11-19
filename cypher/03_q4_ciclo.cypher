// Padrao 4: anel de transferencias (ciclo de 3 a 5 contas) em ordem temporal crescente, sem repetir conta.
// A ordem temporal e regra de negocio (segue o fluxo do dinheiro: cada repasse ocorre depois de receber)
// e tambem faz o anel ser reportado uma unica vez (comecando pela primeira transferencia), sem rotacoes.
// A coluna vinculos lista vinculos compartilhados entre titulares de contas diferentes do anel
// (Endereco, Dispositivo, IP, Cartao). Anel SEM vinculos (vinculos = []) e o mais proximo de
// "grupos aparentemente sem relacao". Anel com vinculo (ex.: C001 e C002 em E1) pode ser grupo
// coordenado OU familia: ambos merecem revisao humana.
// Esperado: A037 (vinculos []) e A001 (A001->A002->A003->A004->A001, vinculos ['Endereco']).
MATCH p = (a:Conta)-[:TRANSFERIU*3..5]->(a)
WITH a, relationships(p) AS rs, [n IN nodes(p)[0..-1] | n.id] AS ciclo
WHERE all(i IN range(1, size(rs) - 1) WHERE rs[i-1].data < rs[i].data)
  AND all(x IN ciclo WHERE single(y IN ciclo WHERE y = x))
OPTIONAL MATCH (x:Conta)<-[:TITULAR_DE]-(cx:Cliente)-[:MORA_EM]->(e:Endereco),
      (e)<-[:MORA_EM]-(cy:Cliente)-[:TITULAR_DE]->(y:Conta)
WHERE x.id IN ciclo AND y.id IN ciclo AND cx <> cy
WITH a, ciclo,
     collect(DISTINCT CASE WHEN e IS NULL THEN null ELSE 'Endereco' END) AS v1
OPTIONAL MATCH (x2:Conta)-[]->(s)<-[]-(y2:Conta)
WHERE (s:Dispositivo OR s:IP OR s:Cartao)
  AND x2.id IN ciclo AND y2.id IN ciclo AND x2 <> y2
WITH a, ciclo, v1, collect(DISTINCT labels(s)[0]) AS v2
WITH a, ciclo, v1 + v2 AS vinculos
RETURN a.id AS chave, ciclo, vinculos
ORDER BY size(vinculos), chave
