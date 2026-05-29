import math
from collections import defaultdict


def poisson_probability(k, lam):
    """
    Probability of scoring exactly k goals.
    """
    return (math.exp(-lam) * lam**k) / math.factorial(k)


def score_matrix(home_xg, away_xg, max_goals=10):
    """
    Returns scoreline probabilities.
    """

    matrix = {}

    for hg in range(max_goals + 1):
        for ag in range(max_goals + 1):

            p_home = poisson_probability(hg, home_xg)
            p_away = poisson_probability(ag, away_xg)

            matrix[(hg, ag)] = p_home * p_away

    return matrix


def goal_difference_probs(home_xg, away_xg, max_goals=10):
    """
    Converts score matrix into goal difference probabilities.
    """

    score_probs = score_matrix(home_xg, away_xg, max_goals)

    goal_diff_probs = defaultdict(float)

    for (hg, ag), prob in score_probs.items():
        goal_diff_probs[hg - ag] += prob

    return dict(goal_diff_probs)


def match_probs(home_xg, away_xg):
    """
    Returns win/draw/loss probabilities.
    """

    score_probs = score_matrix(home_xg, away_xg)

    home = 0
    draw = 0
    away = 0

    for (hg, ag), prob in score_probs.items():

        if hg > ag:
            home += prob
        elif hg == ag:
            draw += prob
        else:
            away += prob

    return {
        "home_win": home,
        "draw": draw,
        "away_win": away
    }
