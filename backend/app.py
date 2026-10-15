import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from db import run

FRONT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app = Flask(__name__, static_folder=FRONT, static_url_path="/static")
CORS(app)


@app.get("/")
def index():
    return send_from_directory(FRONT, "index.html")


@app.get("/api/skills")
def skills():
    return jsonify(run("MATCH (s:Skill) RETURN s.name AS name ORDER BY name"))


@app.get("/api/roles")
def roles():
    return jsonify(run("MATCH (r:Role) RETURN r.title AS title ORDER BY title"))


@app.post("/api/analyze")
def analyze():
    """Skill-gap analysis for one target role + ordered learning path."""
    data = request.get_json(force=True)
    have, role = set(data.get("skills", [])), data.get("role")
    rows = run("MATCH (:Role {title:$r})-[x:REQUIRES]->(s:Skill) RETURN s.name AS skill, x.level AS level", r=role)
    if not rows:
        return jsonify(error="Unknown role"), 404

    total = sum(r["level"] for r in rows)
    got = sum(r["level"] for r in rows if r["skill"] in have)
    missing = sorted((r for r in rows if r["skill"] not in have), key=lambda r: -r["level"])

    prereq = {r["skill"]: r["pre"] for r in run(
        "MATCH (s:Skill) OPTIONAL MATCH (p:Skill)-[:PREREQUISITE_OF]->(s) "
        "RETURN s.name AS skill, collect(p.name) AS pre")}
    needed = {r["skill"] for r in rows}
    path, seen = [], set()

    def visit(skill):  # prerequisites first (depth-first)
        if skill in seen or skill in have:
            return
        seen.add(skill)
        for p in prereq.get(skill, []):
            visit(p)
        path.append({"skill": skill, "foundation": skill not in needed})

    for m in missing:
        visit(m["skill"])

    return jsonify(role=role, score=round(got * 100 / total),
                   have=[r["skill"] for r in rows if r["skill"] in have],
                   missing=missing, path=path)


@app.post("/api/recommend")
def recommend():
    """Rank every role by weighted skill match."""
    have = request.get_json(force=True).get("skills", [])
    rows = run(
        "MATCH (r:Role)-[x:REQUIRES]->(s:Skill) "
        "WITH r, sum(x.level) AS total, "
        "sum(CASE WHEN s.name IN $have THEN x.level ELSE 0 END) AS got, "
        "collect(CASE WHEN NOT s.name IN $have THEN s.name END) AS missing "
        "RETURN r.title AS role, toInteger(round(got*100.0/total)) AS score, missing "
        "ORDER BY score DESC", have=have)
    return jsonify(rows)


@app.get("/api/graph/<role>")
def graph(role):
    rows = run("MATCH (:Role {title:$r})-[x:REQUIRES]->(s:Skill) RETURN s.name AS skill, x.level AS level", r=role)
    names = [r["skill"] for r in rows]
    pre = run("MATCH (p:Skill)-[:PREREQUISITE_OF]->(s:Skill) WHERE s.name IN $n AND p.name IN $n "
              "RETURN p.name AS a, s.name AS b", n=names)
    nodes = [{"id": role, "label": role, "group": "role"}] + \
            [{"id": n, "label": n, "group": "skill"} for n in names]
    edges = [{"from": role, "to": r["skill"], "label": str(r["level"]), "arrows": "to"} for r in rows] + \
            [{"from": e["a"], "to": e["b"], "arrows": "to", "dashes": True} for e in pre]
    return jsonify(nodes=nodes, edges=edges)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
