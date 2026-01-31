import pandas as pd
import os
from tqdm import tqdm

# Configuration
RAW_DIR = "data/raw"
OUTPUT_DIR = "data/processed"
CHUNK_SIZE = 100000

# Input files
MOVIES_FILE = os.path.join(RAW_DIR, "title.basics.tsv.gz")
NAMES_FILE = os.path.join(RAW_DIR, "name.basics.tsv.gz")
PRINCIPALS_FILE = os.path.join(RAW_DIR, "title.principals.tsv.gz")

# Output files
CLEAN_MOVIES_CSV = os.path.join(OUTPUT_DIR, "clean_movies.csv")
CLEAN_PEOPLE_CSV = os.path.join(OUTPUT_DIR, "clean_people.csv")
CLEAN_ROLES_CSV = os.path.join(OUTPUT_DIR, "clean_roles.csv")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_movies():
    print("Processing Movies...")
    valid_tconsts = set()
    
    # We write header first, then append mode for chunks
    first_chunk = True
    
    # title.basics columns: tconst, titleType, primaryTitle, originalTitle, isAdult, startYear, endYear, runtimeMinutes, genres
    usecols = ['tconst', 'titleType', 'primaryTitle', 'startYear']
    
    with tqdm(desc="Movies") as pbar:
        for chunk in pd.read_csv(MOVIES_FILE, sep='\t', compression='gzip', chunksize=CHUNK_SIZE, usecols=usecols, dtype=str):
            # Filter for movies only
            filtered = chunk[chunk['titleType'] == 'movie'].copy()
            
            # Handle \N in startYear (pandas might read as string "\N")
            filtered['startYear'] = filtered['startYear'].replace('\\N', '')
            
            # Keep only needed columns
            final_df = filtered[['tconst', 'primaryTitle', 'startYear']]
            
            # Save valid IDs for next steps
            valid_tconsts.update(final_df['tconst'].tolist())
            
            # Write to CSV
            mode = 'w' if first_chunk else 'a'
            header = first_chunk
            final_df.to_csv(CLEAN_MOVIES_CSV, index=False, mode=mode, header=header)
            
            first_chunk = False
            pbar.update(len(chunk))
            
    print(f"Total Movies: {len(valid_tconsts)}")
    return valid_tconsts

def process_principals(valid_tconsts):
    print("\nProcessing Principals (Roles)...")
    valid_nconsts = set()
    
    first_chunk = True
    
    # title.principals columns: tconst, ordering, nconst, category, job, characters
    usecols = ['tconst', 'nconst', 'category']
    target_categories = {'actor', 'actress', 'director'}
    
    with tqdm(desc="Principals") as pbar:
        for chunk in pd.read_csv(PRINCIPALS_FILE, sep='\t', compression='gzip', chunksize=CHUNK_SIZE, usecols=usecols, dtype=str):
            # Filter by valid movies
            filtered = chunk[chunk['tconst'].isin(valid_tconsts)].copy()
            
            # Filter by category
            filtered = filtered[filtered['category'].isin(target_categories)]
            
            # Keep needed columns
            final_df = filtered[['tconst', 'nconst', 'category']]
            
            # Save valid person IDs
            valid_nconsts.update(final_df['nconst'].tolist())
            
            # Write
            mode = 'w' if first_chunk else 'a'
            header = first_chunk
            final_df.to_csv(CLEAN_ROLES_CSV, index=False, mode=mode, header=header)
            
            first_chunk = False
            pbar.update(len(chunk))
            
    print(f"Total Relationships: {len(valid_nconsts)} unique people linked to movies")
    return valid_nconsts

def process_names(valid_nconsts):
    print("\nProcessing Names (People)...")
    found_nconsts = set()
    first_chunk = True
    
    # name.basics columns: nconst, primaryName, birthYear, deathYear, primaryProfession, knownForTitles
    usecols = ['nconst', 'primaryName', 'birthYear']
    
    with tqdm(desc="Names") as pbar:
        for chunk in pd.read_csv(NAMES_FILE, sep='\t', compression='gzip', chunksize=CHUNK_SIZE, usecols=usecols, dtype=str):
            # Filter by valid people found in principals
            filtered = chunk[chunk['nconst'].isin(valid_nconsts)].copy()
            
            # Handle \N
            filtered['birthYear'] = filtered['birthYear'].replace('\\N', '')
            
            final_df = filtered[['nconst', 'primaryName', 'birthYear']]
            
            # Track who we actually found
            found_nconsts.update(final_df['nconst'].tolist())
            
            # Write
            mode = 'w' if first_chunk else 'a'
            header = first_chunk
            final_df.to_csv(CLEAN_PEOPLE_CSV, index=False, mode=mode, header=header)
            
            first_chunk = False
            pbar.update(len(chunk))
    
    print(f"Total People: {len(found_nconsts)}")
    return found_nconsts

def finalize_roles(found_nconsts):
    print("\nFinalizing Roles (Referential Integrity Check)...")
    temp_roles = os.path.join(OUTPUT_DIR, "temp_roles.csv")
    first_chunk = True
    
    with tqdm(desc="Finalizing Roles") as pbar:
        # Read the roles we just wrote
        for chunk in pd.read_csv(CLEAN_ROLES_CSV, chunksize=CHUNK_SIZE, dtype=str):
            # Keep only roles where the person exists in our people file
            filtered = chunk[chunk['nconst'].isin(found_nconsts)]
            
            mode = 'w' if first_chunk else 'a'
            header = first_chunk
            filtered.to_csv(temp_roles, index=False, mode=mode, header=header)
            
            first_chunk = False
            pbar.update(len(chunk))
            
    # Replace the old roles file with the filtered one
    os.replace(temp_roles, CLEAN_ROLES_CSV)
    print("Roles finalized.")

if __name__ == "__main__":
    valid_movie_ids = process_movies()
    valid_person_ids = process_principals(valid_movie_ids)
    found_person_ids = process_names(valid_person_ids)
    finalize_roles(found_person_ids)
    print("\nProcessing Complete! Check 'data/processed' folder.")
