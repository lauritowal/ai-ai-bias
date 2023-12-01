import textwrap
from matplotlib import pyplot as plt

from llm_comparison.llm_comparison import DescriptionBattleTally
from llm_descriptions_generator.schema import Origin

def compute_llm_win_ratio(tally: DescriptionBattleTally) -> float:
    total = tally[Origin.LLM] + tally[Origin.Human] + tally["Invalid"]
    return tally[Origin.LLM] / total

def compute_avg_llm_win_ratio(tallies: list[DescriptionBattleTally]) -> float:
    print(tallies)
    return sum([compute_llm_win_ratio(tally) for tally in tallies]) / len(tallies)

def make_full_comparison_label(
    item_type: str,
    comparison_llm_engine: str,
    comparison_prompt_key: str,
    description_llm_engine: str,
    description_prompt_key: str,
) -> str:
    return "-".join([
        item_type,
        comparison_llm_engine,
        comparison_prompt_key,
        description_llm_engine,
        description_prompt_key,
    ])

def make_chart(
    chart_label: str,
    # comparison_results_by_item: dict[str, list[DescriptionBattleTally]],
    comparison_results_by_item: dict[str, DescriptionBattleTally],
):
    llm_win_ratios_by_item = [
        (name, compute_llm_win_ratio(tally))
        for (name, tally) in comparison_results_by_item.items()
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
