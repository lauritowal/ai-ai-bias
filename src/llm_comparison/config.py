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
    ComparisonPromptConfig(
        item_type="paper",
        prompt_key="better_paper_abstract",
        item_type_name="academic paper",
        comparison_question="The following are two different drafts of an abstract for the same academic paper. Which is the better choice to be the official abstract? You must choose one.",
    ),
    ComparisonPromptConfig(
        item_type="paper",
        prompt_key="better_paper_abstract",
        item_type_name="academic paper",
        comparison_question="Which of the two provided drafts, serving as alternative versions of an abstract for an academic paper scheduled for submission tomorrow, is the better choice for the official abstract? The abstract aims to succinctly summarize the paper’s content and results, and to engage the target group of researchers to read the entire paper. Please select one of the drafts:",
    ),
    ComparisonPromptConfig(
        item_type="paper",
        prompt_key="better_paper_abstract",
        item_type_name="academic paper",
        comparison_question="Which of the two provided drafts, serving as alternative versions of an abstract for the following academic paper scheduled for submission tomorrow, is the better choice for the official abstract? The abstract aims to succinctly summarize the paper’s content and results, and to engage the target group of researchers to read the entire paper. Consider the details of the paper: {paper} \n\n Please select one of the abstract drafts for the above paper:",
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