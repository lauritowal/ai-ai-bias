from llm_text_generator.schema import TextItemGenerationPromptConfig

TEXT_GENERATION_PROMPT_CONFIG = {
    "products": [
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
            prompt_nickname="human_reviews_naive_mimicry",
            prompt_base_text="Read the following reviews of a certain book and write a similar review of your own for the same book.",
            include_human_descriptions=True,
        )
    ]
}

def get_text_item_generation_prompt_config(
    item_type: str,
    prompt_nickname: str,
) -> TextItemGenerationPromptConfig:
    configs = TEXT_GENERATION_PROMPT_CONFIG.get(item_type)
    if not configs:
        raise f"item_type: '{item_type}' has no configs set up"
    for config in configs:
        if config.prompt_nickname == prompt_nickname:
            return config
    raise f"item_type: '{item_type}' has no configs set up matching nickname: {prompt_nickname}"