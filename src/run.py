import json, pathlib
from db import get_driver, run

ROOT = pathlib.Path(__file__).parent.parent
ESPERADO = {  # chave esperada por consulta (controles negativos ficam de fora)
    "q1_dispositivo_compartilhado": ["D1"],
    "q2_ip_compartilhado": ["203.0.113.10"],
    "q3_conta_nova_recebendo": ["A013"],
    "q4_ciclo": ["A001", "A037"],
    "q5_cartao_compartilhado": ["K1"],
    "q6_cadeia_sem_historico": ["A019"],
    "q7_passagem_rapida": ["A027"],
}

d = get_driver()
for f in ["01_schema", "02_carga"]:
    for stmt in (ROOT / "cypher" / f"{f}.cypher").read_text(encoding="utf-8").split(";"):
        if stmt.strip():
            run(d, stmt)

contagem = {
    "nos": {r["l"]: r["n"] for r in run(d, "MATCH (n) RETURN labels(n)[0] AS l, count(*) AS n ORDER BY l")},
    "arestas": {r["t"]: r["n"] for r in run(d, "MATCH ()-[r]->() RETURN type(r) AS t, count(*) AS n ORDER BY t")},
}
print(contagem)

resultados = {}
for nome, esp in ESPERADO.items():
    linhas = run(d, (ROOT / "cypher" / f"03_{nome}.cypher").read_text(encoding="utf-8"))
    resultados[nome] = linhas
    print(nome, linhas)
    if sorted(l["chave"] for l in linhas) != esp:
        raise AssertionError(f"{nome}: esperado {esp}, obtido {linhas}")
    if nome == "q4_ciclo":
        vinc = {l["chave"]: l["vinculos"] for l in linhas}
        if vinc != {"A001": ["Endereco"], "A037": []} or linhas[0]["chave"] != "A037":
            raise AssertionError(f"{nome}: vinculos inesperados: {linhas}")
d.close()

(ROOT / "report").mkdir(exist_ok=True)
(ROOT / "report" / "resultados.json").write_text(
    json.dumps({"contagem": contagem, "consultas": resultados}, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
print("OK")
