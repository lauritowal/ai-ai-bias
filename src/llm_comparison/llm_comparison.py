import hashlib
import json
import logging
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
from llm_descriptions_generator.file_io import (
    load_all_human_description_batches,
    load_all_llm_description_batches,
    to_safe_filename,
)
from storage import cache_friendly_file_storage
from utils import or_join

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
        logging.info(f"--Found cached result-- {_make_description_comparison_tags(llm_engine, description_1.uid, description_2.uid, comparison_prompt_config.prompt_key)}")
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
        
        @dataclass
        class Choice:
            # answer: int = Field(description="One of the following integers: " + or_join(list(descriptions_by_int_id.keys()))) 
            answer: t.Optional[int] = Field(description=f"The integer ID (one of the following: {or_join(list(descriptions_by_int_id.keys()))} of the item that was chosen, or None if no clear choice was made." )

        llm_model = langchain.chat_models.ChatOpenAI(model_name=llm_engine)
        choice_answer = query_model(llm_model, prompt)
        int_id_result: Choice = query_for_json(
            llm_model,
            Choice,
            f"The following text is a snippet where the writer makes a choice between two items. Each {comparison_prompt_config.item_type_name} should have an integer ID. Which {comparison_prompt_config.item_type_name} ID was chosen, if any? \n\n**(Text snippet)**" + choice_answer,
        )
        chosen_int_id = str(int_id_result.answer)
        chosen_description = (
            descriptions_by_int_id.get(chosen_int_id, None)
            if int_id_result is not None else None
        )
        
        ctx.set_result(chosen_description)
        return chosen_description
    

def compare_description_lists_for_one_item(
    llm_engine: Engine,
    comparison_prompt_config: ComparisonPromptConfig,
    description_list_1: list[Description],
    description_list_2: list[Description],
    storage: StorageBase = DEFAULT_STORAGE,
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
        for (description_1, description_2) in ordered_combos:
            winner = compare_descriptions(
                llm_engine=llm_engine,
                comparison_prompt_config=comparison_prompt_config,
                description_1=description_1,
                description_2=description_2,
            )
            winning_descriptions.append(winner)
            if winner is None:
                battle_tally["Invalid"] += 1
            else:
                battle_tally[str(winner.origin)] += 1
        
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
    

def compare_saved_description_batches(
    comparison_llm_engine: Engine,
    comparison_prompt_config: ComparisonPromptConfig,
    item_type: str,
    description_llm_engine: Engine,
    description_prompt_key: t.Optional[str] = None,
    item_title_like: t.Optional[list[str]] = None,
    storage: StorageBase = DEFAULT_STORAGE,
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
            logging.info(f"Starting next <{item_type}> --> '{title}'")
            llm_description_batches = load_all_llm_description_batches(
                item_type=item_type,
                title=title,
                llm_engine=description_llm_engine,
                prompt_nickname=description_prompt_key,
            )
            human_descriptions = _make_descriptions_from_human_description_batch(human_description_batch)
            
            # NOTE: llm_description_generation has been modified so there really should be
            # only one batch per (item_type + engine + prompt), so just take first hit
            llm_description_batch = llm_description_batches[0]

            llm_descriptions = _make_descriptions_from_llm_description_batch(llm_description_batch)

            (winners, battle_tally) = compare_description_lists_for_one_item(
                llm_engine=comparison_llm_engine,
                comparison_prompt_config=comparison_prompt_config,
                storage=storage,
                description_list_1=human_descriptions,
                description_list_2=llm_descriptions
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

            for future in as_completed(future_to_item):
                human_description_batch = future_to_item[future]
                title = human_description_batch.title
                try:
                    (winners, battle_tally) = future.result()
                except Exception as exc:
                    logging.error(f'{human_description_batch} generated an exception: {exc}')
                else:
                    filesafe_title = to_safe_filename(title)

                    print(f"""
                    ------Batch Results------

                    item_type: {item_type}
                    item_title: {title}
                    file_title_like: {filesafe_title}
                    description_llm_engine: {description_llm_engine}
                    description_prompt_key: {description_prompt_key}
                    comparison_llm_engine: {comparison_llm_engine}
                    comparison_prompt_key: {comparison_prompt_config.prompt_key}

                        """)
                    print(json.dumps(battle_tally, indent=4))
                    # print(json.dumps(winners, indent=4))

                    tallies_by_item_title[filesafe_title] = battle_tally

                    total_tally[str(Origin.Human)] += battle_tally[str(Origin.Human)]
                    total_tally[str(Origin.LLM)] += battle_tally[str(Origin.LLM)]
                    total_tally["Invalid"] += battle_tally["Invalid"]


        print("-----tallies_by_item_title-----")
        print(json.dumps(tallies_by_item_title, indent=4))
        print("-----total_tally-----")
        print(json.dumps(total_tally, indent=4))

        ctx.set_result((tallies_by_item_title, total_tally))

        return (tallies_by_item_title, total_tally)