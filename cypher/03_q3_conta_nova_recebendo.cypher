// Padrao 3: conta criada ha menos de 30 dias (ref. fixa 2026-11-19) recebendo de 3+ origens distintas.
// Esperado: A013 (origens A005, A006, A007). A014 nao aparece: tambem recebe de 3 origens, mas e conta antiga (2024).
MATCH (o:Conta)-[:TRANSFERIU]->(a:Conta)
WHERE a.criada_em >= datetime('2026-11-19T12:00:00') - duration('P30D')
WITH a, collect(DISTINCT o.id) AS origens
WHERE size(origens) >= 3
RETURN a.id AS chave, origens
