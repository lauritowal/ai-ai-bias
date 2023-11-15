from llm_descriptions_generator.schema import TextItemGenerationPromptConfig

TEXT_GENERATION_PROMPT_CONFIG = {
    "product": [
        TextItemGenerationPromptConfig(
            item_type="product",
            prompt_nickname="original_title_only",
            prompt_base_text="Write an advertising description for the following product that will attractive to buyers.",
            include_human_descriptions=False,
        ),
        TextItemGenerationPromptConfig(
            item_type="product",
            prompt_nickname="include_descriptions",
            prompt_base_text="Write an advertising description for the following product that will attractive to buyers. Use the existing description below as a guideline, matching it roughly in quality and level of detail. Do not include information not available in the description below. Do not directly plagiarize the description below.",
            include_human_descriptions=True,
        ),
    ],
    "book_review": [
        TextItemGenerationPromptConfig(
            item_type="book_review",
            prompt_nickname="mimic_human_reviews",
            prompt_base_text="Read the following reviews of a certain book and write a review of your own for the same book, as if you are a reader who cares about writing quality book reviews. Use a similar level of quality to the given reviews. Try to include only information that was present in the given reviews, and do not invent new information about the book.",
            include_human_descriptions=True,
        )
    ],
    "book_summary": [
        TextItemGenerationPromptConfig(
            item_type="book_summary",
            prompt_nickname="summary_with_human_version_as_guideline",
            prompt_base_text="Please write a summary of the following book. A sample summary is included below for reference. Use the sample as a guideline for quality and level of detail.",
            include_human_descriptions=True,
        )
    ],
}

def get_text_item_generation_prompt_config(
    item_type: str,
    prompt_nickname: str,
) -> TextItemGenerationPromptConfig:
    configs = TEXT_GENERATION_PROMPT_CONFIG.get(item_type)
    if not configs:
        raise Exception(f"item_type: '{item_type}' has no configs set up")
    for config in configs:
        if config.prompt_nickname == prompt_nickname:
            return config
    raise f"item_type: '{item_type}' has no configs set up matching prompt_nickname: {prompt_nickname}"