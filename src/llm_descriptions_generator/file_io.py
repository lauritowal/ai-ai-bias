import json
import logging
from pathlib import Path
import re
import toml
from typing import Optional

from llm_descriptions_generator.schema import (
    Engine,
    HumanTextItemDescriptionBatch,
    LlmGeneratedTextItemDescriptionBatch,
    Origin,
    TextItemDescriptionBatch,
)

THIS_FILE_DIR = Path(__file__).parent.resolve()
DATA_DIR = THIS_FILE_DIR / "../../data"

# DEPRECATED (see json files instead)
def load_human_text_item_descriptions_from_toml_file(
    filepath: str,
) -> HumanTextItemDescriptionBatch:
    print("Loading Human Text from", filepath)

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

# DEPRECATED (see json files instead)
def load_many_human_text_item_descriptions_from_toml_files(
    item_type: str,
    item_filename: Optional[str] = None,
) -> list[HumanTextItemDescriptionBatch]:
    HUMAN_GENERATED_INPUT_TOML_DIR = THIS_FILE_DIR / "../../data/"
    item_type_dirpath = HUMAN_GENERATED_INPUT_TOML_DIR / item_type

    if item_filename:
        filepath = item_type_dirpath / item_filename
        return [load_human_text_item_descriptions_from_toml_file(str(filepath))]
    
    filepaths = item_type_dirpath.glob("*.toml")

    human_item_description_batches = [
        load_human_text_item_descriptions_from_toml_file(filepath) for filepath in filepaths
    ]
    return human_item_description_batches

def standardize_for_filepath(text: str) -> str:
    return re.sub(r'[^A-Za-z0-9 _]+', "", text).replace(" ", "_").lower()

def to_safe_filename(
    title_text: str,
    file_extension: Optional[str] = None,
    prompt_uid: Optional[str] = None,
    max_title_characters: Optional[int] = 32,
) -> str:
    cleaned_title = standardize_for_filepath(title_text)
    cleaned_shortened_title = cleaned_title[:max_title_characters]
    filename = cleaned_shortened_title
    if prompt_uid:
        filename += f"-{prompt_uid}"
    if file_extension:
        filename += file_extension
    return filename

def generate_descriptions_dirpath(
    item_type: str,
    origin: Origin,
    llm_engine: Optional[Engine] = None,
):
    item_type_dirname = standardize_for_filepath(item_type)
    origin_dirname = standardize_for_filepath(origin)
    if origin == Origin.Human:
        return DATA_DIR / item_type_dirname / origin_dirname
    if origin == Origin.LLM:
        if not llm_engine:
            raise Exception("Generating LLM description filepaths requires explicit `llm_engine`")
        llm_engine_dirname = standardize_for_filepath(llm_engine)
        return DATA_DIR / item_type_dirname / origin_dirname / llm_engine_dirname
    raise f"Unrecognized origin: '{origin}'"
    
def generate_descriptions_filepath(
    title: str,
    item_type: str,
    origin: Origin,
    file_extension: str = ".json",
    llm_engine: Optional[Engine] = None,
    prompt_uid: Optional[str] = None,
) -> Path:
    filename = to_safe_filename(
        title_text=title,
        file_extension=file_extension,
        prompt_uid=prompt_uid,
    )
    dirpath = generate_descriptions_dirpath(
        item_type=item_type,
        origin=origin,
        llm_engine=llm_engine,
    )
    return dirpath / filename


def save_description_batch_to_json_file(
    description_batch: TextItemDescriptionBatch,
    filepath: Path
) -> None:
    logging.info(f"Saving data to file at: {filepath}")
    # create directory if not exists
    filepath.parent.mkdir(exist_ok=True, parents=True) 

    with open(filepath, "w") as file:
        json.dump(description_batch.__dict__, file, ensure_ascii=False, indent=4)

    logging.info(f"Saved description_batch to: {filepath}")


def load_description_batch_from_json_file(
    filepath: str,
) -> TextItemDescriptionBatch:
    logging.info(f"Loading descriptions from: {filepath}")
    with open(filepath) as f:
        data = json.load(f)
    origin = data.get("origin")
    if origin == Origin.LLM:
        return LlmGeneratedTextItemDescriptionBatch(**data)
    if origin == Origin.Human:
        return HumanTextItemDescriptionBatch(**data)
    raise f"Unrecognized origin: {origin}"


def load_all_human_description_batches(
    item_type: str,
    item_filename: Optional[str] = None,
) -> list[HumanTextItemDescriptionBatch]:
    dirpath = generate_descriptions_dirpath(
        item_type=item_type,
        origin=Origin.Human,
    )

    if item_filename:
        filepath = dirpath / item_filename
        return [load_description_batch_from_json_file(str(filepath))]
    
    filepaths = dirpath.glob("*.json")

    human_item_description_batches = [
        load_description_batch_from_json_file(filepath) for filepath in filepaths
    ]

    return human_item_description_batches


def load_all_llm_json_summary_batches(
    item_type: str,
) -> list[LlmGeneratedTextItemDescriptionBatch]:
    LATEST_JSON_SUMMARY_ENGINE = Engine.gpt4turbo
    LATEST_JSON_SUMMARY_PROMPT_NICKNAME = "jsonify_key_details"
    
    dirpath = generate_descriptions_dirpath(
        item_type=item_type,
        origin=Origin.LLM,
        llm_engine=LATEST_JSON_SUMMARY_ENGINE,
    )
    filepaths = dirpath.glob("*.json")

    description_batches: list[LlmGeneratedTextItemDescriptionBatch] = [
        load_description_batch_from_json_file(filepath) for filepath in filepaths
    ]

    json_summary_description_batches = [
        db for db in description_batches
        if db.generation_prompt_nickname == LATEST_JSON_SUMMARY_PROMPT_NICKNAME
    ]

    return json_summary_description_batches


def load_all_llm_description_batches(
    item_type: str,
    title: Optional[str] = None,
    llm_engine: Optional[Engine] = None,
    prompt_uid: Optional[str] = None,
) -> list[LlmGeneratedTextItemDescriptionBatch]:
    if llm_engine:
        llm_engines = [llm_engine]
    else:
        llm_engines = [e for e in Engine]
    
    filepaths: Path = []
    for engine in llm_engines:
        dirpath = generate_descriptions_dirpath(
            item_type=item_type,
            origin=Origin.LLM,
            llm_engine=engine,
        )
        
        if title:
            partial_filename = to_safe_filename(
                title_text=title,
                prompt_uid=prompt_uid,
            )
            filepaths += dirpath.glob(f"*{partial_filename}*.json")
        elif prompt_uid:
            filepaths += dirpath.glob(f"*{prompt_uid}*.json")
        else:
            filepaths += dirpath.glob("*.json")
    
    llm_description_batches: list[LlmGeneratedTextItemDescriptionBatch] = []
    for filepath in filepaths:
        llm_description_batches.append(
            load_description_batch_from_json_file(filepath=filepath)
        )

        print("filepath llms", filepath)
    return llm_description_batches
