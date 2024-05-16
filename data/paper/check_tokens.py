import json
import random
import nltk
from nltk.tokenize import word_tokenize
from os import listdir
from os.path import isfile, join

# Initialize NLTK components
nltk.download('punkt')

def read_json_and_tokenize(directory):
    files = [f for f in listdir(directory) if isfile(join(directory, f)) and f.endswith('.json')]
    print("len(files)", len(files))
    token_counts = []
    
    for filename in files:
        with open(join(directory, filename), 'r', encoding='utf-8') as file:
            data = json.load(file)
            # Check if the 'abstract' key exists
            if 'abstract' in data:
                abstract = data['abstract']
            else:
                # pick random from data["descriptions"]:
                idx = random.randint(0, len(data['descriptions']) - 1)
                
                abstract = data['descriptions'][idx]
            tokens = word_tokenize(abstract)
            token_count = len(tokens)
            token_counts.append((filename, token_count))
            if token_count > 4000:
                print(f"{filename}: {token_count} tokens")

    return token_counts

# Set the directory where your JSON files are stored
for i in ["human", "llm"]:
    print(i)
    directory_path = f'/home/wombat_share/ai-ai-bias/data/paper/{i}'
    if i == "llm":
        for j in ["gpt35turbo1106", "gpt41106preview"]:
            sub_path = f"{directory_path}/{j}"
            print("sub_path", sub_path)
            print(j)
            read_json_and_tokenize(sub_path)
    else:    
        read_json_and_tokenize(directory_path)
    print("done", i)

