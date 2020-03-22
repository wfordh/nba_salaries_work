from bs4 import BeautifulSoup
import requests
from time import sleep
import pandas as pd
from tqdm import tqdm
from random import uniform

from salary_utilities import headers, team_season_mapping


def get_hoops_hype_salary(team, season):
    """
	Scrapes and cleans salary data from Hoops Hype, if the team existed at the time.
	If it did not, then nothing is returned.
	"""
    sleep(uniform(1.1, 2))

    team = team.lower().replace(" ", "_")
    season = f"{season}-{season+1}"
    url = f"https://hoopshype.com/salaries/{team}/{season}/"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    salary_table = soup.find(
        "table",
        {"class": "hh-salaries-team-table hh-salaries-table-sortable responsive"},
    )

    columns = [
        td.text.replace("*", "Inflation Adj")
        for td in salary_table.find("thead").find_all("tr").pop().find_all("td")
    ]
    rows = [
        [
            td.get("data-value")
            if td.get("data-value") is not None
            else td.text.strip()
            for td in tr.find_all("td")
        ]
        for tr in salary_table.find("tbody").find_all("tr")
    ]

    df = pd.DataFrame(rows, columns=columns)
    df["season"] = season
    df["team"] = team
    return df if rows != [] else None


def main():

    teams = team_season_mapping["2019"]
    team_season_list = list()

    for season in range(1990, 2019):
        for team in tqdm(teams, desc=f"Getting teams for {season} NBA season."):
            team_season_list.append(get_hoops_hype_salary(team, season))

    pd.concat(team_season_list, sort=False).to_csv(
        "./data/hoopshype_salaries.csv", index=False
    )


if __name__ == "__main__":
    main()
