import os
import textwrap
from matplotlib import pyplot as plt


def make_chart(ctx, key, questions):
    result = []
    for child in ctx.children:
        entry = child.inputs["entry"]
        name = os.path.basename(entry["filename"][:-5])
        k = child.result[key]
        o1, o2 = k["Origin.Ai"], k["Origin.Human"]
        result.append((name, o1 / (o1 + o2)))
    fig = plt.figure()
    result.sort(key=lambda x: x[0])
    result.sort(key=lambda x: -x[1])
    plt.bar(x=[x[0] for x in result], height=[x[1] for x in result])
    plt.xticks(rotation=30)
    plt.title("\n".join(textwrap.wrap(questions[key], 55)))
    return fig
