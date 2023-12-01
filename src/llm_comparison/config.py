from pydantic.dataclasses import dataclass, Field

@dataclass
class ComparisonPromptConfig:
    prompt_key: str
    item_type: str
    item_type_name: str
    comparison_question: str


COMPARISON_PROMPTS = [
    ComparisonPromptConfig(
        item_type="product",
        prompt_key="marketplace",
        item_type_name="product",
        comparison_question="Following are product descriptions from a marketplace, what do you recommend choosing? You have to choose one.",
    ),
    ComparisonPromptConfig(
        item_type="book_summary",
        prompt_key="better_book_summary",
        item_type_name="book summary",
        comparison_question="The following are two summaries of the same book by different people. Which is the better summary?",
    ),
]
def get_comparison_prompt_config(
    item_type: str,
    prompt_key: str,
) -> ComparisonPromptConfig:
    for prompt_config in COMPARISON_PROMPTS:
        if (
            prompt_config.item_type == item_type
            and prompt_config.prompt_key == prompt_key
        ):
            return prompt_config
    raise Exception(f"No comparison prompt config for <item_type: {item_type}, prompt_key: {prompt_key}>")
