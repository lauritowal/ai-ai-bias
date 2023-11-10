from dataclasses import dataclass
import os

import toml

from description import Description, Origin
from utils import ensure_list


@dataclass
class Entry:
    filename: str
    type: str
    prompt: str
    human_desc: list[str]
    
    
def remove_empty_lines(file):
    """Remove empty lines from file."""
    lines = file.readlines()
    no_empty_lines = [line for line in lines if line.strip()]
    return "".join(no_empty_lines)

def load_data(filename: str):
    print("Loading", filename)
    with open(filename) as f:
        # needed for TOML to work
        no_empty_lines = remove_empty_lines(f) 
        print("no_empty_lines", no_empty_lines)
        data = toml.loads(no_empty_lines)
        
    return Entry(
        filename=filename,
        type=data["type"].strip(),
        prompt=data["prompt"].strip(),
        human_desc=[
            Description(origin=Origin.Human, text=s.strip()) for s in ensure_list(data["human_desc"])
        ]
    )

def load_all(path):
    result = []
    for name in os.listdir(path): # TODO: replace os with Path
        if not name.endswith(".toml"):
            continue
        result.append(load_data(os.path.join(path, name)))
    return result

