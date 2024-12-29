#!/bin/bash

# start in local virtual environment 
poetry shell

WORKERS=1

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
    --description-engine=together-meta-llama/Meta-Llama-3-70B-Instruct-Turbo
    --description-engine=gpt-3.5-turbo
    --description-engine=gpt-4-1106-preview
"

# Generate jsons
python scripts/generate_llm_descriptions.py \
    --item-type=proposal \
    --prompt-nickname=jsonify_key_details_proposal \
    --engine='gpt-4-1106-preview' \
    --target-count=1

# Generate abstracts and compare them
# ALL models
poetry run python3 scripts/generate_and_compare_descriptions.py \
    --item-type=proposal \
    --comparison-prompt-key=proposal_pick_one \
    --description-prompt-key=from_json_details \
    --min-description-generation-count=3  \
    --max-comparison-concurrent-workers=$WORKERS \
    ${COMPARISON_ENGINES_ARGS} \
    ${DESCRIPTION_ENGINES_ARGS}