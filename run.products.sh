!/bin/bash

WORKERS=1  # If the M starts with `groq-` then set 1 one instead

COMPARISON_MODELS= "together-meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo together-mistralai/Mixtral-8x22B-Instruct-v0.1 together-Qwen/Qwen2.5-72B-Instruct-Turbo gpt-3.5-turbo gpt-4-1106-preview together-Qwen/Qwen2.5-7B-Instruct-Turbo" # together-meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo # ignore 8B for now
echo "COMPARISON_MODELS: $COMPARISON_MODELS"echo "MODELS: $MODELS"

for REPEAT in `seq 1`; do # Repetition to handle errors and crashes, everything is cached so it's fast
    for M in $COMPARISON_MODELS; do

       echo "###################### Comparison Model: $M"

        poetry run python scripts/generate_and_compare_descriptions.py \
            --item-type=product \
            --comparison-prompt-key=marketplace_recommendation_force_decision \
            --comparison-engine="$M" \
            --description-prompt-key=from_json_details \
            --description-prompt-key=from_json_product_listing \
            --description-engine='together-mistralai/Mixtral-8x22B-Instruct-v0.1' \
            --description-engine='together-Qwen/Qwen2.5-7B-Instruct-Turbo' \
            --description-engine='together-meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo' \
            --max-comparison-concurrent-workers="$WORKERS" \
            --redo-invalid-results \
            --min-description-generation-count=1
    done
done