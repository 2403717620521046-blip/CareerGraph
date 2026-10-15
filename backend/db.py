import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, ".env"))
load_dotenv(os.path.join(HERE, "aura.env"))

URI = os.environ.get("NEO4J_URI")
USER = os.environ.get("NEO4J_USERNAME", "neo4j")
PASSWORD = os.environ.get("NEO4J_PASSWORD")
DATABASE = os.environ.get("NEO4J_DATABASE", "neo4j")

if not URI or not PASSWORD or "PASTE" in URI + PASSWORD:
    raise SystemExit("Missing NEO4J_URI / NEO4J_PASSWORD. Open backend/aura.env "
                     "and paste in the values from your Aura credentials file.")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
try:
    driver.verify_connectivity()
except Exception as e:
    raise SystemExit(f"Cannot connect to Neo4j Aura: {e}\nCheck the URI/password and that the instance is running (Aura Free pauses when idle).")


def run(cypher, **params):
    with driver.session(database=DATABASE) as session:
        return [r.data() for r in session.run(cypher, **params)]
