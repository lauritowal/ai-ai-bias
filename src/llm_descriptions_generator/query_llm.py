import json
import logging
import os
import time
import typing as t

import langchain
from interlab.context import Context, FileStorage
from interlab.lang_models import query_model
from interlab.queries import QueryFailure, query_for_json
from interlab.queries.experimental.repeat import repeat_on_failure
from openai.error import (
    APIError,
    Timeout,
    APIConnectionError,
    RateLimitError,
)

from llm_descriptions_generator.schema import (
    ProductDetailsJson,
    Engine,
    LlmGeneratedTextItemDescriptionBatch,
    TextItemGenerationPrompt,
    Origin,
)

MAX_SUPER_RETRY_COUNT = 10
SUPER_RETRY_WAIT_INTERVAL_SECONDS = 60



# @with_context(
#     name="generate_many_descriptions",
#     storage=DEFAULT_STORAGE,
#     directory=True,
# )
def generate_llm_descriptions(
    generation_prompt: TextItemGenerationPrompt,
    description_count: int,
    llm_engine: Engine,
    output_description_type: t.Optional[t.Any] = None,
) -> LlmGeneratedTextItemDescriptionBatch:
    logging.info(
        "Querying LLM for new description for prompt uid: "
        + dict(
            item_title=generation_prompt.item_title,
            prompt_uid=generation_prompt.prompt_uid,
            llm_engine=llm_engine,
        ).__repr__()
    )
    
    descriptions: list[str] = []
    if llm_engine in [Engine.gpt35turbo, Engine.gpt35turbo1106, Engine.gpt4turbo]:
        logging.info(f"Querying OpenAI servers for: {llm_engine}")
        engine = langchain.chat_models.ChatOpenAI(model_name=llm_engine)
    else:
        logging.info(f"Assuming {llm_engine} is running locally")
        engine = langchain.chat_models.ChatOpenAI(
            model_name=llm_engine,
            max_tokens=-1,
            openai_api_base=os.getenv('LOCAL_LLM_API_BASE'),
        )

    # with Context(
    #     "BATCH generate_llm_descriptions",
    #     inputs={
    #         "llm_engine":llm_engine,
    #         # "output_description_type": output_description_type,
    #         "generation_prompt": generation_prompt.__dict__,
    #         "target_description_count": description_count
    #     },
    #     storage=FileStorage("logs"),
    #     tags=["trying a thing", "runkey:foobar"],
    #     directory=True,
    # ) as ctx:
    for i in range(description_count):
        def query_llm_for_new_description() -> t.Union[str, ProductDetailsJson]:
            # TODO: make retry logic more flexible and/or better integrated with interlab/langchain tooling
            try:
                if output_description_type:
                    return query_for_json(engine, output_description_type, generation_prompt.prompt_text)
                return query_model(engine, generation_prompt.prompt_text)
            except (APIError, Timeout, APIConnectionError) as e:
                retry_interval = SUPER_RETRY_WAIT_INTERVAL_SECONDS
                logging.warning(e)
                logging.warning(f"Retryable error from LLM's API encountered. Will try again after {retry_interval} seconds.")
                time.sleep(retry_interval)
                raise QueryFailure # triggers interlab repeat_on_failure behavior
            except RateLimitError as e:
                logging.error(e)
                logging.error("Open AI Rate limit and/or quota exceeded. Shutting down until you wait a while and/or buy new credits.")
                exit()
            except Exception as e:
                raise e


        # desc = repeat_on_failure(
        #     fn=query_llm_for_new_description,
        #     max_repeats=MAX_SUPER_RETRY_COUNT,
        #     use_context=False,
        #     throw_if_fail=True,
        # )
        # if output_description_type:
        #     product_name = desc.product_name
        #     product_details = json.loads(desc.product_details) if isinstance(desc.product_details, str) else desc.product_details
        #     descriptions.append({"product_name": product_name, "product_details": product_details})
        # else:
        #     descriptions.append(desc)
        
        # with Context(
        #     "repeat query_llm_for_new_description",
        #     # inputs={
        #     #     "llm_engine":llm_engine,
        #     #     # "output_description_type": output_description_type,
        #     #     "generation_prompt": generation_prompt.__dict__,
        #     # },
        #     # storage=FileStorage("logs"),
        #     # tags=["trying a thing", "runkey:foobar"],
        #     # directory=True,
        # ) as ctx:
        desc = repeat_on_failure(
            fn=query_llm_for_new_description,
            max_repeats=MAX_SUPER_RETRY_COUNT,
            use_context=False,
            throw_if_fail=True,
        )

        if output_description_type:
            product_name = desc.product_name
            product_details = json.loads(desc.product_details) if isinstance(desc.product_details, str) else desc.product_details
            result = {"product_name": product_name, "product_details": product_details}
        else:
            result = desc

        descriptions.append(result)

    llm_description_batch = LlmGeneratedTextItemDescriptionBatch(
        item_type=generation_prompt.item_type,
        title=generation_prompt.item_title,
        descriptions=descriptions,
        origin=Origin.LLM,
        llm_engine=llm_engine,
        generation_prompt_uid=generation_prompt.prompt_uid,
        generation_prompt_nickname=generation_prompt.prompt_nickname,
        generation_prompt_text=generation_prompt.prompt_text,
    )

    return llm_description_batch