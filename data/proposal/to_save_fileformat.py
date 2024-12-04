import os
import re
from typing import Optional

def standardize_for_filepath(text: str) -> str:
    return re.sub(r'[^A-Za-z0-9 _]+', "", text).replace(" ", "_").lower()

def to_safe_filename(
    title_text: str,
    file_extension: Optional[str] = None,
    prompt_key: Optional[str] = None,
    max_title_characters: Optional[int] = 32,
) -> str:
    # Remove the file extension before cleaning
    base_name = os.path.splitext(title_text)[0]
    cleaned_title = standardize_for_filepath(base_name)
    cleaned_shortened_title = cleaned_title[:max_title_characters]
    filename = cleaned_shortened_title
    if prompt_key:
        filename += f"-{prompt_key}"
    # Add .json extension
    filename += ".json"
    return filename

folder = "/home/wombat_share/laurito/ai-ai-bias/data/proposal/human"

# go through folder human and update each file name to make it safe
for file in os.listdir(folder):
    old_path = os.path.join(folder, file)
    new_file_name = to_safe_filename(file)
    new_path = os.path.join(folder, new_file_name)  # Don't add .json here, it's already in the filename
    os.rename(old_path, new_path)