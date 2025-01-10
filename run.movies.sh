#!/bin/bash


WORKERS=1  # If the M starts with `groq-` then set 1 one instead

# Note: No space after the '=' and the entire list is wrapped in quotes:
# COMPARISON_MODELS="\
#   together-meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo \
#   together-mistralai/Mixtral-8x22B-Instruct-v0.1 \
#   together-Qwen/Qwen2.5-72B-Instruct-Turbo \
#   gpt-3.5-turbo \
#   gpt-4-1106-preview \
#   together-Qwen/Qwen2.5-7B-Instruct-Turbo\
# "

COMPARISON_MODELS="gpt-4-1106-preview"

echo "COMPARISON_MODELS: $COMPARISON_MODELS"

for REPEAT in `seq 1`; do # Repetition to handle errors and crashes, everything is cached so it's fast
    for M in $COMPARISON_MODELS; do
        echo "###################### Comparison Model: $M"
        
        poetry run python3 scripts/generate_and_compare_descriptions.py \
            --item-type=movie \
            --comparison-engine="$M" \
            --comparison-prompt-key=movie_pick_one \
            --description-prompt-key=from_title_and_year  \
            --min-description-generation-count=1  \
            --description-engine='gpt-4-1106-preview' \
            --max-comparison-concurrent-workers="$WORKERS" \
            --redo-invalid-results \
            --min-description-generation-count=1
    done
done

            # --description-engine='gpt-3.5-turbo' \
            # --description-engine='together-mistralai/Mixtral-8x22B-Instruct-v0.1' \
            # --description-engine='together-Qwen/Qwen2.5-7B-Instruct-Turbo' \
            # --description-engine='together-meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo' \
            # --description-engine='together-meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo' \
            # --description-engine='together-meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo' \
