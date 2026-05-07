import numpy as np

GRID = np.linspace(-3, 3, 100)


def p(theta, a, b, c):
    return c + (1-c)/(1 + np.exp(-a*(theta-b)))


def info(theta, a, b, c):
    pr = p(theta, a, b, c)
    return (a**2)*((1-pr)/pr)*((pr-c)/(1-c))**2


def mle(resp, bank):
    if len(resp) < 2:
        return 0.0

    scores = []
    for t in GRID:
        ll = sum(
            np.log(max(
                p(t, bank[q]["a"], bank[q]["b"], bank[q]["c"]) if s
                else 1 - p(t, bank[q]["a"], bank[q]["b"], bank[q]["c"]),
                1e-9
            ))
            for q, s in resp.items()
        )
        scores.append(ll - 0.5*t*t)

    return round(float(GRID[np.argmax(scores)]), 2)


def se(theta, answered, bank):
    total = sum(info(theta, bank[q]["a"], bank[q]["b"], bank[q]["c"])
                for q in answered)
    return round(1/np.sqrt(total), 3)


def next_item(theta, bank, answered):
    left = {k: v for k, v in bank.items() if k not in answered}
    if not left:
        return None
    return max(left, key=lambda q: info(theta, left[q]["a"], left[q]["b"], left[q]["c"]))
