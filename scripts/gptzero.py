import os
import glob
import json
import time
from dotenv import load_dotenv
import requests
import logging

# Configure logging
logging.basicConfig(
    filename='gptzero_submission.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# Load environment variables from .env
load_dotenv()

# Ensure consistent environment variable naming
API_KEY = os.getenv("GPT_ZERO")  # Update this if your .env uses a different name

if not API_KEY:
    logging.error("GPT_ZERO_API_KEY not found in environment variables. Please check your .env file.")
    raise ValueError("GPT_ZERO_API_KEY not found in environment variables. Please check your .env file.")

# Constants
DATA_FOLDER = "/Users/walt/ai-ai-bias/data/product"
HUMAN_FOLDER = os.path.join(DATA_FOLDER, "human")
LLM_FOLDER = os.path.join(DATA_FOLDER, "llm", "gpt41106preview")  # Adjust if multiple subfolders
OUTPUT_FILE = "analysis_results.json"
MAX_RETRIES = 5  # Maximum number of retries for failed requests
BACKOFF_FACTOR = 1  # Factor for exponential backoff
MAX_CHAR_LIMIT = 50000  # Maximum characters per description as per API
API_ENDPOINT = "/v2/predict/text"  # Adjust based on the API's documentation

# New Constant: Maximum number of submissions
MAX_SUBMISSIONS = -1  # Set to None to process all descriptions

# Function to get title from human file path
def get_title_from_human_path(path):
    base = os.path.basename(path)
    title = os.path.splitext(base)[0]
    return title

# Function to get title from LLM file path
def get_title_from_llm_path(path):
    base = os.path.basename(path)
    title = base.replace("-from_json_details.json", "")
    return title

# 1) Collect all human and LLM files
human_files = glob.glob(os.path.join(HUMAN_FOLDER, "*.json"))
llm_files = glob.glob(os.path.join(LLM_FOLDER, "*-from_json_details.json"))

logging.info(f"Found {len(human_files)} human files and {len(llm_files)} LLM files.")

# 2) Map files by title
human_dict = {get_title_from_human_path(hf): hf for hf in human_files}
llm_dict = {get_title_from_llm_path(lf): lf for lf in llm_files}

# 3) Build a unified list of descriptions (independent items)
descriptions = []
for title, human_path in human_dict.items():
    if title in llm_dict:
        llm_path = llm_dict[title]
        
        # Load human description
        try:
            with open(human_path, 'r', encoding='utf-8') as f:
                h_data = json.load(f)
            human_desc = h_data.get("descriptions", [])
            human_desc_text = human_desc[0].strip() if human_desc else ""
        except Exception as e:
            logging.error(f"Failed to load human description for title '{title}': {e}")
            human_desc_text = ""
        
        # Load LLM description
        try:
            with open(llm_path, 'r', encoding='utf-8') as f:
                l_data = json.load(f)
            llm_desc = l_data.get("descriptions", [])
            llm_desc_text = llm_desc[0].strip() if llm_desc else ""
        except Exception as e:
            logging.error(f"Failed to load LLM description for title '{title}': {e}")
            llm_desc_text = ""
        
        # Truncate descriptions if necessary
        if len(human_desc_text) > MAX_CHAR_LIMIT:
            logging.info(f"Truncating human_description for title '{title}' to {MAX_CHAR_LIMIT} characters.")
            human_desc_text = human_desc_text[:MAX_CHAR_LIMIT]
        
        if len(llm_desc_text) > MAX_CHAR_LIMIT:
            logging.info(f"Truncating llm_description for title '{title}' to {MAX_CHAR_LIMIT} characters.")
            llm_desc_text = llm_desc_text[:MAX_CHAR_LIMIT]
        
        # Append human description as an independent item
        if human_desc_text:
            descriptions.append({
                "title": title,
                "description_type": "human_description",
                "text": human_desc_text
            })
        
        # Append LLM description as an independent item
        if llm_desc_text:
            descriptions.append({
                "title": title,
                "description_type": "llm_description",
                "text": llm_desc_text
            })

logging.info(f"Total descriptions to analyze: {len(descriptions)}")

# Apply the MAX_SUBMISSIONS limit
if MAX_SUBMISSIONS is not None:
    descriptions = descriptions[:MAX_SUBMISSIONS]
    logging.info(f"Limiting submissions to the first {MAX_SUBMISSIONS} descriptions.")

print(f"Total descriptions to analyze: {len(descriptions)}")

# 4) Function to submit a single description to GPTZero API
def submit_description(description, api_key):
    url = f"https://api.gptzero.me{API_ENDPOINT}"
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "document": description["text"],
        "multilingual": False  # Set to True if your descriptions are multilingual
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        response_json = response.json()
        logging.info(f"Successfully submitted: {description['title']} - {description['description_type']}")
        return response_json
    except requests.exceptions.Timeout:
        logging.error(f"Request timed out for: {description['title']} - {description['description_type']}")
        return {"error": "Request timed out"}
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error for {description['title']} - {description['description_type']}: {e} - Response: {response.text}")
        return {"error": f"HTTP error: {e}", "response": response.text}
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed for {description['title']} - {description['description_type']}: {e}")
        return {"error": str(e)}
    except json.JSONDecodeError:
        logging.error(f"Failed to parse JSON response for {description['title']} - {description['description_type']}.")
        return {"error": "Invalid JSON in response"}

# 5) Submit each description individually and collect results
results = []
total_descriptions = len(descriptions)
print(f"Submitting {total_descriptions} descriptions to GPTZero API...")

for idx, description in enumerate(descriptions, start=1):
    print(f"Submitting {idx}/{total_descriptions}: {description['title']} - {description['description_type']}")
    response = submit_description(description, API_KEY)
    
    # Append the result
    results.append({
        "title": description["title"],
        "description_type": description["description_type"],
        "original_text": description["text"],
        "gptzero_response": response
    })
    
    # Optional: Sleep to respect rate limits (adjust as necessary)
    time.sleep(1)

# 6) Save the results to a JSON file
try:
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved GPTZero analysis results to {OUTPUT_FILE}")
    logging.info(f"Saved GPTZero analysis results to {OUTPUT_FILE}")
except Exception as e:
    logging.error(f"Failed to save analysis results: {e}")
    print(f"Failed to save analysis results: {e}")
