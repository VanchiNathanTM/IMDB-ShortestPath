#!/bin/bash

# Six Degrees of Movies - Import Script for macOS/Linux
echo "Stopping existing Neo4j container..."
docker compose down -v

echo "Running Neo4j Import..."
docker run --rm \
    --volume="$(pwd)/data/import:/import" \
    --volume="imdb_neo4j_data:/data" \
    neo4j:5.16.0-community \
    neo4j-admin database import full \
    --nodes=Movie="/import/movies_header.csv,/import/movies.csv" \
    --nodes=Person="/import/people_header.csv,/import/people.csv" \
    --relationships=WORKED_IN="/import/roles_header.csv,/import/roles.csv" \
    --overwrite-destination=true \
    --verbose

echo "Starting Neo4j Service..."
docker compose up -d

echo "Waiting for Neo4j to start..."
sleep 30

echo "Creating Indexes..."
docker exec imdb_neo4j cypher-shell -u neo4j -p password "CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.name);"
docker exec imdb_neo4j cypher-shell -u neo4j -p password "CREATE INDEX movie_title IF NOT EXISTS FOR (m:Movie) ON (m.title);"

echo "Done! Access at http://localhost:7474"
