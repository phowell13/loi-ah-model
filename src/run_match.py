import pandas as pd

from ratings import (
    build_match_model,
    load_matches,
    current_season_matches
)
from poisson_model import goal_difference_probs, match_probs
from asian_handicap import fair_odds_for_handicap, ah_expected_return


BETFAIR_LINES = [
    {"selection": "Drogheda", "handicap": 0.0, "market_odds": 1.44},
    {"selection": "Drogheda", "handicap": -0.25, "market_odds": 1.70},
    {"selection": "Drogheda", "handicap": -0.5, "market_odds": 1.96},
    {"selection": "Drogheda", "handicap": -0.75, "market_odds": 2.27},
    {"selection": "Drogheda", "handicap": -1.0, "market_odds": 2.87},
]


def away_handicap_to_home_handicap(away_handicap):
    return -away_handicap


def run():
    model = build_match_model(
        home_team="Drogheda",
        away_team="Waterford",
        path="IRL.csv",
        season=2026,
    )

    home_xg = model["home_xg"]
    away_xg = model["away_xg"]

    print(f"\n{model['home_team']} v {model['away_team']}")
    print(f"Projected goals: {model['home_team']} {home_xg} - {away_xg} {model['away_team']}\n")

    probs = match_probs(home_xg, away_xg)
    print("Match probabilities")
    print(f"Home win: {probs['home_win']:.2%}")
    print(f"Draw:     {probs['draw']:.2%}")
    print(f"Away win: {probs['away_win']:.2%}\n")

    print("Sanity check:")
    print(f"Total probability = {probs['home_win'] + probs['draw'] + probs['away_win']:.4f}")
    print()

    gd_probs = goal_difference_probs(home_xg, away_xg)

    rows = []

    for line in BETFAIR_LINES:
        selection = line["selection"]
        market_odds = line["market_odds"]

        if selection == "Drogheda":
            home_handicap = line["handicap"]
        else:
            home_handicap = away_handicap_to_home_handicap(line["handicap"])

        fair_odds = fair_odds_for_handicap(gd_probs, home_handicap)
        ev = ah_expected_return(gd_probs, home_handicap, market_odds)

        rows.append({
            "selection": selection,
            "handicap": line["handicap"],
            "market_odds": market_odds,
            "model_fair_odds": fair_odds,
            "edge_pct": round(ev * 100, 2),
            "value": "YES" if ev > 0.03 else "NO",
        })

    output = pd.DataFrame(rows)
    print(output.to_string(index=False))

    output.to_csv("outputs/drogheda_waterford_ah.csv", index=False)
    print("\nSaved: outputs/drogheda_waterford_ah.csv")


if __name__ == "__main__":
    run()
