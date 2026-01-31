import pandas as pd
import os

# Configuration
OUTPUT_DIR = "data/processed"
CLEAN_MOVIES_CSV = os.path.join(OUTPUT_DIR, "clean_movies.csv")
CLEAN_ROLES_CSV = os.path.join(OUTPUT_DIR, "clean_roles.csv")

# Sydney's Director Credit (Short Film "Traffic")
TRAFFIC_ID = "tt37388558"
TRAFFIC_TITLE = "Traffic"
TRAFFIC_YEAR = "2025"

SYDNEY_ID = "nm12228615"

def add_director_credit():
    print(f"Adding Director credit for {SYDNEY_ID} (Movie: {TRAFFIC_TITLE})...")
    
    # 1. Add the Movie (Shorts were originally filtered out, but user wants her Director credit)
    movies_df = pd.read_csv(CLEAN_MOVIES_CSV, dtype=str)
    if TRAFFIC_ID not in movies_df['tconst'].values:
        new_movie = pd.DataFrame([{
            "tconst": TRAFFIC_ID,
            "primaryTitle": TRAFFIC_TITLE,
            "startYear": TRAFFIC_YEAR
        }])
        new_movie.to_csv(CLEAN_MOVIES_CSV, mode='a', header=False, index=False)
        print(f"Added movie '{TRAFFIC_TITLE}' to {CLEAN_MOVIES_CSV}")
    else:
        print(f"Movie '{TRAFFIC_TITLE}' already in database.")

    # 2. Add the Director Role
    roles_df = pd.read_csv(CLEAN_ROLES_CSV, dtype=str)
    exists = ((roles_df['tconst'] == TRAFFIC_ID) & 
              (roles_df['nconst'] == SYDNEY_ID) & 
              (roles_df['category'] == 'director')).any()
    
    if not exists:
        new_role = pd.DataFrame([{
            "tconst": TRAFFIC_ID,
            "nconst": SYDNEY_ID,
            "category": "director"
        }])
        new_role.to_csv(CLEAN_ROLES_CSV, mode='a', header=False, index=False)
        print(f"Added Director role for {SYDNEY_ID} to {CLEAN_ROLES_CSV}")
    else:
        print("Director role already exists.")

if __name__ == "__main__":
    add_director_credit()
