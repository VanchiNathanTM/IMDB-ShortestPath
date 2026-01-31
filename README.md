# Six Degrees of Movies

A "Six Degrees of Separation" application for movies and people, built with Neo4j, Python (FastAPI), and React.

Find the shortest path between any two people or movies in the IMDB database!

## Prerequisites

- **Docker Desktop** (Required) - [Download Here](https://www.docker.com/products/docker-desktop/)
- **Python 3.8+**
- **Node.js 16+**

---

## First-Time Setup

### 1. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cd ..
```

**Frontend:**
```bash
cd frontend
npm install
cd ..
```

### 2. Prepare Database (Optional - if you have raw IMDB data)

This repo does **not** include the raw IMDB datasets. If you want to import your own:

1. Download these files from [IMDB Datasets](https://datasets.imdbws.com/):
   - `title.basics.tsv.gz`
   - `name.basics.tsv.gz`
   - `title.principals.tsv.gz`

2. Place them in `data/raw/`

3. Run the processing scripts:
   ```bash
   python scripts/process_data.py
   python scripts/add_friend.py
   python scripts/add_friend_director.py
   python scripts/prepare_import.py
   ```

### 3. Import Database

Run the import script to create and populate the Neo4j database:

**Windows:**
```cmd
import.bat
```

This will:
- Stop any existing Neo4j container
- Import data into Neo4j (creates 2.27M nodes, 4.77M relationships)
- Start Neo4j and create indexes
- Takes about 30 seconds

---

## Startup

To start the application, follow these steps:

### 1. Start the Database (Neo4j)
Ensure Docker Desktop is running, then start the Neo4j container:
```bash
docker compose up -d
```
*Note: Wait about 15-30 seconds for the database to fully initialize before starting the backend.*

### 2. Start the Backend API
Open a new terminal, navigate to the backend directory, and start the FastAPI server:
```bash
cd backend
# Optional: Activate your virtual environment first
# .venv\Scripts\activate (Windows)
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Start the Frontend
Open another terminal, navigate to the frontend directory, and start the React dev server:
```bash
cd frontend
npm start
```
The app will be available at [http://localhost:3000](http://localhost:3000).

---

## Service URLs

Once running, access:

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8001
- **API Docs:** http://localhost:8001/docs
- **Neo4j Browser:** http://localhost:7474 (user: `neo4j`, password: `password`)

---

## Usage

1. Open http://localhost:3000
2. Type to search for a person or movie in the "Start" field (e.g., "Kevin Bacon")
3. Type to search in the "End" field (e.g., "Timothée Chalamet")
4. Click "Find Connection" to see the shortest path!

The app supports:
- **Person → Person** connections (shows "degrees of separation")
- **Movie → Movie** connections
- **Person → Movie** or **Movie → Person** connections

---

## Project Structure

```
.
├── backend/              # FastAPI backend
│   ├── main.py          # API endpoints
│   ├── requirements.txt # Python dependencies
│   └── tests/           # Backend tests
├── frontend/            # React frontend
│   ├── src/
│   │   └── App.tsx     # Main React component
│   └── package.json    # Node dependencies
├── scripts/             # Data processing scripts
├── data/
│   ├── raw/            # Raw IMDB downloads (gitignored)
│   ├── processed/      # Processed CSVs (gitignored)
│   └── import/         # Neo4j import format (gitignored)
├── docker-compose.yml   # Neo4j container config
├── import.bat           # Database import script
├── start.bat            # Start all services
└── stop.bat             # Stop all services
```

---

## Running Tests

**Backend tests:**
```bash
cd backend
pytest
```

**Frontend tests:**
```bash
cd frontend
npm test
```

---

## Troubleshooting

**Port conflicts:**
- Backend runs on port **8001** (changed from 8000 to avoid conflicts)
- Frontend runs on port **3000**
- Neo4j uses ports **7474** (HTTP) and **7687** (Bolt)

**Database not responding:**
- Wait 15-30 seconds after starting Docker Compose for Neo4j to initialize
- Check logs: `docker logs imdb_neo4j`

**Frontend autocomplete not working:**
- Ensure backend is running on port 8001
- Check browser console for CORS errors
- Verify Neo4j is running: `docker ps | grep neo4j`

---

## Notes

- All data files (`data/raw/`, `data/processed/`, `data/import/`) are gitignored
- Neo4j data is stored in Docker volumes (`imdb_neo4j_data`, `imdb_neo4j_logs`)
- Run processing scripts from project root so paths resolve correctly
