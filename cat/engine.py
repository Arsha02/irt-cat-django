import numpy as np

GRID = np.linspace(-3, 3, 100)


def p(theta, a, b, c):
    return c + (1 - c) / (1 + np.exp(-a * (theta - b)))


def info(theta, a, b, c):
    pr = p(theta, a, b, c)
    if pr <= 0 or pr >= 1:
        return 0.0
    return (a**2) * ((1 - pr) / pr) * ((pr - c) / (1 - c))**2


def estimate_theta(resp, bank):
    if not resp:
        return 0.0

    scores = []
    for t in GRID:
        ll = 0.0
        for q_id, score in resp.items():
            q_id = str(q_id)
            prob = p(t, bank[q_id]["a"], bank[q_id]["b"], bank[q_id]["c"])
            actual_p = prob if score == 1 else 1 - prob
            ll += np.log(max(actual_p, 1e-9))
        scores.append(ll - 0.5 * (t ** 2))
    return round(float(GRID[np.argmax(scores)]), 2)


def se(theta, answered, bank):
    total_info = sum(info(theta, bank[str(q)]["a"], bank[str(
        q)]["b"], bank[str(q)]["c"]) for q in answered)
    if total_info <= 0:
        return 99.0
    return round(1 / np.sqrt(total_info), 3)


def next_item(theta, bank, answered):
    answered_str = {str(q) for q in answered}
    left = {str(k): v for k, v in bank.items() if str(k) not in answered_str}

    if not left:
        return None
    return max(left, key=lambda q: info(theta, left[q]["a"], left[q]["b"], left[q]["c"]))
