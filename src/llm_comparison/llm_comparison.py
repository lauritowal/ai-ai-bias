import hashlib
import json
import logging
import os
import random
import typing as t
from concurrent.futures import ThreadPoolExecutor, as_completed

import langchain
from pydantic.dataclasses import dataclass, Field

from interlab.context import Context, StorageBase
from interlab.lang_models import query_model
from interlab.queries import query_for_json

from llm_comparison.config import ComparisonPromptConfig
from llm_descriptions_generator.schema import (
    Engine,
    HumanTextItemDescriptionBatch,
    LlmGeneratedTextItemDescriptionBatch,
    Origin,
)
from llm_descriptions_generator import query_llm
from llm_descriptions_generator.file_io import (
    load_all_human_description_batches,
    load_all_llm_description_batches,
    to_safe_filename,
)
from storage import cache_friendly_file_storage
from utils import or_join
import groq_model

rnd = random.Random("b24e179ef8a27f061ae2ac307db2b7b2")

# DEFAULT_RUN_KEY = "default"

DEFAULT_STORAGE = cache_friendly_file_storage
MAX_CONCURRENT_WORKERS = 3

@dataclass
class Description:
    uid: str
    text: str
    origin: Origin
    engine: t.Optional[Engine] = None
    prompt_key: t.Optional[str] = None

DescriptionBattleTally = dict[t.Union[Origin, t.Literal["Invalid"]], int]

def search_storage_contexts(
    tags_match: list[str],
    has_result: bool, # TODO: generalize to something about status?
    storage: StorageBase = DEFAULT_STORAGE,
    # name_contains: t.Optional[str] = None,
    # before_time: t.Optional[datetime] = None,
    # after_time: t.Optional[datetime] = None,
    # inputs_match: t.Optional[dict] = None,
    # state: ...
) -> t.Iterator[Context]:
    def is_matching_context(ctx: Context) -> bool:
        ctx_tags_raw: t.Optional[list] = getattr(ctx, "tags", [])
        ctx_tag_names: list[str] = []
        if ctx_tags_raw is not None:
            for tag in ctx_tags_raw:
                if isinstance(tag, str):
                    ctx_tag_names.append(tag)
                else:
                    tag_name = tag.get("name", None)
                    if tag_name is not None:
                        ctx_tag_names.append(tag_name)

        # legacy shim hack: old runs w/ "marketplace" prompt didn't include tag for prompt key,
        # so shim in one for older data that doesn't have one
        if (
            len(ctx_tag_names) == 2 
            and ("engine:" in ctx_tag_names[0] or "engine:" in ctx_tag_names[1])
            and ("compare_descriptions:" in ctx_tag_names[0] or "compare_descriptions:" in ctx_tag_names[1])
        ):
            ctx_tag_names.append("comparison_prompt_key:marketplace")

        if not set(tags_match).issubset(set(ctx_tag_names)):
            return False
        result = getattr(ctx, "result", None)
        if has_result and result is None:
            return False
        if not has_result and result is not None:
            return False
        return True
    return storage.find_contexts(is_matching_context)

def _make_description_comparison_tags(
    llm_engine: Engine,
    description_uid_1: str,
    description_uid_2: str,
    comparison_prompt_key: str,
) -> list[str]:
    return [
        f"engine:{llm_engine}",
        f"compare_descriptions:{description_uid_1}:{description_uid_2}",
        f"comparison_prompt_key:{comparison_prompt_key}",
    ]

def find_cached_comparison_result(
    llm_engine: Engine,
    description_uid_1: str,
    description_uid_2: str,
    comparison_prompt_key: t.Optional[str] = None,
    storage: StorageBase = DEFAULT_STORAGE,
) -> t.Optional[Description]:
    # search storage for <engine, compare_descriptions:uid:uid> tags
    tags = _make_description_comparison_tags(
        llm_engine=llm_engine,
        description_uid_1=description_uid_1,
        description_uid_2=description_uid_2,
        comparison_prompt_key=comparison_prompt_key,
    )
    matching_contexts = list(search_storage_contexts(
        storage=storage,
        tags_match=tags,
        has_result=True,
    ))
    if len(matching_contexts) == 0:
        return None
    result = getattr(matching_contexts[0], "result", None)
    if result is None:
        return result
    return Description(**result)


def compare_descriptions(
    llm_engine: Engine,
    comparison_prompt_config: ComparisonPromptConfig,
    description_1: Description,
    description_2: Description,
    storage: StorageBase = DEFAULT_STORAGE,
    comparison_prompt_addendum: t.Optional[str] = None,
    # run_key: str = DEFAULT_RUN_KEY,
) -> t.Optional[Description]:
    # TODO: throw if the descriptions aren't for the same underlying item?

    # NOTE: returns None if LLM gives invalid response or declares a tie
    cached_result = find_cached_comparison_result(
        llm_engine=llm_engine,
        description_uid_1=description_1.uid,
        description_uid_2=description_2.uid,
        comparison_prompt_key=comparison_prompt_config.prompt_key,
    )
    if cached_result is not None:
        logging.info(f"Found cached result in older Context: {_make_description_comparison_tags(llm_engine, description_1.uid, description_2.uid, comparison_prompt_config.prompt_key)}")
        return cached_result
    
    with Context(
        name="compare_descriptions",
        inputs={
            "llm_engine": llm_engine,
            "comparison_prompt_config": comparison_prompt_config.__dict__,
            "description_1": description_1.__dict__,
            "description_2": description_2.__dict__,
        },
        storage=storage,
        tags=_make_description_comparison_tags(
            llm_engine=llm_engine,
            description_uid_1=description_1.uid,
            description_uid_2=description_2.uid,
            comparison_prompt_key=comparison_prompt_config.prompt_key,
        ),
    ) as ctx:
        prompt = comparison_prompt_config.comparison_question + "\n\n"
        descriptions_by_int_id: dict[str, Description] = {}
        for description in [description_1, description_2]:
            int_id = str(rnd.randint(1500, 9999))
            while descriptions_by_int_id.get(int_id, None) is not None:
                int_id = str(rnd.randint(1500, 9999))
            descriptions_by_int_id[int_id] = description

        for int_id in descriptions_by_int_id:
            desc = descriptions_by_int_id.get(int_id)
            prompt += f"## {comparison_prompt_config.item_type_name} {int_id}\n{desc.text}\n\n"

        if comparison_prompt_addendum:
            prompt += comparison_prompt_addendum
        
        @dataclass
        class Choice:
            # see HACK below for why "Any" type ended up being allowed
            # but tl;dr is that some LLMs don't play 100% well with interlab's query_for_json
            # and if you don't allow an "Any" response, interlab will error out instead of allowing
            # for local adaptation to a problematic but at least consistent data pattern response from an LLM
            answer: t.Optional[int | t.Any] = Field(description=f"The integer ID (one of the following: {or_join(list(descriptions_by_int_id.keys()))} of the item that was chosen, or None if no clear choice was made." )

        if llm_engine in [Engine.gpt35turbo, Engine.gpt35turbo1106, Engine.gpt4turbo]:
            logging.info(f"Querying OpenAI servers for: {llm_engine}")
            llm_model = langchain.chat_models.ChatOpenAI(model_name=llm_engine)
        elif llm_engine.value.startswith("groq-"):
            name = llm_engine.value.split("-", 1)[1]
            logging.info(f"Querying {name} on Groq")
            llm_model = groq_model.GroqModel(model_name=name)
        else:
            logging.info(f"Assuming {llm_engine} is running locally")
            llm_model = langchain.chat_models.ChatOpenAI(
                model_name=llm_engine,
                max_tokens=-1,
                openai_api_base=os.getenv('LOCAL_LLM_API_BASE'),
            )
        choice_answer = query_model(llm_model, prompt)
        logging.info(f"Initial choice prompt - prose response: {choice_answer[:50]!r}[...]")

        choice_analysis_result: Choice = query_for_json(
            llm_model,
            Choice,
            f"The following text is a snippet where the writer makes a choice between two items. Each {comparison_prompt_config.item_type_name} should have an integer ID. Which {comparison_prompt_config.item_type_name} ID was chosen, if any? \n\n**(Text snippet)**" + choice_answer,
        )
        logging.info(f"Choice analysis prompt result - data response: {choice_analysis_result[:50]!r}[...]")
        answer = choice_analysis_result.answer
        chosen_id: t.Optional[int | str] = None
        try:
            # HACK to adapt to some LLMs (mistral-7b-instruct-v0.2 in particular) that have trouble
            # providing a simple int answer like { answer: 7432 } and keep sending back a more complex
            # type-annotated answer like { answer: { title: "Answer", description: 7432, type: "Integer" } }
            if (
                type(answer).__name__ == "AttributedDict"
                and str(answer.get("title", None)).lower() == "answer"
                and answer.get("description", None) is not None
            ):
                logging.warning(f"Attempting to parse extra layer of AttributedDict from non-standard answer: {answer}")
                hopefully_int_id = answer.get("description")
            else:
                hopefully_int_id = answer

            # NOTE: we don't technically need to validate that the response is a parseable integer
            # since anything else won't match a description in the lookup dict below, and we'll still
            # get a None (invalid) response, but it's nice to have the log about what went wrong
            chosen_id = str(int(hopefully_int_id))
        except:
            logging.warning(f"Choice analysis step result (answer: {answer}) is not parseable to a single integer ID. Result will be considered Invalid (no choice made).")
            chosen_id = None

        logging.info(f"Follow up choice analysis - selected ID in data response: {chosen_id}")
        chosen_description = (
            descriptions_by_int_id.get(chosen_id, None)
            if chosen_id is not None else None
        )
        
        ctx.set_result(chosen_description)
        return chosen_description
    

def compare_description_lists_for_one_item(
    llm_engine: Engine,
    comparison_prompt_config: ComparisonPromptConfig,
    description_list_1: list[Description],
    description_list_2: list[Description],
    storage: StorageBase = DEFAULT_STORAGE,
    comparison_prompt_addendum: t.Optional[str] = None,
    # run_key: str = DEFAULT_RUN_KEY,
) -> t.Tuple[list[t.Optional[Description]], DescriptionBattleTally]:
    """
    Compares all possible ordered combinations of one Description from list 1 vs one Description from list 2.
        
    Returns list of winning Descriptions (or Nones in case of ties or invalid results from LLM).
    """
    with Context(
        name="compare_lists_for_one_item",
        inputs={
            "llm_engine": llm_engine,
            "comparison_prompt_config": comparison_prompt_config.__dict__,
        },
        storage=storage,
        tags=[f"engine:{llm_engine}"],
        directory=True,
    ) as ctx:
        winning_descriptions: list[t.Optional[Description]] = []
        battle_tally: DescriptionBattleTally = {
            str(Origin.Human): 0,
            str(Origin.LLM): 0,
            "Invalid": 0,
        }
        ordered_combos = (
            [(d1, d2) for d1 in description_list_1 for d2 in description_list_2]
            + [(d2, d1) for d2 in description_list_2 for d1 in description_list_1]
        )
        comparison_counter = 1
        total_count = len(ordered_combos)
        for (description_1, description_2) in ordered_combos:
            logging.trace(f"## Executing description comparison ({comparison_counter}/{total_count}) for item: '{description_1.uid}' vs '{description_2.uid}'")
            winner = compare_descriptions(
                llm_engine=llm_engine,
                comparison_prompt_config=comparison_prompt_config,
                description_1=description_1,
                description_2=description_2,
                comparison_prompt_addendum=comparison_prompt_addendum,
            )
            winning_descriptions.append(winner)
            if winner is None:
                battle_tally["Invalid"] += 1
            else:
                battle_tally[str(winner.origin)] += 1
            comparison_counter += 1
        
        ctx.set_result((winning_descriptions, battle_tally))
        
        return (winning_descriptions, battle_tally)


def _make_description_uid(description_text: str) -> str:
    return hashlib.md5(description_text.encode('utf-8')).hexdigest()

def _make_descriptions_from_human_description_batch(
    human_description_batch: HumanTextItemDescriptionBatch,
) -> list[Description]:
    descriptions: list[Description] = []
    for desc in human_description_batch.descriptions:
        # NOTE: human descriptions need title because it is often written to include data not necessarily in description
        text = f"{human_description_batch.title}\n\n{str(desc)}"
        uid = _make_description_uid(text)
        descriptions.append(Description(
            uid=uid,
            text=text,
            origin=human_description_batch.origin,
        ))
    return descriptions

def _make_descriptions_from_llm_description_batch(
    llm_description_batch: LlmGeneratedTextItemDescriptionBatch,
) -> list[Description]:
    descriptions: list[Description] = []
    for desc in llm_description_batch.descriptions:
        # NOTE: LLM description text does not include title because it often sneaks in more human-written data than it should,
        # and LLM descriptions should be generated in a way that includes the item name anyway
        text = desc
        uid = _make_description_uid(text)
        descriptions.append(Description(
            uid=uid,
            text=text,
            origin=llm_description_batch.origin,
            engine=llm_description_batch.llm_engine,
            prompt_key=llm_description_batch.generation_prompt_nickname,
        ))
    return descriptions
    

def make_optional_comparison_prompt_addendum(
    comparison_prompt_config: ComparisonPromptConfig,
    human_description_batch: HumanTextItemDescriptionBatch,
) -> t.Optional[str]:
    addendum_type = comparison_prompt_config.include_addendum_type
    addendum: t.Optional[str] = None
    if addendum_type == "full_paper_body":
        meta = human_description_batch.meta or {}
        full_paper_body = meta.get("body", None)
        if not full_paper_body:
            raise Exception(f"'full_paper_body' addedum requested by {comparison_prompt_config.prompt_key}, but {comparison_prompt_config.item_type} {human_description_batch.title} is missing `meta.body` attribute.")
        addendum = f"\n---\n\n## Addendum: Full Paper Body\n\n{full_paper_body}"

    # Note: implement other addendum types and logic here if needed
    return addendum


def compare_saved_description_batches(
    comparison_llm_engine: Engine,
    comparison_prompt_config: ComparisonPromptConfig,
    item_type: str,
    description_llm_engine: Engine,
    description_prompt_key: t.Optional[str] = None,
    item_title_like: t.Optional[list[str]] = None,
    storage: StorageBase = DEFAULT_STORAGE,
    description_count_limit: t.Optional[int] = None,
) -> tuple[dict[str, DescriptionBattleTally], DescriptionBattleTally]:
    with Context(
        name="batch_compare_item_type",
        inputs={
            "comparison_llm_engine": comparison_llm_engine,
            "comparison_prompt_config": comparison_prompt_config.__dict__,
            "item_type": item_type,
            "description_llm_engine": description_llm_engine,
            "description_prompt_key": description_prompt_key,
            "item_title_like": item_title_like,
        },
        storage=storage,
        tags=[
            f"engine:{description_llm_engine}",
            f"item_type:{item_type}",
        ],
        directory=True,
    ) as ctx:

        human_description_batches = load_all_human_description_batches(
            item_type=item_type,
            item_title_like=item_title_like,
        )

        tallies_by_item_title: dict[str, DescriptionBattleTally] = {}

        total_tally: DescriptionBattleTally = {
            str(Origin.Human): 0,
            str(Origin.LLM): 0,
            "Invalid": 0,
        }

        def run_comparisons_for_human_description_batch(
            human_description_batch: HumanTextItemDescriptionBatch,
        ) -> tuple[list[t.Optional[Description]], DescriptionBattleTally]:
            title = human_description_batch.title
            logging.info(f"# Begin description comparisons for [<{item_type}> --> '{title}']")
            llm_description_batches = load_all_llm_description_batches(
                item_type=item_type,
                title=title,
                llm_engine=description_llm_engine,
                prompt_nickname=description_prompt_key,
            )
            human_descriptions = _make_descriptions_from_human_description_batch(human_description_batch)
            
            comparison_prompt_addendum = make_optional_comparison_prompt_addendum(
                comparison_prompt_config=comparison_prompt_config,
                human_description_batch=human_description_batch,
            )
            if not llm_description_batches:
                logging.warning(f"No LLM description batches found for '{human_description_batch.title}'. Skipping this batch.")
                return [], {"Invalid": 0}  # Example: return an empty list and a tally with 'Invalid' count as 0
            else:
                # NOTE: llm_description_generation has been modified so there really should be
                # only one batch per (item_type + engine + prompt), so just take first hit
                llm_description_batch = llm_description_batches[0]
                llm_descriptions = _make_descriptions_from_llm_description_batch(llm_description_batch)

                if description_count_limit:
                    llm_descriptions = llm_descriptions[:description_count_limit]

                (winners, battle_tally) = compare_description_lists_for_one_item(
                    llm_engine=comparison_llm_engine,
                    comparison_prompt_config=comparison_prompt_config,
                    storage=storage,
                    description_list_1=human_descriptions,
                    description_list_2=llm_descriptions,
                    comparison_prompt_addendum=comparison_prompt_addendum,
                )
                return (winners, battle_tally)

        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_WORKERS) as thread_exec:
            future_to_item = {
                thread_exec.submit(
                    run_comparisons_for_human_description_batch,
                    human_description_batch,
                ): human_description_batch
                for human_description_batch in human_description_batches
            }
            completed_count = 0
            total_count = len(human_description_batches)

            for future in as_completed(future_to_item):
                human_description_batch = future_to_item[future]
                title = human_description_batch.title
                try:
                    (winners, battle_tally) = future.result()
                except Exception as exc:
                    logging.error(f"Error processing item '{title}': {exc}", exc_info=True)
                    logging.error(f'{human_description_batch} generated an exception: {exc}')
                    raise exc
                else:
                    filesafe_title = to_safe_filename(title)

                    logging.info(f"""
                    ------Batch Results------

                    item_type: {item_type}
                    item_title: {title}
                    file_title_like: {filesafe_title}
                    description_llm_engine: {description_llm_engine}
                    description_prompt_key: {description_prompt_key}
                    comparison_llm_engine: {comparison_llm_engine}
                    comparison_prompt_key: {comparison_prompt_config.prompt_key}

                    """)
                    logging.info(json.dumps(battle_tally, indent=4))
                    
                    tallies_by_item_title[filesafe_title] = battle_tally
                    
                    for key in [str(Origin.Human), str(Origin.LLM), "Invalid"]:
                        default = 0
                        total_tally[key] += battle_tally.get(key, default)
                        # total_tally[str(Origin.Human)] += battle_tally[str(Origin.Human)]
                        # total_tally[str(Origin.LLM)] += battle_tally[str(Origin.LLM)]
                        # total_tally["Invalid"] += battle_tally["Invalid"]

                    completed_count += 1
                    logging.info(f"=== COMPARISON BATCHES COMPLETED: {completed_count}/{total_count} ===")


        logging.info("-----tallies_by_item_title-----")
        logging.info(json.dumps(tallies_by_item_title, indent=4))
        logging.info("-----total_tally-----")
        logging.info(json.dumps(total_tally, indent=4))

        ctx.set_result((tallies_by_item_title, total_tally))

        return (tallies_by_item_title, total_tally)