import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from time import sleep
from random import uniform

from salary_utilities import headers, team_season_mapping


def get_historical_bi_team_salary(team, season):
    sleep(uniform(1, 2.5))
    team = team.lower().replace(" ", "-")
    try:
        base_url = f"http://www.basketballinsiders.com/{team}-team-salary/{team}-salary-archive-{season}/"
        if season == 201415 and team == "minnesota-timberwolves":
            base_url = "http://www.basketballinsiders.com/minnesota-timberwolves-team-salary/minnesota-timbewolves-salary-archive-201415/"
        if season == 201617 and team == "portland-trail-blazers":
            base_url = "http://www.basketballinsiders.com/portland-trail-blazers-team-salary/portland-trail-blazers-archive-201617/"
        if season == 201516 and team == "washington-wizards":
            base_url = "http://www.basketballinsiders.com/washington-wizards-team-salary/washington-wizard-salary-archive-201516/"
        if season == "2018-19" and team in ["san-antonio-spurs", "toronto-raptors"]:
            base_url = f"http://www.basketballinsiders.com/{team}-team-salary/{team}-salary-archive-2017-18-2/"
        if season == "2018-19" and team == "phoenix-suns":
            base_url = "http://www.basketballinsiders.com/phoenix-suns-team-salary/phoenix-suns-archive-2018-19/"

        response = requests.get(base_url, headers=headers)

        soup = BeautifulSoup(response.content, "html.parser")
        columns = [th.text for th in soup.find("thead").find_all("th")]

        rows = list(
            filter(
                lambda val: len(val) > 0,
                [
                    [td.text for td in tr.find_all("td")]
                    for tr in soup.find("tbody").find_all("tr")
                ],
            )
        )

        rows = [
            [player[0].replace(" - X", ""), player[1].replace("$", "").replace(",", "")]
            for player in rows
        ]

        df = pd.DataFrame(rows, columns=["player", "salary"])
        df["season"] = columns.pop()
        return df
    except AttributeError:
        print(f"{team} not found in {season}. Base url: {base_url}")
        return pd.DataFrame([[None, None]], columns=["player", "salary"])


def main():
    team_season_list = []

    for season in range(201213, 201920, 101):
        teams_list = team_season_mapping[str(season)[:4]]
        if season in [201718, 201819]:
            season = str(season)[:4] + "-" + str(season)[4:]
        for team in tqdm(
            teams_list, desc=f"Getting teams for {str(season)} NBA season"
        ):
            team_season_list.append(get_historical_bi_team_salary(team, season))

    df = pd.concat(team_season_list, sort=False)
    df = df.groupby(["player", "season"]).sum().reset_index()
    df.to_csv("data/basketball_insiders_salaries.csv", index=False)


if __name__ == "__main__":
    main()
