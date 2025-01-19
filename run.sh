#!/bin/bash

WORKERS=1  # If the M starts with `groq-` then set 1 one instead

COMPARISON_MODELS="\
  together-mistralai/Mixtral-8x22B-Instruct-v0.1 \
  gpt-4-1106-preview \
  together-Qwen/Qwen2.5-72B-Instruct-Turbo \
  gpt-3.5-turbo-1106 \
  together-meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo \
"

DESCRIPTION_ENGINES="
  gpt-4-1106-preview \
"

echo "COMPARISON_MODELS: $COMPARISON_MODELS"

# echo "###################### Paper"
# for M in $COMPARISON_MODELS; do
#   echo "###################### Comparison Model: $M"
#   poetry run python3 scripts/generate_and_compare_descriptions.py \
#     --item-type=paper \
#     --comparison-prompt-key=literature_review_pick_one \
#     --comparison-engine="$M" \
#     --description-prompt-key=write_xml_paper_abstract_control_word_count \
#     $(for DESC_ENGINE in $DESCRIPTION_ENGINES; do echo "--description-engine=$DESC_ENGINE"; done) \
#     --max-comparison-concurrent-workers="$WORKERS" \
#     --redo-invalid-results \
#     --min-description-generation-count=1
#   # wait for 60 sec to make sure all concurrent workers are done
#   sleep 60
#   # move to context_cache_DATE
#   mv "context_cache" "context_cache_$(date +%Y-%m-%d_%H-%M-%S)"
#   echo "###################### Done Comparison Model: $M"
# done

echo "###################### Product"

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
  # wait for 60 sec to make sure all concurrent workers are done
  sleep 60
  # move to context_cache_DATE
  mv "context_cache" "context_cache_$(date +%Y-%m-%d_%H-%M-%S).bak"
  echo "###################### Done Comparison Model: $M"
done