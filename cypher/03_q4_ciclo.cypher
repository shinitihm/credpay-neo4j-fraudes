// Padrao 4: anel de transferencias (ciclo de 3 a 5 contas que volta ao ponto de partida).
// Esperado: ciclo do enunciado A001->A002->A003->A004->A001 (reportado uma vez, comecando pelo menor id).
MATCH p = (a:Conta)-[:TRANSFERIU*3..5]->(a)
WITH a, [n IN nodes(p)[0..-1] | n.id] AS ciclo
WHERE a.id = reduce(m = ciclo[0], x IN ciclo | CASE WHEN x < m THEN x ELSE m END)
RETURN a.id AS chave, ciclo
