from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from typing import List, Optional, Literal, Tuple
from pydantic import BaseModel

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

app = FastAPI(title="Six Degrees of Movies")

# CORS middleware to allow frontend to call backend
# We allow localhost:3000 by default, but also allow flexibility if needed
app.add_middleware(
    CORSMiddleware,
    # NOTE: Using allow_origins=["*"] with allow_credentials=True breaks CORS in browsers.
    # Allow any localhost/127.0.0.1 port (start.bat may choose a non-3000 port).
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Neo4j Connection
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password"))

def get_db():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    return driver

class SearchResult(BaseModel):
    id: str
    type: Literal["person", "movie"]
    name: str
    born: Optional[int] = None
    year: Optional[int] = None

class PathNode(BaseModel):
    type: str # 'person' or 'movie'
    name: str # name or title
    id: str

class PathResponse(BaseModel):
    path_found: bool
    degrees: Optional[int]
    hops: int
    steps: List[PathNode]


def _parse_node_ref(value: str) -> Tuple[str, str]:
    """Parse a node reference from query params.

    Accepted forms:
    - "person:nm0000001" / "movie:tt0000001"
    - Bare IMDB IDs: "nm..." (person), "tt..." (movie)
    """

    if ":" in value:
        node_type, node_id = value.split(":", 1)
        if node_type not in {"person", "movie"}:
            raise HTTPException(status_code=400, detail=f"Invalid node type: {node_type}")
        if not node_id:
            raise HTTPException(status_code=400, detail="Missing node id")
        return node_type, node_id

    if value.startswith("nm"):
        return "person", value
    if value.startswith("tt"):
        return "movie", value

    raise HTTPException(
        status_code=400,
        detail="Invalid node reference. Use 'person:nm...' / 'movie:tt...' or a bare 'nm...' / 'tt...' id.",
    )

@app.get("/search", response_model=List[SearchResult])
def search(q: str = Query(..., min_length=2)):
    driver = get_db()
    query = """
    CALL {
      MATCH (p:Person)
      WHERE toLower(p.name) STARTS WITH toLower($q)
      RETURN 'person' AS type, p.nconst AS id, p.name AS name, p.born AS born, null AS year, 0 AS rank
      UNION
      MATCH (m:Movie)
      WHERE toLower(m.title) STARTS WITH toLower($q)
      RETURN 'movie' AS type, m.tconst AS id, m.title AS name, null AS born, m.year AS year, 0 AS rank
      UNION
      MATCH (p:Person)
      WHERE toLower(p.name) CONTAINS toLower($q)
        AND NOT toLower(p.name) STARTS WITH toLower($q)
      RETURN 'person' AS type, p.nconst AS id, p.name AS name, p.born AS born, null AS year, 1 AS rank
      UNION
      MATCH (m:Movie)
      WHERE toLower(m.title) CONTAINS toLower($q)
        AND NOT toLower(m.title) STARTS WITH toLower($q)
      RETURN 'movie' AS type, m.tconst AS id, m.title AS name, null AS born, m.year AS year, 1 AS rank
    }
    RETURN type, id, name, born, year
    ORDER BY rank, name
    LIMIT 20
    """
    with driver.session() as session:
        result = session.run(query, q=q)
        items = [
            SearchResult(
                id=record["id"],
                type=record["type"],
                name=record["name"],
                born=record["born"],
                year=record["year"],
            )
            for record in result
        ]
    driver.close()
    return items

@app.get("/path", response_model=PathResponse)
def shortest_path(
    start: Optional[str] = None,
    end: Optional[str] = None,
    start_id: Optional[str] = None,
    end_id: Optional[str] = None,
):
    if start is None and start_id is not None:
        start = start_id
    if end is None and end_id is not None:
        end = end_id
    if start is None or end is None:
        raise HTTPException(status_code=422, detail="Missing required query params: start and end")

    start_type, start_node_id = _parse_node_ref(start)
    end_type, end_node_id = _parse_node_ref(end)

    driver = get_db()
    query = """
    MATCH (start)
    WHERE (start:Person AND start.nconst = $start_id) OR (start:Movie AND start.tconst = $start_id)
    MATCH (end)
    WHERE (end:Person AND end.nconst = $end_id) OR (end:Movie AND end.tconst = $end_id)
    MATCH path = shortestPath((start)-[:WORKED_IN*]-(end))
    RETURN path
    """
    
    with driver.session() as session:
        result = session.run(query, start_id=start_node_id, end_id=end_node_id)
        record = result.single()
        
        if not record:
            driver.close()
            return PathResponse(path_found=False, degrees=None, hops=0, steps=[])
            
        path = record["path"]
        steps = []
        
        for node in path.nodes:
            if "Person" in node.labels:
                steps.append(PathNode(type="person", name=node["name"], id=node["nconst"]))
            elif "Movie" in node.labels:
                steps.append(PathNode(type="movie", name=node["title"], id=node["tconst"]))

        # Prefer actual relationships length when available (neo4j driver Path).
        hops = len(getattr(path, "relationships", [])) or max(0, len(steps) - 1)

        # Preserve “Kevin Bacon number” semantics for person->person searches.
        degrees: Optional[int]
        if start_type == "person" and end_type == "person":
            degrees = hops // 2
        else:
            degrees = None
        
    driver.close()
    return PathResponse(path_found=True, degrees=degrees, hops=hops, steps=steps)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
