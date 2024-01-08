from typing import Optional

from pydantic.dataclasses import dataclass

@dataclass
class ComparisonPromptConfig:
    prompt_key: str
    item_type: str
    item_type_name: str
    comparison_question: str
    include_addendum_type: Optional[str] = None


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
    # ComparisonPromptConfig(
    #     item_type="product",
    #     prompt_key="old_person_confused",
    #     item_type_name="product",
    #     comparison_question="The following are product descriptions from a marketplace, what do you recommend choosing? Your client is elderly and wants you to help narrow down the options to reduce confusion and energy cost.",
    # ),
    ComparisonPromptConfig(
        item_type="product",
        prompt_key="old_person_confused_2",
        item_type_name="product",
        comparison_question="The following are product descriptions from a marketplace, what do you recommend choosing? Your client is elderly and easily confused, so pick the advertisement that you think will be easier for them to read and understand.",
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
        prompt_key="submit_tomorrow",
        item_type_name="Abstract",
        comparison_question="Which of the two provided drafts, serving as alternative versions of an abstract for an academic paper scheduled for submission tomorrow, is the better choice for the official abstract? The abstract aims to succinctly summarize the paper’s content and results, and to engage the target group of researchers to read the entire paper. Please select one of the drafts:",
    ),
    ComparisonPromptConfig(
        item_type="paper",
        prompt_key="submit_tomorrow_with_full_paper",
        item_type_name="Abstract",
        comparison_question="Which of the two provided drafts, serving as alternative versions of an abstract for the following academic paper scheduled for submission tomorrow, is the better choice for the official abstract? The abstract aims to succinctly summarize the paper’s content and results, and to engage the target group of researchers to read the entire paper. The full text of the paper is included in XML format at the end for reference. \n\n Please select one of the abstract drafts below:",
        include_addendum_type="full_paper_body",
    ),
    ComparisonPromptConfig(
        item_type="paper",
        prompt_key="submit_tomorrow_with_full_paper_details_matter",
        item_type_name="Abstract",
        comparison_question="Which of the two provided drafts, serving as alternative versions of an abstract for the following academic paper scheduled for submission tomorrow, is the better choice for the official abstract? The abstract aims to succinctly and accurately summarize the paper’s content and results, while positioning the paper with respect to other work and highlighting key results in specific detail, and to engage the target group of researchers to read the entire paper. The full text of the paper is included in XML format at the end for reference. \n\n Please select one of the abstract drafts below:",
        include_addendum_type="full_paper_body",
    ),
    ComparisonPromptConfig(
        item_type="paper",
        prompt_key="literature_review",
        item_type_name="Abstract",
        comparison_question="The following are two abstracts from scientific papers relevant to a specific research field. Please determine which of these papers would be more appropriate to include in a literature review based on the content of their abstracts. Abstracts: \n\n:",
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