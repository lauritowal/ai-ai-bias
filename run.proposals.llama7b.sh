#!/bin/bash

WORKERS=1  # Set to 1 if the model starts with `groq-`

COMPARISON_MODELS="\
  together-meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo \
"

DESCRIPTION_ENGINES="\
  together-meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo \
  together-mistralai/Mixtral-8x22B-Instruct-v0.1 \
  together-Qwen/Qwen2.5-7B-Instruct-Turbo \
"

for REPEAT in `seq 1`; do # Repetition to handle errors and crashes; caching ensures fast retries
    for M in $COMPARISON_MODELS; do
        echo "###################### Comparison Model: $M"
        
        poetry run python3 scripts/generate_and_compare_descriptions.py \
            --item-type=proposal \
            --comparison-engine="$M" \
            --comparison-prompt-key=proposal_pick_one \
            --description-prompt-key=from_json_details \
            --min-description-generation-count=1 \
            $(for DESC_ENGINE in $DESCRIPTION_ENGINES; do echo "--description-engine='$DESC_ENGINE'"; done) \
            --max-comparison-concurrent-workers="$WORKERS" \
            --redo-invalid-results
    done
done
