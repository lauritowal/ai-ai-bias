#!/bin/bash

# start in local virtual environment 
poetry shell

WORKERS=20

COMPARISON_ENGINES_ARGS="
    --comparison-engine=together-mistralai/Mixtral-8x22B-Instruct-v0.1
    --comparison-engine=together-meta-llama/Meta-Llama-3-8B-Instruct-Turbo
    --comparison-engine=together-meta-llama/Meta-Llama-3-70B-Instruct-Turbo
    --comparison-engine=together-Qwen/Qwen1.5-4B-Chat
    --comparison-engine=together-Qwen/Qwen1.5-14B-Chat
    --comparison-engine=together-Qwen/Qwen1.5-72B-Chat
    --comparison-engine=gpt-3.5-turbo
    --comparison-engine=gpt-4-1106-preview
"

DESCRIPTION_ENGINES_ARGS="
    --description-engine=together-meta-llama/Llama-3.3-70B-Instruct-Turbo
    --description-engine=gpt-3.5-turbo
    --description-engine=gpt-4-1106-preview
"




# python scripts/generate_llm_descriptions.py \
#     --item-type=product \
#     --prompt-nickname=jsonify_key_details \
#     --engine='gpt-4-1106-preview' \
#     --target-count=1

# Products
# poetry run python3 scripts/generate_and_compare_descriptions.py \
#     --item-type=product \
#     --comparison-prompt-key=marketplace_recommendation_force_decision \
#     --description-prompt-key=from_json_details \
#     --description-prompt-key=from_json_product_listing \
#     --min-description-generation-count=3 \
#     --max-comparison-concurrent-workers=$WORKERS \
#     ${COMPARISON_ENGINES_ARGS} \
#     ${DESCRIPTION_ENGINES_ARGS}

# sleep 60s # A hack to ensure another filename, otherwise the same filename is used and the file is overwritten

# # Papers
poetry run python3 scripts/generate_and_compare_descriptions.py \
    --item-type=paper \
    --comparison-prompt-key=literature_review_pick_one \
    --description-prompt-key=write_xml_paper_abstract_control_word_count \
     --min-description-generation-count=1  \
     --max-comparison-concurrent-workers=$WORKERS \
    ${COMPARISON_ENGINES_ARGS} \
    ${DESCRIPTION_ENGINES_ARGS}

# Generate Proposal jsons
# python scripts/generate_llm_descriptions.py \
#     --item-type=proposal \
#     --prompt-nickname=jsonify_key_details_proposal \
#     --engine='gpt-4-1106-preview' \
#     --target-count=1

# sleep 60s # A hack to ensure another filename, otherwise the same filename is used and the file is overwritten

# Proposals
# poetry run python3 scripts/generate_and_compare_descriptions.py \
#     --item-type=proposal \
#     --comparison-prompt-key=proposal_pick_one \
#     --description-prompt-key=from_json_details \
#     --min-description-generation-count=1  \
#     --max-comparison-concurrent-workers=$WORKERS \
#     ${COMPARISON_ENGINES_ARGS} \
#     ${DESCRIPTION_ENGINES_ARGS}

# poetry run python3 scripts/generate_llm_descriptions.py \
#     --item-type=proposal \
#     --prompt-nickname=from_json_details \
#     --target-count=3