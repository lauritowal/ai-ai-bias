#!/bin/bash

# Get the project root folder and cd into it
DIR="$( dirname "${BASH_SOURCE[0]}" )"
echo Changing dir to $DIR/..
cd $DIR/..

WORKERS=1
OPTS="  --comparison-engine=together-mistralai/Mixtral-8x22B-Instruct-v0.1
        --comparison-engine=together-Qwen/Qwen1.5-4B-Chat
        --comparison-engine=together-meta-llama/Llama-3-8b-chat-hf
        --comparison-engine=together-meta-llama/Llama-3-70b-chat-hf
        --max-comparison-concurrent-workers=$WORKERS
        --min-description-generation-count=4"


poetry run python scripts/generate_and_compare_descriptions.py \
    --item-type=product \
    --comparison-prompt-key=marketplace_recommendation_force_decision \
    --description-prompt-key=from_json_details \
    --description-prompt-key=from_json_product_listing \
    --description-engine='gpt-3.5-turbo' \
    --description-engine='gpt-4-1106-preview' \
    $OPTS

sleep 60s # A hack to ensure another filename, otherwise the same filename is used and the file is overwritten

poetry run python3 scripts/generate_and_compare_descriptions.py \
    --item-type=paper \
    --comparison-prompt-key=literature_review_pick_one \
    --description-prompt-key=write_xml_paper_abstract_control_word_count \
    --description-engine='gpt-3.5-turbo-1106' \
    --description-engine='gpt-4-1106-preview' \
    $OPTS

