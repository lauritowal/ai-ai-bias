import json
import logging
from pathlib import Path
import re
import toml
from typing import Optional, Literal

from llm_descriptions_generator.schema import (
    Engine,
    HumanTextItemDescriptionBatch,
    LlmGeneratedTextItemDescriptionBatch,
    Origin,
    TextItemDescriptionBatch,
)

THIS_FILE_DIR = Path(__file__).parent.resolve()
DATA_DIR = THIS_FILE_DIR / "../../data"

PAPERS_HUMAN_SOURCE_SUBDIR_NAME = "xml"

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
    # prompt_uid: Optional[str] = None,
    prompt_key: Optional[str] = None,
    max_title_characters: Optional[int] = 32,
) -> str:
    cleaned_title = standardize_for_filepath(title_text)
    cleaned_shortened_title = cleaned_title[:max_title_characters]
    filename = cleaned_shortened_title
    # if prompt_uid:
    #     filename += f"-{prompt_uid}"
    if prompt_key:
        filename += f"-{prompt_key}"
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
    # prompt_uid: Optional[str] = None,
    prompt_key: Optional[str] = None,
) -> Path:
    filename = to_safe_filename(
        title_text=title,
        file_extension=file_extension,
        # prompt_uid=prompt_uid,
        prompt_key=prompt_key,
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


# Special loader just for academic paper raw data.
# Can be used to generate an abstract-only description batch
# to use as the human version in comparisons, or a body-only
# description to have LLM generate descriptions (abstracts) from.
def load_all_academic_papers_as_description_batches(
    item_type: Literal["paper"],
    fill_description_with: Literal["abstract", "body"],
    item_title_like: Optional[list[str]] = None,
) -> list[HumanTextItemDescriptionBatch]:
    if item_type != "paper":
        raise("Method only allowed for item_type='paper'")

    dirpath = generate_descriptions_dirpath(
        item_type=item_type,
        origin=Origin.Human,
    )
    # use special subdirectory to source the papers info
    dirpath = dirpath / PAPERS_HUMAN_SOURCE_SUBDIR_NAME
    
    filepaths = []
    if item_title_like:
        # case sensitivity hack...
        all_json_filepaths = dirpath.glob("*.json")
        for filepath in all_json_filepaths:
            for partial_filename in item_title_like:
                if to_safe_filename(partial_filename) in to_safe_filename(str(filepath.name)):
                    filepaths.append(filepath)
    else:
        filepaths = dirpath.glob("*.json")

    text_item_description_batches: list[HumanTextItemDescriptionBatch] = []
    for filepath in filepaths:
        with open(filepath, "r") as f:
            paper_data = json.load(f)
        
        # if no title in data, use filename as title
        title = paper_data.get("title", None)
        if not title:
            title = filepath.stem # without file extension
        
        abstract = paper_data.get("abstract", None)
        if not abstract:
            # try XML field if non-xml not found
            abstract = paper_data.get("abstract_xml", None)
        if not abstract:
            raise Exception(f"Paper file {filepath} is missing the 'abstract' attribute")
        
        if len(abstract) <= 20:
            raise Exception(f"Paper file {filepath} abstract has a suspiciously small character count. Maybe bad data?")
        
        body = paper_data.get("article", None)
        if not body:
            raise Exception(f"Paper file {filepath} is missing the 'article' attribute")
        
        if fill_description_with == "abstract":
            descriptions = [abstract]
        elif fill_description_with == "body":
            descriptions = [body]
        else:
            # should be impossible to get here if pydantic is working
            raise(f"Illegal choice for `fill_description_with`: {fill_description_with}")

        text_item_description_batches.append(
            HumanTextItemDescriptionBatch(
                item_type=item_type,
                title=title,
                descriptions=descriptions,
                origin=Origin.Human,
                meta=dict(abstract=abstract, body=body),
            )
        )
    return text_item_description_batches
    

def load_all_human_description_batches(
    item_type: str,
    item_title_like: Optional[list[str]] = None,
    item_filename: Optional[str] = None,
) -> list[HumanTextItemDescriptionBatch]:
    # HACK/SHIM that loads paper abstracts (only) as a data source
    if item_type == "paper":
        return load_all_academic_papers_as_description_batches(
            item_type=item_type,
            fill_description_with="abstract",
            item_title_like=item_title_like,
        )

    # normal handling
    dirpath = generate_descriptions_dirpath(
        item_type=item_type,
        origin=Origin.Human,
    )

    if item_filename:
        filepath = dirpath / item_filename
        return [load_description_batch_from_json_file(str(filepath))]
    
    filepaths = []
    if item_title_like:
        for title_fragment in item_title_like:
            partial_filename = to_safe_filename(title_text=title_fragment)
            filepaths += dirpath.glob(f"*{partial_filename}*.json")
    else:
        filepaths = dirpath.glob("*.json")

    human_item_description_batches = [
        load_description_batch_from_json_file(filepath) for filepath in filepaths
    ]

    return human_item_description_batches


def load_all_llm_json_summary_batches(
    item_type: str,
    item_title_like: Optional[list[str]] = None,
) -> list[LlmGeneratedTextItemDescriptionBatch]:
    LATEST_JSON_SUMMARY_ENGINE = Engine.gpt4turbo
    LATEST_JSON_SUMMARY_PROMPT_NICKNAME = "jsonify_key_details"
    
    dirpath = generate_descriptions_dirpath(
        item_type=item_type,
        origin=Origin.LLM,
        llm_engine=LATEST_JSON_SUMMARY_ENGINE,
    )

    filepaths = []
    if item_title_like:
        for title_fragment in item_title_like:
            partial_filename = to_safe_filename(title_text=title_fragment)
            filepaths += dirpath.glob(f"*{partial_filename}*{LATEST_JSON_SUMMARY_PROMPT_NICKNAME}*.json")
    else:
        filepaths = dirpath.glob(f"*{LATEST_JSON_SUMMARY_PROMPT_NICKNAME}*.json")

    description_batches: list[LlmGeneratedTextItemDescriptionBatch] = [
        load_description_batch_from_json_file(filepath) for filepath in filepaths
    ]
    return description_batches


def load_all_llm_description_batches(
    item_type: str,
    title: Optional[str] = None,
    llm_engine: Optional[Engine] = None,
    # prompt_uid: Optional[str] = None,
    prompt_nickname: Optional[str] = None,
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
        glob_str = "*.json"
        if prompt_nickname:
            glob_str = f"*{prompt_nickname}.json"
        
        if title:
            partial_filename = to_safe_filename(
                title_text=title,
                # prompt_uid=prompt_uid,
            )
            glob_str = f"*{partial_filename}{glob_str}"
        # elif prompt_uid:
        #     filepaths += dirpath.glob(f"*{prompt_uid}*.json")

        filepaths = dirpath.glob(glob_str)
    
    llm_description_batches: list[LlmGeneratedTextItemDescriptionBatch] = []
    for filepath in filepaths:
        llm_description_batches.append(
            load_description_batch_from_json_file(filepath=filepath)
        )
    
    if prompt_nickname:
        llm_description_batches = [
            batch for batch in llm_description_batches
            if batch.generation_prompt_nickname == prompt_nickname
        ]
    return llm_description_batches
