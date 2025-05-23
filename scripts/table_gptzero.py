import json
import pandas as pd
import os
import logging

# Configure logging
logging.basicConfig(
    filename='create_analysis_table.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

def load_analysis_results(file_path):
    """
    Load the analysis_results.json file.

    Args:
        file_path (str): Path to the analysis_results.json file.

    Returns:
        list: List of analysis result entries.
    """
    if not os.path.exists(file_path):
        logging.error(f"The file {file_path} does not exist.")
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data

import json  # Import json to stringify nested dictionaries

def extract_document_data(entry):
    """
    Extract the required fields from each analysis entry at the document level.

    Args:
        entry (dict): A single analysis result entry.

    Returns:
        dict: A dictionary containing the extracted fields.
    """
    extracted = {
        "title": entry.get("title", ""),
        "description_type": entry.get("description_type", ""),
        # Stringify gptzero_response for inclusion in DataFrame
        "gptzero_response": json.dumps(entry.get("gptzero_response", {})),
        "class_prob_human": None,
        "class_prob_ai": None,
        "class_prob_mixed": None,
        "confidence_score_ai": None,
        "confidence_score_human": None,
        "confidence_score_mixed": None,
        "confidence_score": None,
        "predicted_class": None
    }

    gptzero_response = entry.get("gptzero_response", {})

    if not isinstance(gptzero_response, dict):
        logging.error(f"'gptzero_response' is not a dictionary for title '{extracted['title']}' and description_type '{extracted['description_type']}'.")
        return extracted

    # Extract 'documents' array
    documents = gptzero_response.get("documents", [])

    if not documents:
        logging.warning(f"No documents found in response for title '{extracted['title']}' and description_type '{extracted['description_type']}'.")
        return extracted

    document = documents[0]

    # Extract class probabilities
    class_probs = document.get("class_probabilities", {})
    extracted["class_prob_human"] = class_probs.get("human", None)
    extracted["class_prob_ai"] = class_probs.get("ai", None)
    extracted["class_prob_mixed"] = class_probs.get("mixed", None)

    # Extract confidence scores
    confidence_scores_raw = document.get("confidence_scores_raw", {}).get("identity", {})
    extracted["confidence_score_ai"] = confidence_scores_raw.get("ai", None)
    extracted["confidence_score_human"] = confidence_scores_raw.get("human", None)
    extracted["confidence_score_mixed"] = confidence_scores_raw.get("mixed", None)

    # Extract overall confidence score
    extracted["confidence_score"] = document.get("confidence_score", None)

    # Extract predicted class
    extracted["predicted_class"] = document.get("predicted_class", None)

    return extracted


def create_table(analysis_data):
    """
    Create a structured table from the analysis data.

    Args:
        analysis_data (list): List of analysis result entries.

    Returns:
        pandas.DataFrame: DataFrame containing the structured data.
    """
    extracted_data = []
    human_count = 0
    llm_count = 0
    error_count = 0
    no_doc_count = 0

    for idx, entry in enumerate(analysis_data, start=1):
        extracted = extract_document_data(entry)
        extracted_data.append(extracted)

        # Count description types
        if extracted["description_type"] == "human_description":
            human_count += 1
        elif extracted["description_type"] == "llm_description":
            llm_count += 1

        # Count errors
        if "error" in entry.get("gptzero_response", {}):
            error_count += 1

        # Count entries with no documents
        if (extracted["class_prob_human"] is None and 
            extracted["class_prob_ai"] is None and 
            extracted["class_prob_mixed"] is None):
            no_doc_count += 1

    logging.info(f"Total entries processed: {len(extracted_data)}")
    logging.info(f"Human descriptions: {human_count}")
    logging.info(f"LLM descriptions: {llm_count}")
    logging.info(f"Entries with errors: {error_count}")
    logging.info(f"Entries with no documents: {no_doc_count}")

    # Create DataFrame
    df = pd.DataFrame(extracted_data)

    # Optional: Reorder columns for better readability
    column_order = [
        "title",
        "description_type",
        "class_prob_human",
        "class_prob_ai",
        "class_prob_mixed",
        "confidence_score_ai",
        "confidence_score_human",
        "confidence_score_mixed",
        "confidence_score",
        "predicted_class"
    ]
    df = df[column_order]

    return df

def save_to_csv(df, output_file):
    """
    Save the DataFrame to a CSV file.

    Args:
        df (pandas.DataFrame): The DataFrame to save.
        output_file (str): Path to the output CSV file.
    """
    try:
        df.to_csv(output_file, index=False, encoding='utf-8')
        logging.info(f"Saved the analysis table to {output_file}")
        print(f"Saved the analysis table to {output_file}")
    except Exception as e:
        logging.error(f"Failed to save analysis table: {e}")
        print(f"Failed to save analysis table: {e}")

def main():
    # Define the path to the analysis_results.json file
    analysis_file = "/Users/walt/ai-ai-bias/scripts/analysis_results.json"  # Adjust the path if necessary

    # Define the output CSV file
    output_csv = "/Users/walt/ai-ai-bias/scripts/analysis_table.csv"

    # Load the analysis results
    try:
        analysis_data = load_analysis_results(analysis_file)
    except FileNotFoundError as e:
        logging.error(e)
        print(e)
        return
    except json.JSONDecodeError:
        logging.error(f"Failed to parse JSON from {analysis_file}. Please ensure it's a valid JSON file.")
        print(f"Failed to parse JSON from {analysis_file}. Please ensure it's a valid JSON file.")
        return

    # Debug: Check the number of entries loaded
    print(f"Number of entries loaded: {len(analysis_data)}")
    logging.info(f"Number of entries loaded: {len(analysis_data)}")

    # Debug: Check if 'gptzero_response' exists in all entries
    missing_response = [entry for entry in analysis_data if 'gptzero_response' not in entry]
    if missing_response:
        print(f"Found {len(missing_response)} entries missing 'gptzero_response'. Check 'gptzero_submission.log' for details.")
        logging.warning(f"Found {len(missing_response)} entries missing 'gptzero_response'.")
    else:
        print("All entries have 'gptzero_response'.")
        logging.info("All entries have 'gptzero_response'.")

    # Create the table
    df = create_table(analysis_data)

    # Debug: Print DataFrame columns
    print("DataFrame Columns:", df.columns.tolist())

    # Display counts
    print(f"Total entries processed: {len(df)}")
    print(f"Human descriptions: {df['description_type'].value_counts().get('human_description', 0)}")
    print(f"LLM descriptions: {df['description_type'].value_counts().get('llm_description', 0)}")
    print(f"Entries with no documents: {df[['class_prob_human', 'class_prob_ai', 'class_prob_mixed']].isnull().all(axis=1).sum()}")

    logging.info(f"Total entries processed: {len(df)}")
    logging.info(f"Human descriptions: {df['description_type'].value_counts().get('human_description', 0)}")
    logging.info(f"LLM descriptions: {df['description_type'].value_counts().get('llm_description', 0)}")
    logging.info(f"Entries with no documents: {df[['class_prob_human', 'class_prob_ai', 'class_prob_mixed']].isnull().all(axis=1).sum()}")

    # Save the table to CSV
    save_to_csv(df, output_csv)

if __name__ == "__main__":
    main()
