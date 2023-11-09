def ensure_list(value):
    if isinstance(value, list):
        return value
    else:
        return [value]

def or_join(values):
    if not values:
        return ""
    if len(values) == 1:
        return values[0]
    return ",".join(values[:-1]) + " or " + values[-1]


def compute_avg(ctx, key):
    r = []
    for child in ctx.children:
        b = child.result[key]
        o1 = b["Origin.Ai"]
        o2 = b["Origin.Human"]
        r.append(o1 / (o1 + o2))    
    return sum(r) / len(r)