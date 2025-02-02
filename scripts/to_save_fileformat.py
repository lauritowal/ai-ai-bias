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
    is_file=True
) -> str:
    # Remove the file extension before cleaning
    base_name = os.path.splitext(title_text)[0]
    cleaned_title = standardize_for_filepath(base_name)
    cleaned_shortened_title = cleaned_title[:max_title_characters]
    filename = cleaned_shortened_title
    if prompt_key:
        filename += f"-{prompt_key}"
    # Add .json extension
    if is_file:
        filename += ".json"
    return filename