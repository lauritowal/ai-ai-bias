import scripts_common_setup

import pathlib

from llm_descriptions_generator.file_io import (
    generate_descriptions_filepath,
    load_human_text_item_descriptions_from_toml_file,
    save_description_batch_to_json_file,
)

# OLD_TOML_DIRNAME = "products"
# OLD_TOML_DIRNAME = "book_review"
OLD_TOML_DIRNAME = "game_review"

DATA_DIR = pathlib.Path(__file__).parent.resolve() / "../data"

toml_source_dir = DATA_DIR / OLD_TOML_DIRNAME

print(f"Matching file paths for conversion in: {toml_source_dir}")
toml_filepaths = toml_source_dir.glob("*.toml")

for toml_source_file in toml_filepaths:
    print(f"Found TOML file to convert: {toml_source_file}")
    human_description_batch = load_human_text_item_descriptions_from_toml_file(toml_source_file)
    json_filepath = generate_descriptions_filepath(
        item_type=human_description_batch.item_type,
        title=human_description_batch.title,
        origin=human_description_batch.origin,
        file_extension=".json"
    )
    save_description_batch_to_json_file(
        description_batch=human_description_batch,
        filepath=json_filepath,
    )
    print(f"...Converted and saved: {json_filepath}")
