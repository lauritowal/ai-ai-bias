from pathlib import Path
import re
import xml.etree.ElementTree as ET
import json
import numpy as np

def clean_text(text):
    # Strip and remove newlines and extra spaces
    return re.sub(r'\s+', ' ', text.strip())

def process_xml(file_path, output_format='md'):
    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Extract title from the first <S> tag under <PAPER>
    title_element = root.find('S')
    title = title_element.text.strip() if title_element is not None and title_element.text is not None else "Unknown_Title"

    # Extract and clean the abstract element
    abstract = root.find('ABSTRACT')
    abstract_text = clean_text(''.join(abstract.itertext())) if abstract is not None else "No Abstract"
    abstract_xml = ET.tostring(abstract, encoding='unicode', method='xml') if abstract is not None else "No Abstract XML"

    # Remove the abstract element from the tree
    if abstract is not None:
        root.remove(abstract)

    # Format article content based on output_format
    if output_format == 'md':
        article_content = ' '.join(element.text if element.text is not None else '' for element in root.iter() if element.tag == 'S')
    elif output_format == 'xml':
        article_content = ET.tostring(root, encoding='unicode', method='xml')

    return title, abstract_text, abstract_xml, article_content

def process_directory(directory, dest_directory, output_format='md'):
    # Iterate over files in the directory
    for file in directory.iterdir():
        if file.suffix == '.xml':
            # Process the XML file
            title, abstract, abstract_xml, article_content = process_xml(file, output_format)

            # Get relative path of the source XML from 'ai-ai-bias'
            relative_xml_path = file.relative_to(*file.parts[:file.parts.index('ai-ai-bias') + 1])

            # Construct JSON object
            json_data = {
                "item_type": "paper",
                "title": title,
                "abstract": abstract,
                "abstract_xml": abstract_xml,
                "origin": "Human",
                "article": article_content,
                "source_xml": str(relative_xml_path)  # Include the relative path of the source XML
            }
            
            # Generate filename from title and truncate to avoid too long filenames
            max_filename_length = 250
            sanitized_title = ''.join(char for char in title if char.isalnum() or char in [' ', '-']).rstrip().replace(' ', '_')
            # truncated_title = sanitized_title[:max_filename_length]
            if len(sanitized_title) > max_filename_length:
                print("Title is too long, skipping since something went wrong:", file)
                return
            filename = sanitized_title + '.json'

            new_dest_path = dest_directory / filename

            # Create directory if it does not exist
            dest_directory.mkdir(parents=True, exist_ok=True)

            # Write JSON data to new file
            with new_dest_path.open('w', encoding='utf-8') as json_file:
                json.dump(json_data, json_file, indent=4, ensure_ascii=False)

def main(src_root_directory, dest_directory, num_dirs, output_format='md'):
    # Define the base directory (project root)
    base_directory = Path(__file__).resolve().parent.parent

    src_root_directory = base_directory / src_root_directory
    dest_directory = base_directory / dest_directory / output_format

    # Find all 'Documents_xml' directories
    documents_xml_dirs = src_root_directory.rglob('Documents_xml')

    # Randomly select directories
    selected_dirs = np.random.choice(list(documents_xml_dirs), num_dirs, replace=False)

    # Process each selected directory
    for directory in selected_dirs:
        process_directory(directory, dest_directory, output_format)

# Source root directory containing the subdirectories with XML files (relative to project root)
src_root_directory = Path('data/raw/paper/scisummnet_release1.1__20190413/top1000_complete')

# Destination directory to save the JSON files (relative to project root)
dest_directory = Path('data/paper_2/human')

main(src_root_directory, dest_directory, 100, output_format='xml')