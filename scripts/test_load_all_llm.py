import scripts_common_setup

from llm_descriptions_generator.file_io import load_all_llm_description_batches
from pprint import pprint

llm_batches = load_all_llm_description_batches(
    item_type="book_review",
    # title="poop",
    # title="Tomorrow, and Tomorrow, and Tomorrow [Gabrielle Zevin]",
    # prompt_uid="ad2506aecbc8cd78a0e85b9c7ae15e7b",
    # prompt_uid="4e76c12fe4e99bcf0524c947afabcf05",
)
pprint(llm_batches, width=5000)
