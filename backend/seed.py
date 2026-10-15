"""Loads a starter career graph into Neo4j. Safe to re-run (uses MERGE)."""
from db import driver, run

ROLES = {
    "Data Scientist": {"Python": 5, "SQL": 4, "Statistics": 5, "Pandas": 4, "Machine Learning": 5, "Data Visualization": 3, "Git": 2},
    "ML Engineer": {"Python": 5, "Machine Learning": 5, "Deep Learning": 4, "PyTorch": 4, "Docker": 3, "Git": 3, "Cloud (AWS)": 3},
    "Backend Developer": {"Python": 4, "SQL": 4, "REST APIs": 5, "Git": 3, "Docker": 3, "Linux": 3},
    "Frontend Developer": {"HTML/CSS": 5, "JavaScript": 5, "React": 4, "Git": 3, "REST APIs": 3},
    "DevOps Engineer": {"Linux": 5, "Docker": 5, "Kubernetes": 4, "CI/CD": 4, "Cloud (AWS)": 4, "Git": 3},
}

# (prerequisite, skill): learn the first before the second
PREREQS = [
    ("Python", "Pandas"), ("Python", "Machine Learning"), ("Statistics", "Machine Learning"),
    ("Pandas", "Machine Learning"), ("Machine Learning", "Deep Learning"), ("Deep Learning", "PyTorch"),
    ("Python", "REST APIs"), ("HTML/CSS", "JavaScript"), ("JavaScript", "React"),
    ("Linux", "Docker"), ("Docker", "Kubernetes"), ("Git", "CI/CD"), ("Docker", "CI/CD"),
    ("Linux", "Cloud (AWS)"), ("SQL", "Data Visualization"),
]

run("CREATE CONSTRAINT skill_name IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE")
run("CREATE CONSTRAINT role_title IF NOT EXISTS FOR (r:Role) REQUIRE r.title IS UNIQUE")

for role, reqs in ROLES.items():
    for skill, level in reqs.items():
        run("MERGE (r:Role {title:$r}) MERGE (s:Skill {name:$s}) "
            "MERGE (r)-[x:REQUIRES]->(s) SET x.level=$l", r=role, s=skill, l=level)

for a, b in PREREQS:
    run("MERGE (p:Skill {name:$a}) MERGE (s:Skill {name:$b}) MERGE (p)-[:PREREQUISITE_OF]->(s)", a=a, b=b)

print("Seeded:", run("MATCH (r:Role) WITH count(r) AS roles MATCH (s:Skill) RETURN roles, count(s) AS skills")[0])
driver.close()
