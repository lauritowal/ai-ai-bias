#!/bin/bash

WORKERS=1  # If the M starts with `groq-` then set 1 one instead

# Note: No space after the '=' and the entire list is wrapped in quotes:
COMPARISON_MODELS="\
  gpt-3.5-turbo \
"
# together-meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo \
# together-mistralai/Mixtral-8x22B-Instruct-v0.1 \
# together-Qwen/Qwen2.5-72B-Instruct-Turbo \
# gpt-4-1106-preview \
# together-Qwen/Qwen2.5-7B-Instruct-Turbo\

#  --description-engine='together-meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo' \

echo "COMPARISON_MODELS: $COMPARISON_MODELS"

for REPEAT in `seq 1`; do # Repetition to handle errors and crashes, everything is cached so it's fast
    for M in $COMPARISON_MODELS; do
        echo "###################### Comparison Model: $M"
        poetry run python3 scripts/generate_and_compare_descriptions.py \
            --item-type=paper \
            --comparison-prompt-key=literature_review_pick_one \
            --comparison-engine="$M" \
            --description-prompt-key=write_xml_paper_abstract_control_word_count \
            --description-engine='together-mistralai/Mixtral-8x22B-Instruct-v0.1' \
            --description-engine='together-meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo' \
            --max-comparison-concurrent-workers="$WORKERS" \
            --redo-invalid-results \
            --min-description-generation-count=1
    done
done

# --description-engine='together-Qwen/Qwen2.5-7B-Instruct-Turbo' \