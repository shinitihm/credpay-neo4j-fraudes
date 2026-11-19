// Carga idempotente: apaga tudo e recarrega. C001-C004, A001-A004, T001-T004 sao do enunciado, o resto e sintetico.
MATCH (n) DETACH DELETE n;
UNWIND [i IN range(1,32) WHERE NOT i IN [12,18]] AS i
CREATE (:Cliente {id:'C'+right('000'+toString(i),3),
  nome: CASE i WHEN 1 THEN 'Ana' WHEN 2 THEN 'Bruno' WHEN 3 THEN 'Carlos' WHEN 4 THEN 'Daniela' ELSE 'Cliente '+toString(i) END,
  cpf:'***.***.***-**'});
// A012 e A018 pertencem aos clientes C011 e C017 (duas contas do mesmo cliente: controles negativos).
UNWIND range(1,32) AS i
WITH i, CASE i WHEN 12 THEN 11 WHEN 18 THEN 17 ELSE i END AS cli
MATCH (c:Cliente {id: 'C'+right('000'+toString(cli),3)})
CREATE (c)-[:TITULAR_DE]->(:Conta {id:'A'+right('000'+toString(i),3), tipo:'Corrente',
  criada_em: CASE WHEN i=13 THEN datetime('2026-11-15T00:00:00') WHEN i<=4 THEN datetime('2023-01-01T00:00:00') ELSE datetime('2024-06-01T00:00:00') END});
UNWIND [
 ['T001','A001','A002',500,'2026-11-01T10:00:00'],['T002','A002','A003',450,'2026-11-03T10:00:00'],
 ['T003','A003','A004',400,'2026-11-05T10:00:00'],['T004','A004','A001',350,'2026-11-07T10:00:00'],
 ['T005','A005','A013',200,'2026-11-16T10:00:00'],['T006','A006','A013',250,'2026-11-16T11:00:00'],['T007','A007','A013',300,'2026-11-17T09:00:00'],
 ['T008','A008','A014',150,'2026-11-10T09:00:00'],['T009','A009','A014',160,'2026-11-11T09:00:00'],['T010','A010','A014',170,'2026-11-12T09:00:00'],
 ['T011','A019','A020',900,'2026-11-17T09:00:00'],['T012','A020','A021',880,'2026-11-17T14:00:00'],['T013','A021','A022',860,'2026-11-17T20:00:00'],
 ['T014','A028','A027',1000,'2026-11-18T10:00:00'],['T015','A027','A029',980,'2026-11-18T10:04:00'],
 ['T016','A031','A030',500,'2026-11-18T10:00:00'],['T017','A030','A032',480,'2026-11-18T12:00:00']] AS t
MATCH (o:Conta {id:t[1]}), (d:Conta {id:t[2]})
CREATE (o)-[:TRANSFERIU {id:t[0], valor:t[3], data:datetime(t[4])}]->(d);
UNWIND [['D1',['A005','A006','A007']],['D2',['A001']],['D3',['A008']],['D4',['A011','A012']]] AS x
CREATE (d:Dispositivo {id:x[0]}) WITH d, x UNWIND x[1] AS a MATCH (c:Conta {id:a}) CREATE (c)-[:ACESSOU_DE]->(d);
UNWIND [['203.0.113.10',['A009','A010']],['198.51.100.7',['A011','A012']],['192.0.2.1',['A001']]] AS x
CREATE (p:IP {id:x[0]}) WITH p, x UNWIND x[1] AS a MATCH (c:Conta {id:a}) CREATE (c)-[:USOU_IP]->(p);
UNWIND [['K1',['A015','A016']],['K2',['A017','A018']],['K3',['A001']]] AS x
CREATE (k:Cartao {id:x[0]}) WITH k, x UNWIND x[1] AS a MATCH (c:Conta {id:a}) CREATE (c)-[:USA_CARTAO]->(k);
UNWIND [['E1',['C001','C002']],['E2',['C003']],['E3',['C004']]] AS x
CREATE (e:Endereco {id:x[0]}) WITH e, x UNWIND x[1] AS cid MATCH (c:Cliente {id:cid}) CREATE (c)-[:MORA_EM]->(e);
