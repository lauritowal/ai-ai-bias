import scripts_common_setup

import json
import re
from pathlib import Path

from llm_comparison.presentation import compute_llm_win_ratio
from llm_comparison.llm_comparison import DescriptionBattleTally
from llm_descriptions_generator.schema import Origin

THIS_FILE_DIR = Path(__file__).parent.resolve()
FULL_RUNS_DIR = THIS_FILE_DIR / "../full_run_outputs"


# PURPOSE OF SCRIPT: older version of calculating LLM win ratio
# counted "Invalid" results in the total, which skewed the numbers
# when there were non-neglible numbers of invalid results.
# This script fixes the data results

def fix_results_object(results: dict) -> dict:
    # NOTE: mutates input object
    for run_name, run_data in results.items():
        # fix individual items
        details_by_item = run_data.get("details_by_item")
        for details in details_by_item.values():
            human_ct = details.get(str(Origin.Human))
            llm_ct = details.get(str(Origin.LLM))
            invalid_ct = details.get("Invalid")
            tally = DescriptionBattleTally({
                 Origin.Human: human_ct,
                 Origin.LLM: llm_ct,
                 "Invalid": invalid_ct
            })
            details["LLM_win_ratio"] = compute_llm_win_ratio(tally)
    
        # fix totals
        total_tallies = run_data.get("total_tallies")
        run_data["avg_llm_win_ratio"] = compute_llm_win_ratio(total_tallies)
    return results


# direct fix on the json data files
json_filepaths = FULL_RUNS_DIR.glob("*.json")
for filepath in json_filepaths:
    with open(filepath) as f:
        data = json.load(f)
        
    results = data.get("results")
    data["results"] = fix_results_object(results)

    with open(filepath, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# similar action via regex muckery on the html files
html_filepaths = FULL_RUNS_DIR.glob("*.html")
def fix_initInterlab_args(match):
    context = json.loads(match.group(2))
    context_result = context.get("result")
    if context_result:
        run_results_obj = context_result.get("results")
        context_result["results"] = fix_results_object(run_results_obj)
    return 'window.initInterlab("{}", {})'.format(match.group(1), json.dumps(context))

for html_filepath in html_filepaths:
    with open(html_filepath, 'r') as file:
        html_doc = file.read()

    # Find the script tag with the window.initInterlab call and process&replace the Context object
    html_doc = re.sub(r'window\.initInterlab\("([^"]*)", ({.*?})\)', fix_initInterlab_args, html_doc)

    with open(html_filepath, 'w') as f:
        f.write(html_doc)