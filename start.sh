# python scripts/generate_llm_descriptions.py \
#     --item-type=proposal \
#     --prompt-nickname=jsonify_key_details_proposal \
#     --engine='gpt-4-1106-preview' \
#     --target-count=1

# python scripts/generate_llm_descriptions.py \
#     --item-type=proposal \
#     --prompt-nickname=from_json_details \
#     --engine='gpt-4-1106-preview' \
#     --target-count=1


# TODO: NEXT
python3 scripts/generate_and_compare_descriptions.py \
    --item-type=proposal \
    --comparison-prompt-key=proposal_pick_one \
    --comparison-engine='gpt-4-1106-preview' \
    --description-prompt-key=from_json_details \
    --description-engine='gpt-4-1106-preview' \
    --min-description-generation-count=4