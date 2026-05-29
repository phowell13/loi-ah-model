import pandas as pd


def load_matches(path="IRL.csv"):
    df = pd.read_csv(path)

    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df["Season"] = pd.to_numeric(df["Season"], errors="coerce")
    df["HG"] = pd.to_numeric(df["HG"], errors="coerce")
    df["AG"] = pd.to_numeric(df["AG"], errors="coerce")

    df = df.dropna(subset=["Date", "Season", "Home", "Away", "HG", "AG"])

    return df


def current_season_matches(df, season=2026):
    return df[df["Season"] == season].copy()


def league_averages(df):
    return {
        "home_goals_avg": df["HG"].mean(),
        "away_goals_avg": df["AG"].mean(),
        "total_goals_avg": (df["HG"] + df["AG"]).mean(),
    }


def team_strengths(df):
    league = league_averages(df)

    teams = sorted(set(df["Home"]).union(set(df["Away"])))
    rows = []

    for team in teams:
        home = df[df["Home"] == team]
        away = df[df["Away"] == team]

        home_for = home["HG"].mean()
        home_against = home["AG"].mean()
        away_for = away["AG"].mean()
        away_against = away["HG"].mean()

        attack_home = safe_div(home_for, league["home_goals_avg"])
        defence_home = safe_div(home_against, league["away_goals_avg"])
        attack_away = safe_div(away_for, league["away_goals_avg"])
        defence_away = safe_div(away_against, league["home_goals_avg"])

        rows.append({
            "team": team,
            "home_games": len(home),
            "away_games": len(away),
            "home_for": home_for,
            "home_against": home_against,
            "away_for": away_for,
            "away_against": away_against,
            "attack_home": attack_home,
            "defence_home": defence_home,
            "attack_away": attack_away,
            "defence_away": defence_away,
        })

    return pd.DataFrame(rows)


def safe_div(a, b):
    if pd.isna(a) or pd.isna(b) or b == 0:
        return 1.0
    return a / b


def expected_goals(df, home_team, away_team):
    league = league_averages(df)
    strengths = team_strengths(df).set_index("team")

    if home_team not in strengths.index:
        raise ValueError(f"Unknown home team: {home_team}")

    if away_team not in strengths.index:
        raise ValueError(f"Unknown away team: {away_team}")

    home = strengths.loc[home_team]
    away = strengths.loc[away_team]

    home_xg = (
        league["home_goals_avg"]
        * home["attack_home"]
        * away["defence_away"]
    )

    away_xg = (
        league["away_goals_avg"]
        * away["attack_away"]
        * home["defence_home"]
    )

    return round(home_xg, 3), round(away_xg, 3)


def build_match_model(home_team, away_team, path="IRL.csv", season=2026):
    df = load_matches(path)
    season_df = current_season_matches(df, season)

    home_xg, away_xg = expected_goals(season_df, home_team, away_team)

    return {
        "home_team": home_team,
        "away_team": away_team,
        "season": season,
        "home_xg": home_xg,
        "away_xg": away_xg,
        "league": league_averages(season_df),
        "team_strengths": team_strengths(season_df),
    }
