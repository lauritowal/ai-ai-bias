from pathlib import Path
import json
import csv
import re
import random
import shutil

def clean_text(text):
    if not text or text.isspace():
        return None
    return re.sub(r'\s+', ' ', text.strip())

def process_csv_row(row):
    # Extract and clean the required fields
    title = clean_text(row['Project Title'])
    abstract = clean_text(row['Abstract'])

    # Skip if abstract is empty/None or just "-"
    if not abstract or abstract == "-":
        return None, None

    # Construct JSON object
    json_data = {
        "item_type": "proposal",
        "title": title, 
        "abstract": abstract,
        "origin": "Human"
    }
    
    return title, json_data

def count_files(directory):
    return len(list(Path(directory).glob('*.json')))

def process_csv(csv_path, dest_directory, num_proposals):
    print(f"Starting process_csv with path: {csv_path}")
    
    if not Path(csv_path).exists():
        print(f"Error: CSV file not found at {csv_path}")
        return
        
    dest_directory = Path(dest_directory)
    
    # Clear destination directory if it exists
    if dest_directory.exists():
        print(f"Clearing directory: {dest_directory}")
        shutil.rmtree(dest_directory)
    dest_directory.mkdir(parents=True, exist_ok=True)
    print(f"Created directory: {dest_directory}")

    # Read all rows into a list
    print("Reading CSV file...")
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    print(f"Total rows in CSV: {len(rows)}")
    
    if len(rows) == 0:
        print("No rows found in CSV!")
        return
        
    # Print first row headers to verify structure
    print("CSV headers:", list(rows[0].keys()))
    
    # Shuffle the rows
    random.shuffle(rows)
    
    # Keep track of processed proposals
    processed = 0
    skipped = 0
    row_index = 0
    
    # Process rows until we get exactly num_proposals valid ones
    while processed < num_proposals and row_index < len(rows):
        row = rows[row_index]
        row_index += 1
        
        title, json_data = process_csv_row(row)
        
        # Skip if row was invalid
        if not title or not json_data:
            skipped += 1
            continue
        
        # Generate filename from title
        max_filename_length = 250
        sanitized_title = ''.join(char for char in title if char.isalnum() or char in [' ', '-']).rstrip().replace(' ', '_')
        
        if len(sanitized_title) > max_filename_length:
            print(f"Title is too long, skipping: {title[:50]}...")
            skipped += 1
            continue
            
        filename = sanitized_title + '.json'
        new_dest_path = dest_directory / filename

        # Write JSON data to new file
        with new_dest_path.open('w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, indent=4, ensure_ascii=False)
            
        processed += 1
        if processed % 10 == 0:  # Progress update every 10 files
            print(f"Processed {processed} files...")

    print(f"Processed: {processed}")
    print(f"Skipped: {skipped}")
    print(f"Total files in directory: {count_files(dest_directory)}")
    
    if processed < num_proposals:
        print(f"Warning: Could only process {processed} valid proposals out of {num_proposals} requested")

def main():
    print("Starting main function")
    
    # Get the current working directory
    current_dir = Path.cwd()
    print(f"Current working directory: {current_dir}")
    
    # Define the base directory (project root)
    try:
        base_directory = Path(__file__).resolve().parent.parent
        print(f"Base directory: {base_directory}")
    except Exception as e:
        print(f"Error getting base directory: {e}")
        return

    # Source CSV file path (relative to project root)
    csv_path = base_directory / 'data' / 'interim' / 'grants.csv'
    print(f"CSV path: {csv_path}")
    
    # Destination directory to save the JSON files (relative to project root)
    dest_directory = base_directory / 'data' / 'proposal' / 'human'
    print(f"Destination directory: {dest_directory}")
    
    # Number of proposals to generate
    num_proposals = 250  # Change this number as needed
    
    process_csv(csv_path, dest_directory, num_proposals)

if __name__ == "__main__":
    print("Script starting")
    main()