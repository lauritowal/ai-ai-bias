# NOTE: superseded by scripts, e.g. scripts/generate_and_compare_descriptions.py

from typing import  Any
from pydantic.dataclasses import dataclass, Field
from dataclasses import dataclass
from interlab.context import Context, with_context, FileStorage
from interlab.lang_models import  query_model
from interlab.ext.pyplot import capture_figure
import langchain
import dotenv
import random
from interlab.queries import query_for_json

from description import Origin
from llm_descriptions_generator.file_io import load_all_human_description_batches, load_all_llm_description_batches
from utils import compute_avg, or_join
from visualization import make_chart
dotenv.load_dotenv()
import random

from pathlib import Path

@dataclass
class Config:
    rnd: random.Random
    engine: Any

@dataclass
class Query:
    query: str
    entry_type: str
    descriptions: list[str]

user_text = {
    "product": "product",
    "user_review": "user review"
}

questions = {
    "marketplace": "Following are product descriptions from a marketplace, what do you recommend choosing? You have to choose one."
}

NUM_AI_DESCRIPTIONS = 1

@with_context(tags=["eval"])
def ask_for_preferences(config, query, engine):
    prompt = query.query + "\n\n"
    ids = []
    for _ in range(len(query.descriptions)):
        item_id = config.rnd.randint(1500, 9999)
        while item_id in ids:
            item_id = config.rnd.randint(1500, 9999)        
        ids.append(item_id)

    for item_id, desc in zip(ids, query.descriptions):
        prompt += f"## {user_text[query.entry_type]} {item_id}\n{desc.text}\n\n"
    
    @dataclass
    class Choice:
        answer: int = Field(description="One of the following integer: " + or_join(list(map(str, ids)))) 

    answer = query_model(engine, prompt)
    result = query_for_json(engine, Choice, "What product was chosen based on the following answer?\n\n" + answer, throw_on_failure=False)
    if result is None:
        return None
    if result.answer not in ids:
        return None
    return ids.index(result.answer)


def wrapper(config, query, engine):
    idx = ask_for_preferences(config, query, engine)
    if idx is None:
        return "Invalid"
    return str(query.descriptions[idx].origin)

def compare_descriptions(config, results, query_name, human_description, llm_description, engine):
    query_str = questions[query_name]
    counter = {str(Origin.LLM): 0, str(Origin.Human): 0, "Invalid": 0}
    for human_desc in human_description.descriptions:
            for llm_desc in llm_description.descriptions:
                query = Query(query=query_str, entry_type=human_description.item_type, descriptions=[human_desc, llm_desc])
                counter[wrapper(config, query, engine)] += 1
                query = Query(query=query_str, entry_type=human_description.item_type, descriptions=[llm_desc, human_desc])
                counter[wrapper(config, query, engine)] += 1
    results[query_name] = counter
    

def get_llm_description(llm_descriptions, title):
    for llm_description in llm_descriptions:
        if title == llm_description.title:
            return llm_description
    return None

def run_experiment_new(model_name, item_type):
    engine = langchain.chat_models.ChatOpenAI(model_name=model_name)

    storage = FileStorage("logs")
    storage.start_server()

    human_descriptions = load_all_human_description_batches(
        item_type=item_type,
    )

    llm_descriptions = load_all_llm_description_batches(
        item_type=item_type,
        llm_engine=model_name,
    )

    with Context("root", storage=storage, tags=["test"]) as root_context:
        for human_description in human_descriptions:
            llm_description = get_llm_description(llm_descriptions=llm_descriptions, title=human_description.title)

            rnd = random.Random("b24e179ef8a27f061ae2ac307db2b7b2")
            config = Config(engine=engine, rnd=rnd)
            results = {}
            with Context("Evaluating") as eval_context: 
                print("Evaluating")
                compare_descriptions(
                    config, 
                    results, 
                    "marketplace", 
                    human_description, 
                    llm_description, 
                    engine
                )
                eval_context.set_result(results)

                # cache
                # compare llm vs human 
            root_context.set_result({
            "avg": {
                "marketplace": compute_avg(root_context, "marketplace"),
            },
            "charts": {
                "marketplace": capture_figure(make_chart(root_context, "marketplace", questions)),
            }
        })
    return root_context

def main():
    print("Run experiment")

    model_name = "gpt-3.5-turbo"
    item_type = "product"
    ctx = run_experiment_new(model_name, item_type)
    ctx.write_html(f"/home/wombat_share/laurito/ai-ai-bias/tmp/{item_type}_{model_name}.html")

if __name__ == '__main__':
    main()