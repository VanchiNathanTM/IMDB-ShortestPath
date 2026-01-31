import pandas as pd
import os

# Configuration
OUTPUT_DIR = "data/processed"
CLEAN_PEOPLE_CSV = os.path.join(OUTPUT_DIR, "clean_people.csv")
CLEAN_ROLES_CSV = os.path.join(OUTPUT_DIR, "clean_roles.csv")

# Sydney Balangue Data
SYDNEY_ID = "nm12228615"
SYDNEY_NAME = "Sydney Balangue"
SYDNEY_BIRTH = "" # \N in source

# Her credits (Movies already in our DB)
# Venom: The Last Dance (tt16366836) - Production Secretary
# F1: The Movie (tt16311594) - Production Assistant
# Traffic (tt37388558) is a SHORT, so it's not in clean_movies.csv. We skip it to maintain "Movies only" rule unless requested.

NEW_ROLES = [
    {"tconst": "tt16366836", "nconst": SYDNEY_ID, "category": "production_secretary"},
    {"tconst": "tt16311594", "nconst": SYDNEY_ID, "category": "production_assistant"}
]

def add_sydney():
    print(f"Adding {SYDNEY_NAME} ({SYDNEY_ID}) to dataset...")
    
    # 1. Add to People CSV
    # Check if she's already there (unlikely given previous grep)
    people_df = pd.read_csv(CLEAN_PEOPLE_CSV, dtype=str)
    if SYDNEY_ID not in people_df['nconst'].values:
        new_person = pd.DataFrame([{
            "nconst": SYDNEY_ID,
            "primaryName": SYDNEY_NAME,
            "birthYear": SYDNEY_BIRTH
        }])
        # Append and save
        new_person.to_csv(CLEAN_PEOPLE_CSV, mode='a', header=False, index=False)
        print(f"Added {SYDNEY_NAME} to {CLEAN_PEOPLE_CSV}")
    else:
        print(f"{SYDNEY_NAME} already in people database.")

    # 2. Add Roles to Roles CSV
    roles_df = pd.read_csv(CLEAN_ROLES_CSV, dtype=str)
    
    new_roles_list = []
    for role in NEW_ROLES:
        # Check for duplicates
        exists = ((roles_df['tconst'] == role['tconst']) & 
                  (roles_df['nconst'] == role['nconst']) & 
                  (roles_df['category'] == role['category'])).any()
        
        if not exists:
            new_roles_list.append(role)
    
    if new_roles_list:
        new_roles_df = pd.DataFrame(new_roles_list)
        new_roles_df.to_csv(CLEAN_ROLES_CSV, mode='a', header=False, index=False)
        print(f"Added {len(new_roles_list)} roles for {SYDNEY_NAME} to {CLEAN_ROLES_CSV}")
    else:
        print("Roles already exist.")

if __name__ == "__main__":
    add_sydney()
