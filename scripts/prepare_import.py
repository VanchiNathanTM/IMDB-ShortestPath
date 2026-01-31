import pandas as pd
import os
import shutil

# Configuration
INPUT_DIR = "data/processed"
OUTPUT_DIR = "data/import"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def prepare_movies():
    print("Preparing Movies...")
    # Read without header assumption to just skip first row easily, 
    # but pandas is better to ensure valid CSV writing if needed.
    # Actually, large files -> chunking or just skipping lines is better.
    
    # Let's just use raw file operations to strip the first line to be fast and memory efficient
    with open(os.path.join(INPUT_DIR, "clean_movies.csv"), 'r', encoding='utf-8') as f_in, \
         open(os.path.join(OUTPUT_DIR, "movies.csv"), 'w', encoding='utf-8') as f_out:
        next(f_in) # Skip header
        shutil.copyfileobj(f_in, f_out)
        
    # Write Header File
    with open(os.path.join(OUTPUT_DIR, "movies_header.csv"), 'w', encoding='utf-8') as f:
        f.write("tconst:ID(Movie),title,year:int\n")

def prepare_people():
    print("Preparing People...")
    with open(os.path.join(INPUT_DIR, "clean_people.csv"), 'r', encoding='utf-8') as f_in, \
         open(os.path.join(OUTPUT_DIR, "people.csv"), 'w', encoding='utf-8') as f_out:
        next(f_in) # Skip header
        shutil.copyfileobj(f_in, f_out)
        
    # Write Header File
    with open(os.path.join(OUTPUT_DIR, "people_header.csv"), 'w', encoding='utf-8') as f:
        f.write("nconst:ID(Person),name,born:int\n")

def prepare_roles():
    print("Preparing Roles...")
    with open(os.path.join(INPUT_DIR, "clean_roles.csv"), 'r', encoding='utf-8') as f_in, \
         open(os.path.join(OUTPUT_DIR, "roles.csv"), 'w', encoding='utf-8') as f_out:
        next(f_in) # Skip header
        shutil.copyfileobj(f_in, f_out)
        
    # Write Header File
    # CSV is tconst, nconst, category
    # We want (:Person)-[:WORKED_IN]->(:Movie)
    # So nconst is START, tconst is END
    # Header mapping: :END_ID(Movie), :START_ID(Person), category
    with open(os.path.join(OUTPUT_DIR, "roles_header.csv"), 'w', encoding='utf-8') as f:
        f.write(":END_ID(Movie),:START_ID(Person),category\n")

if __name__ == "__main__":
    prepare_movies()
    prepare_people()
    prepare_roles()
    print("Import preparation complete. Files are in 'data/import/'.")
