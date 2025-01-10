#!/bin/bash

WORKERS=1  # Set to 1 if the model starts with `groq-`

COMPARISON_MODELS="\
  together-mistralai/Mixtral-8x22B-Instruct-v0.1 \
"
  # together-meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo \
  # together-mistralai/Mixtral-8x22B-Instruct-v0.1 \
  # together-Qwen/Qwen2.5-72B-Instruct-Turbo \
  # gpt-3.5-turbo \
  # gpt-4-1106-preview \
  # together-Qwen/Qwen2.5-7B-Instruct-Turbo\

DESCRIPTION_ENGINES="\
  together-meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo \
  together-mistralai/Mixtral-8x22B-Instruct-v0.1 \
  together-Qwen/Qwen2.5-72B-Instruct-Turbo \
" # do 3 at a time, then create new context cache

  # gpt-3.5-turbo \
  # gpt-4-1106-preview \
  # together-Qwen/Qwen2.5-7B-Instruct-Turbo\

# done for Mistral as comp:
#  together-Qwen/Qwen2.5-72B-Instruct-Turbo \


for REPEAT in `seq 1`; do # Repetition to handle errors and crashes; caching ensures fast retries
    for M in $COMPARISON_MODELS; do
        echo "###################### Comparison Model: $M"
        
        poetry run python3 scripts/generate_and_compare_descriptions.py \
            --item-type=proposal \
            --comparison-engine="$M" \
            --comparison-prompt-key=proposal_pick_one \
            --description-prompt-key=include_descriptions \
            --min-description-generation-count=1 \
            $(for DESC_ENGINE in $DESCRIPTION_ENGINES; do echo "--description-engine=$DESC_ENGINE"; done) \
            --max-comparison-concurrent-workers="$WORKERS" \
            --redo-invalid-results
    done
done
