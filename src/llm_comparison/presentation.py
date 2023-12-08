import logging
import textwrap
import typing as t

from matplotlib import pyplot as plt

from llm_comparison.llm_comparison import DescriptionBattleTally
from llm_descriptions_generator.schema import Origin

def compute_llm_win_ratio(tally: DescriptionBattleTally) -> t.Optional[float]:
    # total = tally[Origin.LLM] + tally[Origin.Human] + tally["Invalid"]
    total = tally[Origin.LLM] + tally[Origin.Human]
    if total == 0:
        # If all results are invalid, return None
        logging.warning(f"Encountered description battle tally with no valid results: {tally}")
        return None
    return tally[Origin.LLM] / total

def compute_avg_llm_win_ratio(tallies: list[DescriptionBattleTally]) -> t.Optional[float]:
    valid_llm_win_ratios = []
    for tally in tallies:
        llm_win_ratio = compute_llm_win_ratio(tally)
        if llm_win_ratio is not None:
            valid_llm_win_ratios.append(llm_win_ratio)
    if len(valid_llm_win_ratios) == 0:
        # If all results are invalid, return None
        logging.warning(f"WARNING: processed data has ZERO description battle tallies with valid results: {tallies}")
        return None
    return sum(valid_llm_win_ratios) / len(valid_llm_win_ratios)


def make_comparison_run_permutation_label(
    item_type: str,
    comparison_llm_engine: str,
    comparison_prompt_key: str,
    description_llm_engine: str,
    description_prompt_key: str,
) -> str:
    return (
        f"{item_type}"
        + f"---DESCRIPTION-{description_prompt_key}|{description_llm_engine}"
        + f"---COMPARISON-{comparison_prompt_key}|{comparison_llm_engine}"
    )

def make_chart(
    chart_label: str,
    # comparison_results_by_item: dict[str, list[DescriptionBattleTally]],
    comparison_results_by_item: dict[str, DescriptionBattleTally],
):
    llm_win_ratios_by_item = [
        (name, compute_llm_win_ratio(tally))
        for (name, tally) in comparison_results_by_item.items()
    ]
    llm_win_ratios_by_item = [
        lwr for lwr in llm_win_ratios_by_item if (
            lwr is not None and lwr[0] is not None and lwr[1] is not None
        )
    ]
    llm_win_ratios_by_item.sort(key=lambda x: x[0])
    llm_win_ratios_by_item.sort(key=lambda x: -x[1])

    plt.rcParams.update({"font.size": 6})
    fig = plt.figure()
    plt.bar(
        x=[x[0] for x in llm_win_ratios_by_item],
        height=[x[1] for x in llm_win_ratios_by_item],
    )
    plt.xticks(rotation=30, wrap=True)
    plt.title("\n".join(textwrap.wrap(chart_label, 100)), fontsize=8)
    return fig
