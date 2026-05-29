def ah_profit(goal_diff: int, handicap: float) -> float:
    """
    Returns profit per 1 unit staked at fair odds.
    Used to calculate Asian handicap settlement.

    goal_diff = home goals - away goals
    handicap = home handicap, e.g. -0.5, -0.25, 0, +0.25
    """

    parts = split_handicap(handicap)
    return sum(single_line_result(goal_diff, h) for h in parts) / len(parts)


def split_handicap(handicap: float) -> list[float]:
    """
    Splits quarter handicaps into two half-stakes.
    """
    if handicap % 0.5 == 0:
        return [handicap]

    lower = handicap - 0.25
    upper = handicap + 0.25
    return [lower, upper]


def single_line_result(goal_diff: int, handicap: float) -> float:
    """
    Returns:
    1.0 = win
    0.0 = push
    -1.0 = loss
    """
    result = goal_diff + handicap

    if result > 0:
        return 1.0
    if result == 0:
        return 0.0
    return -1.0


def ah_expected_return(
    probs_by_goal_diff: dict[int, float],
    handicap: float,
    odds: float
) -> float:
    """
    Expected ROI per 1 unit staked at given decimal odds.
    """
    ev = 0.0

    for goal_diff, prob in probs_by_goal_diff.items():
        settlement = ah_profit(goal_diff, handicap)

        if settlement > 0:
            ev += prob * settlement * (odds - 1)
        elif settlement < 0:
            ev += prob * settlement

    return ev


def fair_odds_for_handicap(
    probs_by_goal_diff: dict[int, float],
    handicap: float
) -> float:
    """
    Finds approximate break-even decimal odds.
    """
    low = 1.01
    high = 20.0

    for _ in range(60):
        mid = (low + high) / 2
        ev = ah_expected_return(probs_by_goal_diff, handicap, mid)

        if ev > 0:
            high = mid
        else:
            low = mid

    return round((low + high) / 2, 3)
