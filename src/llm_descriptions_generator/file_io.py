import datetime
import json
import pathlib
import re
import toml
from typing import Optional

from schema import (
    HumanTextItemDescriptionBatch,
    LlmGeneratedTextItemDescriptionBatch,
    Origin,
)

THIS_FILE_DIR = pathlib.Path(__file__).parent.resolve()
LLM_GENERATED_OUTPUT_DIR = THIS_FILE_DIR / "../../data/_llm_generated"
HUMAN_GENERATED_INPUT_TOML_DIR = THIS_FILE_DIR / "../../data/"


def load_human_text_item_descriptions_from_toml_file(
    filepath: str,
) -> HumanTextItemDescriptionBatch:
    print("Loading", filepath)
    with open(filepath) as f:
        data = toml.loads(f.read())
    item_type = data["type"].strip()
    title = data["prompt"].strip()
    descriptions = data["human_desc"] if isinstance(data["human_desc"], list) else [data["human_desc"]]
    return HumanTextItemDescriptionBatch(
        item_type=item_type,
        title=title.strip(),
        descriptions=[d.strip() for d in descriptions],
        origin=Origin.Human,
    )

def load_many_human_text_item_descriptions_from_toml_files(
    item_type: str,
    item_filename: Optional[str] = None,
) -> list[HumanTextItemDescriptionBatch]:
    item_type_dirpath = HUMAN_GENERATED_INPUT_TOML_DIR / item_type

    if item_filename:
        filepath = item_type_dirpath / item_filename
        return [load_human_text_item_descriptions_from_toml_file(str(filepath))]
    
    filepaths = item_type_dirpath.glob("*.toml")
    human_item_description_batches = [
        load_human_text_item_descriptions_from_toml_file(filepath) for filepath in filepaths
    ]
    return human_item_description_batches


def to_safe_filename(
    title_text: str,
    file_extension: str,
    prompt_uid: Optional[str] = None,
    max_title_characters: Optional[int] = 32,
) -> str:
    cleaned_title = re.sub(r'[^A-Za-z0-9 ]+', "", title_text).replace(" ", "_").lower()
    cleaned_shortened_title = cleaned_title[:max_title_characters]
    filename = "-".join([
        cleaned_shortened_title,
        prompt_uid,
    ])
    filename += file_extension
    return filename

def generate_filepath(title: str, item_type: str,  prompt_uid: str, file_extension: str = ".json"):
    filename = to_safe_filename(
        title_text=title,
        file_extension=file_extension,
        prompt_uid=prompt_uid,
    )   

    filepath = LLM_GENERATED_OUTPUT_DIR / item_type / filename

    return filepath

def save_llm_description_batch_to_json_file(
    llm_description_batch: LlmGeneratedTextItemDescriptionBatch,
    filepath: pathlib.Path
) -> None:
    # create directory if not exists
    filepath.parent.mkdir(exist_ok=True, parents=True) 

    with open(filepath, "w") as file:
        json.dump(llm_description_batch.__dict__, file, ensure_ascii=False, indent=4)


def load_llm_description_batch_from_json_file(
    filepath: str,
) -> LlmGeneratedTextItemDescriptionBatch:
    print("Loading", filepath)
    with open(filepath) as f:
        data = json.load(f)
    return LlmGeneratedTextItemDescriptionBatch(**data)