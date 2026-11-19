import os, pathlib, certifi, neo4j

def _env():
    for l in (pathlib.Path(__file__).parent.parent / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in l and not l.startswith("#"):
            k, v = l.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

def get_driver():
    _env()
    uri = os.environ["NEO4J_URI"]
    if uri.startswith("neo4j+s://"):
        uri = "neo4j://" + uri[len("neo4j+s://"):]
    return neo4j.GraphDatabase.driver(
        uri,
        auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]),
        encrypted=True, trusted_certificates=neo4j.TrustCustomCAs(certifi.where()))

def run(d, query):
    r = d.execute_query(query, database_=os.environ["NEO4J_DATABASE"])
    return [dict(x) for x in r.records]
