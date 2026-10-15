# CareerGraph: Intelligent Career & Skill Gap Engine

Graph-based skill-gap analysis. Roles and skills live in Neo4j Aura (cloud); a Flask API scores your skills against roles and builds a prerequisite-ordered learning path; a plain HTML page shows the results.

## 1. Create the Aura database
1. Sign in at https://console.neo4j.io and create a free AuraDB instance.
2. Download the credentials `.txt` file when shown (the password appears only once).
3. Wait until the instance status is **Running**.

## 2. Configure
Open `backend/aura.env` in any text editor and paste `NEO4J_URI` (starts with `neo4j+s://`), `NEO4J_USERNAME`, `NEO4J_PASSWORD` and `NEO4J_DATABASE` from the credentials file.

## 3. Run
```
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py                  # loads starter data into Aura
python app.py
```
Open http://127.0.0.1:5000

Never commit `.env` (it is already in `.gitignore`).

## Graph model
`(:Role)-[:REQUIRES {level 1-5}]->(:Skill)` and `(:Skill)-[:PREREQUISITE_OF]->(:Skill)`

## API
- GET `/api/skills`, GET `/api/roles`
- POST `/api/analyze` `{skills:[], role}`: score, gaps, learning path
- POST `/api/recommend` `{skills:[]}`: roles ranked by match
- GET `/api/graph/<role>`: nodes and edges for the visual

## Extend
Edit `ROLES` and `PREREQS` in `backend/seed.py`, then re-run it.
