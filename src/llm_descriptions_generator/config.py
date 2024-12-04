from llm_descriptions_generator.schema import (
    PromptDescriptionSource,
    ProductDetailsJson,
    TextItemGenerationPromptConfig,
    ProposalDetailsJson
)

TEXT_GENERATION_PROMPT_CONFIG = {
    "product": [
        TextItemGenerationPromptConfig(
            item_type="product",
            prompt_nickname="original_title_only",
            prompt_base_text="Write an advertising description for the following product that will be attractive to buyers.",
            description_source=PromptDescriptionSource.Human,
            include_descriptions=False,
        ),
        TextItemGenerationPromptConfig(
            item_type="product",
            prompt_nickname="include_descriptions",
            prompt_base_text="Write an advertising description for the following product that will attractive to buyers. Use the existing description below as a guideline, matching it roughly in quality and level of detail. Do not include information not available in the description below. Do not directly plagiarize the description below.",
            description_source=PromptDescriptionSource.Human,
            include_descriptions=True,
        ),
        TextItemGenerationPromptConfig(
            item_type="product",
            prompt_nickname="short_and_pointed",
            prompt_base_text="Write an advertising description for the following product. Use the existing description below as a guideline, matching it roughly in quality and level of detail. Do not include information not available in the description below. Do not directly plagiarize the description below. Be concise and informative. Assume potential buyers who read the ad have access to a photo of the product, and are scanning through many different similar advertisements, spending little time on each, and that they value being able to quickly see the most important details.",
            description_source=PromptDescriptionSource.Human,
            include_descriptions=True,
        ),
        TextItemGenerationPromptConfig(
            item_type="product",
            prompt_nickname="jsonify_key_details",
            prompt_base_text="Summarize the key details of the following product description and present in valid JSON format. Focus on extracting the features and characteristics in data form, without flavor text or prose.",
            description_source=PromptDescriptionSource.Human,
            include_descriptions=True,
            output_description_type=ProductDetailsJson,
        ),
        TextItemGenerationPromptConfig(
            item_type="product",
            prompt_nickname="from_json_details",
            prompt_base_text="Write an advertising description for the following product (described below with title and description of features and characteristics in JSON format). Make it attractive to buyers.",
            description_source=PromptDescriptionSource.LLM_JSON_Summary,
            include_descriptions=True,
        ),
        TextItemGenerationPromptConfig(
            item_type="product",
            prompt_nickname="from_json_product_listing",
            prompt_base_text="Write a product listing for the product described in the following JSON data summary (or summaries).",
            description_source=PromptDescriptionSource.LLM_JSON_Summary,
            include_title=False,
            include_descriptions=True,
        ),
        TextItemGenerationPromptConfig(
            item_type="product",
            prompt_nickname="from_json_avg_human",
            prompt_base_text="You are a relatively average person (NOT a trained marketing professional) trying to sell their products on an ecommerce site. Write a description of the product outlined in the following JSON data to use as a product listing on that site.",
            description_source=PromptDescriptionSource.LLM_JSON_Summary,
            include_title=False,
            include_descriptions=True,
        ),
        TextItemGenerationPromptConfig(
            item_type="product",
            prompt_nickname="from_json_non_native",
            prompt_base_text="You are a representative from a factory in another country trying to sell your products on an ecommerce site. Write a description of the product outlined in the following JSON data to use as a product listing on that site. Pretend English is not your first language, and that you don't have any experience with infomercial-style marketing language.",
            description_source=PromptDescriptionSource.LLM_JSON_Summary,
            include_title=False,
            include_descriptions=True,
        ),
        TextItemGenerationPromptConfig(
            item_type="product",
            prompt_nickname="from_json_old_person",
            prompt_base_text="Write an advertising description for the following product (described below with title and description of features and characteristics in JSON format). Make it easily accessible to elderly folks who may be easily confused.",
            description_source=PromptDescriptionSource.LLM_JSON_Summary,
            include_title=False,
            include_descriptions=True,
        ),
    ],
    "paper": [
        TextItemGenerationPromptConfig(
            item_type="paper",
            prompt_nickname="write_xml_paper_abstract",
            prompt_base_text="Read the following academic paper (in XML format) and create an abstract for it.",
            description_source=PromptDescriptionSource.AcademicPaperBody,
            include_title=False,
            include_descriptions=True,
        ),
        TextItemGenerationPromptConfig(
            item_type="paper",
            prompt_nickname="write_xml_paper_abstract_control_word_count",
            prompt_base_text="Read the following academic paper provided in XML format and create an abstract for it.",
            description_source=PromptDescriptionSource.AcademicPaperBody,
            include_title=False,
            include_descriptions=True,
            match_human_original_length=True,
        ),
    ],
    "proposal": [
        TextItemGenerationPromptConfig(
            item_type="proposal",
            prompt_nickname="jsonify_key_details_proposal",
            prompt_base_text="Extract and present the key details from this grant proposal abstract in valid JSON format. Keep array structures simple and flat where possible. Focus only on capturing the concrete features, characteristics, and data points - exclude any narrative text or prose descriptions.",
            description_source=PromptDescriptionSource.Proposal,
            include_descriptions=True,
            output_description_type=ProposalDetailsJson,
        ),
        TextItemGenerationPromptConfig(
            item_type="proposal",
            prompt_nickname="from_json_details_proposal",
            prompt_base_text="Write an abstract for a grant proposal based on the following details provided in JSON format. The JSON includes the title and key characteristics of the proposed project.",
            description_source=PromptDescriptionSource.LLM_JSON_Summary,
            include_title=False,
            include_descriptions=True,
            match_human_original_length=True,
        ),
    ],
    "book_review": [
        TextItemGenerationPromptConfig(
            item_type="book_review",
            prompt_nickname="mimic_human_reviews",
            prompt_base_text="Read the following reviews of a certain book and write a review of your own for the same book, as if you are a reader who cares about writing quality book reviews. Use a similar level of quality to the given reviews. Try to include only information that was present in the given reviews, and do not invent new information about the book.",
            description_source=PromptDescriptionSource.Human,
            include_descriptions=True,
        )
    ],
    "book_summary": [
        TextItemGenerationPromptConfig(
            item_type="book_summary",
            prompt_nickname="summary_with_human_version_as_guideline",
            prompt_base_text="Please write a summary of the following book. A sample summary is included below for reference. Use the sample as a guideline for quality and level of detail.",
            description_source=PromptDescriptionSource.Human,
            include_descriptions=True,
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
    raise Exception(f"item_type: '{item_type}' has no configs set up matching prompt_nickname: {prompt_nickname}")

def get_all_description_prompt_keys_for_item_type(item_type: str) -> list[str]:
    return [config.prompt_key for config in TEXT_GENERATION_PROMPT_CONFIG[item_type]]