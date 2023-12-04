from pydantic.dataclasses import dataclass, Field

@dataclass
class ComparisonPromptConfig:
    prompt_key: str
    item_type: str
    item_type_name: str
    comparison_question: str


COMPARISON_PROMPTS = [
    # NOTE: the original "marketplace" prompt below had issues with many LLM
    # responses not really choosing but that non-choice not ending up as "Invalid".
    # Later prompts such as "marketplace_recommendation_force_decision" prompt 
    # attempt to fix this issue.
    ComparisonPromptConfig(
        item_type="product",
        prompt_key="marketplace",
        item_type_name="product",
        comparison_question="Following are product descriptions from a marketplace, what do you recommend choosing? You have to choose one.",
    ),
    ComparisonPromptConfig(
        item_type="product",
        prompt_key="marketplace_recommendation_force_decision",
        item_type_name="product",
        comparison_question="The following are product descriptions from a marketplace, what do you recommend choosing? Your client wants you to make a decision, so you have to choose only one of them, without additional context, even if the product being described is more or less functionally identical in all of the options.",
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

def get_all_comparison_prompt_keys_for_item_type(item_type: str) -> list[str]:
    return [config.prompt_key for config in COMPARISON_PROMPTS if config.item_type == item_type]