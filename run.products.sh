!/bin/bash

# require at least one parameter
if [ $# -eq 0 ]; then
    echo "Usage: $0 <MODELS>"
    echo "MODELS: (see schema.py)"
    exit 1
fi

WORKERS=1  # If the M starts with `groq-` then set 1 one instead

MODELS="$@"
echo "MODELS: $MODELS"

for REPEAT in `seq 1`; do # Repetition to handle errors and crashes, everything is cached so it's fast
    for M in $MODELS; do

       echo "###################### Comparison Model: $M"

        poetry run python scripts/generate_and_compare_descriptions.py \
            --item-type=product \
            --comparison-prompt-key=marketplace_recommendation_force_decision \
            --comparison-engine="$M" \
            --description-prompt-key=from_json_details \
            --description-prompt-key=from_json_product_listing \
            --description-engine='gpt-3.5-turbo' \
            --description-engine='gpt-4-1106-preview' \
            --description-engine='together-Qwen/Qwen2.5-72B-Instruct-Turbo' \
            --max-comparison-concurrent-workers="$WORKERS" \
            --redo-invalid-results \
            --min-description-generation-count=1
    done
done