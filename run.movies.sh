#!/bin/bash


WORKERS=1  # If the M starts with `groq-` then set 1 one instead

COMPARISON_MODELS="\
  together-mistralai/Mixtral-8x22B-Instruct-v0.1 \
  gpt-4-1106-preview \
  gpt-3.5-turbo
"


DESCRIPTION_ENGINES="
  gpt-4-1106-preview \
"

echo "COMPARISON_MODELS: $COMPARISON_MODELS"

for M in $COMPARISON_MODELS; do
    echo "###################### Comparison Model: $M"
    
    poetry run python3 scripts/generate_and_compare_descriptions.py \
        --item-type=movie \
        --comparison-engine=$M \
        --comparison-prompt-key=movie_pick_one \
        --description-prompt-key=from_title_and_year  \
        $(for DESC_ENGINE in $DESCRIPTION_ENGINES; do echo "--description-engine=$DESC_ENGINE"; done) \
        --min-description-generation-count=1  \
        --max-comparison-concurrent-workers="$WORKERS" \
        --redo-invalid-results \
        --min-description-generation-count=1
    
    # wait for 60 sec to make sure all concurrent workers are done
    sleep 60
    # move to context_cache_DATE
    mv "context_cache" "context_cache_$(date +%Y-%m-%d_%H-%M-%S)"
    echo "###################### Done Comparison Model: $M"
done