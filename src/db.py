import os, pathlib, certifi, neo4j

def _env():
    for l in (pathlib.Path(__file__).parent.parent / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in l and not l.startswith("#"):
            k, v = l.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

def get_driver():
    _env()
    return neo4j.GraphDatabase.driver(
        os.environ["NEO4J_URI"].replace("neo4j+s", "neo4j"),
        auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]),
        encrypted=True, trusted_certificates=neo4j.TrustCustomCAs(certifi.where()))

def run(d, query, **params):
    r = d.execute_query(query, params or None, database_=os.environ["NEO4J_DATABASE"])
    return [dict(x) for x in r.records]

if __name__ == "__main__":
    d = get_driver()
    print(run(d, "MATCH (n) RETURN count(n) AS nos"))
    d.close()
