#!/bin/bash
# require at least one parameter
if [ $# -eq 0 ]; then
    echo "Usage: $0 <MODELS>"
    echo "MODELS: groq-llama3-8b-8192 groq-mixtral-8x7b-32768 groq-llama3-70b-8192"
    echo "        together-meta-llama/Llama-3-8b-chat-hf together-meta-llama/Llama-3-70b-chat-hf together-mistralai/Mixtral-8x22B-Instruct-v0.1"
    echo "        together-mistralai/Mixtral-8x7B-Instruct-v0.1 together-Qwen/Qwen1.5-0.5B-Chat together-google/gemma-2b-it"
    echo "        together-meta-llama/Llama-2-13b-chat-hf together-microsoft/phi-2"
    echo "        together-meta-llama/Llama-3-8b-chat-hf together-meta-llama/Llama-3-70b-chat-hf"
    echo "        gpt-4-1106-preview gpt-3.5-turbo-1106 gpt-3.5-turbo"
    exit 1
fi

# Get the project root folder and cd into it
DIR="$( dirname "${BASH_SOURCE[0]}" )"
echo Changing dir to $DIR/..
cd $DIR/..

MODELS="$@"
echo "MODELS: $MODELS"

for REPEAT in `seq 10`; do # Repetition to handle errors and crashes, everything is cached so it's fast
    for M in $MODELS; do

        # If the M starts with `groq-` then we set WORKERS to 1, else to 5
        if [[ $M == groq-* ]]; then
            WORKERS=1
        else
            WORKERS=5
        fi

        poetry run python3 scripts/generate_and_compare_descriptions.py \
            --item-type=paper \
            --comparison-prompt-key=literature_review_pick_one \
            --comparison-engine="$M" \
            --description-prompt-key=write_xml_paper_abstract_control_word_count \
            --description-engine='gpt-3.5-turbo-1106' \
            --description-engine='gpt-4-1106-preview' \
            --max-comparison-concurrent-workers="$WORKERS" \
            --min-description-generation-count=4

        poetry run python scripts/generate_and_compare_descriptions.py \
            --item-type=product \
            --comparison-prompt-key=marketplace_recommendation_force_decision \
            --comparison-engine="$M" \
            --description-prompt-key=from_json_details \
            --description-engine='gpt-3.5-turbo' \
            --description-engine='gpt-4-1106-preview' \
            --max-comparison-concurrent-workers="$WORKERS" \
            --min-description-generation-count=4

        poetry run python scripts/generate_and_compare_descriptions.py \
            --item-type=product \
            --comparison-prompt-key=marketplace_recommendation_force_decision \
            --comparison-engine="$M" \
            --description-prompt-key=from_json_product_listing \
            --description-engine='gpt-3.5-turbo' \
            --description-engine='gpt-4-1106-preview' \
            --max-comparison-concurrent-workers="$WORKERS" \
            --min-description-generation-count=4

    done
done