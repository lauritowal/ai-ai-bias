import pathlib
from datasets import load_dataset
import json
import random

DATA_DIR = pathlib.Path(__file__).parent.resolve() / "../data"

# Load first 1000 datapoints from Huggingface
dataset = load_dataset('scientific_papers', 'arxiv', split='train[:1000]')

# Randomly sample 100 data points
sample_size = 100
sampled_data = random.sample(list(dataset), sample_size)

papers_dir = DATA_DIR / "paper"
papers_dir.mkdir(exist_ok=True, parents=True)
for i, paper in enumerate(sampled_data):
    with open(f'{papers_dir}/human/paper_{i}.json', 'w') as file:
        print("Generate data", i)
        example = {
            "item_type": "paper",
            "abstract": paper['abstract'],
            "article":  paper['article'],
            "section_names": paper['section_names'],
            "origin": "Human"
        }
        json.dump(example, file, ensure_ascii=False, indent=4)
