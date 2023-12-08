# ai-ai-bias

## What scripts to run?

### Generate more human-written source data

See "Human written source data" in the data section, which points to example scripts.

### Just generate more LLM descriptions

Use this script: https://github.com/lauritowal/ai-ai-bias/blob/main/scripts/generate_llm_descriptions.py

Ex: Creates/confirms 6 generated descriptions for the "from_json_details" prompt using GPT-4-turbo for every item in the "product" item type
```
python scripts/generate_llm_descriptions.py \
    --item-type=product \
    --prompt-nickname=from_json_details \
    --engine=gpt-4-1106-preview \
    --target-count=6
```

Ex: Same as above but limited to product items with titles/filenames containing the string "avapow" or "cooking"

```
python scripts/generate_llm_descriptions.py \
    --item-type=product \
    --prompt-nickname=from_json_details \
    --engine=gpt-4-1106-preview \
    --target-count=6 \
    --item-title-like=avapow \
    --item-title-like=cooking
```

NOTE: `target-count` indicates the minimum number of LLM-generated descriptions for that specific item_type+prompt+engine that the script will make sure exist for each item of the type.

IMPORTANT: results from LLM queries are written to the cache files after every successful query, and the script checks for how many descriptions in the cache match the criteria before making new LLM queries, so if the script needs to be cancelled or crashes, running again will pick up where the first run left off.


### Just run comparisons

Use this script: https://github.com/lauritowal/ai-ai-bias/blob/main/scripts/run_comparisons.py

Ex: Run comparisons using GPT-4-turbo and the "marketplace" prompt key in the [comparison prompt config](https://github.com/lauritowal/ai-ai-bias/blob/main/src/llm_comparison/config.py) between every human description and (existing) LLM description that was generated with GPT-3.5-turbo and the "from_json_details" prompt key in the [description prompt config](https://github.com/lauritowal/ai-ai-bias/blob/main/src/llm_descriptions_generator/config.py) for every item in the "product" category where the title/filename contains the string "avapow" or "stainless":
```
python scripts/run_comparisons.py \
    --item-type=product \
    --comparison-prompt-key=marketplace \
    --comparison-engine='gpt-4-1106-preview' \
    --description-prompt-key=from_json_details \
    --description-engine='gpt-3.5-turbo' \
    --item-title-like=avapow \
    --item-title-like=stainless
```

NOTE: `item-title-like` filter is optional -- if not provided, the script will run comparisons for all items in the item_type instead.

IMPORTANT: results from LLM queries are written to the Context cache after every successful query, and the script checks for how many descriptions in the cache match the criteria before making new LLM queries, so if the script needs to be cancelled or crashes, running again will pick up where the first run left off.


### Full combo: Generate LLM descriptions AND run comparisons

Use this script: https://github.com/lauritowal/ai-ai-bias/blob/main/scripts/generate_and_compare_descriptions.py

Basically just combines the description generation and comparison scripts above, and adds a final display of average results and bar charts.

Ex: For all items with human descriptions in the "product" item_type category containing the strings "avapow" or "stainless", make sure that at least 6 LLM versions exist in the cache that were generated with GPT-3.5.-turbo using the "from_json_details" [description prompt](https://github.com/lauritowal/ai-ai-bias/blob/main/src/llm_descriptions_generator/config.py), and then run comparisons between those LLM descriptions and the human ones using GPT-4-turbo and the "marketplace" [comparison prompt](https://github.com/lauritowal/ai-ai-bias/blob/main/src/llm_comparison/config.py)

```
python scripts/generate_and_compare_descriptions.py \
    --item-type=product \
    --comparison-prompt-key=marketplace \
    --comparison-engine='gpt-4-1106-preview' \
    --description-prompt-key=from_json_details \
    --description-engine='gpt-3.5-turbo' \
    --item-title-like=avapow \
    --item-title-like=stainless \
    --min-description-generation-count=6
```

Note: *At time of last docs update (2023-12-02)* this script is the only one that **also generates final charts and averages**.

Note: Like `item-title-like`, the `comparison-prompt-key`, `comparison-description-engine`, `description-prompt-key`, and `description-engine` CLI args for this script can take multiple values. IF any of the above are given multiple values, the script will run using all possible permutations of those inputs in sequence.

Ex: Do a massive run that iterates through every item in the "product" category and generates/confirms LLM descriptions (at least 10 per item) and does comparisons against human text for both the "from_json_details" and "short_and_pointed" description prompts AND both the "marketplace" and "seller" comparison prompts, across all combinations of using GPT 3.5 and 4 turbo for either query role.

```
python scripts/generate_and_compare_descriptions.py \
    --item-type=product \
    --comparison-prompt-key=marketplace \
    --comparison-prompt-key=seller \
    --comparison-engine='gpt-3.5-turbo' \
    --comparison-engine='gpt-4-1106-preview' \
    --description-prompt-key=from_json_details \
    --description-prompt-key=short_and_pointed \
    --description-engine='gpt-3.5-turbo' \
    --description-engine='gpt-4-1106-preview' \
    --min-description-generation-count=10
```

NOTE/WARNING: The query above has 2^4 permutations, so it's like running a single version 16 times. Expect it to easily take 24 hours and probably exceed your openai API quota.

On the other hand, the pile of data it will generate at the end is probably what we ultimately want, so if we can build up the caches to the point that this could run in <30 mins, the final output should be great.


### Special case: Generate JSON summaries (for products)

NOTE: for now, this feature only applies to the "product" item_type.

Some description generation prompts, e.g. the `from_json_details` [prompt](https://github.com/lauritowal/ai-ai-bias/blob/dffb6f67716fbd404bbdd350f132b9654697aea6/src/llm_descriptions_generator/config.py#L38), draw from a special json representation of the item features pulled from the original human descriptions.

Reasoning: To lessen the effects on comparisons by noise like having different feature sets (e.g. if the LLM invents new features the human original doesn't have, or misses features the human original does have). Early versions had the LLM generate new descriptions based off just the title (problem with feature disparity) or off the entire human description, but we don't want the LLM to be influenced by the prose in the human version, hence baking the core data down to json as a prior step.

NOTE: We use specifically GPT-4-Turbo for this, since it seems to be reliably better than GPT-3-Turbo, and in this case we just need a solid capturing of the details.

To create additional JSON summaries, run the following command:

```
python scripts/generate_llm_descriptions.py \
    --item-type=product \
    --prompt-nickname=jsonify_key_details \
    --engine='gpt-4-1106-preview' \
    --target-count=3
```

To add new description-generation prompts that use the json summaries, make sure to use the `description_source=PromptDescriptionSource.LLM_JSON_Summary` and `include_descriptions=True` flags (see [from_json_details](https://github.com/lauritowal/ai-ai-bias/blob/8e6c2241300778ed662d0021e276c95255ef1d8e/src/llm_descriptions_generator/config.py#L38-L44) prompt for example)..


### NOTE: Future special cases?

## Where is the data? (inputs & caches)

### Human written source data

*At time of last docs update (2023-12-02):*

Human descriptions are stored in any `/data/<item_type>/human/<item_name>.json` folder in json format like:

```
{
    "item_type": str,
    "title": str,
    "descriptions": list[str], # usually only one for human data
    "origin": "Human"
}
```

NOTE: Please use the `to_safe_filename` function (see `src/llm_descriptions_generator/file_io.py`) to generate filenames.

Some examples of small scripts generating these json files from other data forms (doesn't matter how they are generated as long as the json shape and file path/name have the same pattern):
- https://github.com/lauritowal/ai-ai-bias/blob/main/scripts/convert_human_toml_to_json.py
- https://github.com/lauritowal/scrapper/blob/main/format_products_as_ai_bias_human_description.py 


### Cached LLM-generated data

Queries against OpenAI/etc are pretty slow (and sometimes have a non-trivial failure rate), and we need to do a pretty large volume of them, so we ended up implementing some caching mechanisms to store past results of queries with identical inputs.

NOTE: it's possible to wipe or relocate the caches and do a completely fresh run if desired.

#### LLM-generated descriptions cache

*At time of last docs update (2023-12-02):*

Looking back, not sure if it was a good idea, or necessary given the possibility of the Context-caching solution used for the comparisons (see below), but early on in the project we used a custom json pattern (based off the human description pattern with some extra metadata) to cache results of LLM-generated descriptions.

These can be found at `/data/<item_type>/<llm_model>/<item_name>-<prompt_key>.json`

NOTE: the `<prompt_key>` in the file name is the `prompt_nickname` specified in the LLM description generator config here https://github.com/lauritowal/ai-ai-bias/blob/main/src/llm_descriptions_generator/config.py


#### LLM comparisons of descriptions

We use interlab's native `Context` stack for caching the comparison requests, with `tags` attribute, applying custom tags for LLM engine and prompt key used for comparison, and UIDs for the descriptions compared. (May have been able to use `inputs` in retrospect, but whatever.) Description UIDs are generated by doing an MD5 hash on the entire description.

NOTE: this does require committing the entire past context stack to source control (see `/context_cache`)

The goal is allowing an option for quickly pulling the results of a recent comparison of the same inputs by a specific LLM instead of asking for a new comparison.

See [somewhat hacky implementation here](https://github.com/lauritowal/ai-ai-bias/blob/dffb6f67716fbd404bbdd350f132b9654697aea6/src/llm_comparison/llm_comparison.py#L98). Can be expanded with more options if needed (e.g. a time filter or explicit run key).


#### Retro on custom json cache vs interlab Context

Custom JSON:
- cached results are easily reusable
- json files are easily and quickly legible (without running any context display server) if a human wants to check the kind of descriptions the LLM is generating
- upfront cost in custom code
- requires solidly defined schema

Interlab context:
- Usable with very little additional code (just custom use of `storage.find_contexts`), though upfront learning curve on Context system is a little steep
- Context files are relatively heavy and with a lot of redundant and/or extraneous information.
- Searching context files is relatively slow and gets slower the larger the cache grows.

### Final run results
Full run results can be found in `/full_run_outputs/`. JSON files contain the raw data summaries with the HTML doing some limited presentation.

Runs may have an additional JSON file that selects a random distribution of human+LLM text comparisons that occurred during the run for potential human review.