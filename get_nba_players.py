import requests
import csv
import json
from tqdm import tqdm
from time import sleep
from random import uniform
import argparse

# return the seasons as json with player_id:pid, regular_seasons:listofseasons, allstar:listofseasons, playoffs:listofseasons
# parser = argparse.ArgumentParser(description="Batch player IDs")
# parser.add_argument(
#     "-b", "--batch", help="Pick a batch num", type=int
# )


def extract_player_data(player_json, index):
    player_data = player_json["resultSets"][index]
    return dict(zip(player_data["headers"], player_data["rowSet"].pop()))


def get_player_seasons(player_json, player_id):
    player_data = player_json["resultSets"][2]["rowSet"]
    return {
        "PLAYER_ID": player_id,
        "regular_seasons": [
            season[0] for season in player_data if season[0].startswith("2")
        ],
        "all_star_seasons": [
            season[0] for season in player_data if season[0].startswith("3")
        ],
        "playoff_seasons": [
            season[0] for season in player_data if season[0].startswith("4")
        ],
        "gleague_seasons": [
            season[0] for season in player_data if season[0].startswith("1")
        ],
    }


def get_player_json(player_id, max_retries=5):
    for _ in range(max_retries):
        try:
            player_json = player_json_request(player_id)
            check_player_json(player_json)
            return player_json
        except AssertionError:
            continue
        else:
            break
    else:
        save_player_json(player_json, player_id)
        return None


def player_json_request(player_id):
    sleep(uniform(1.1, 1.8))
    url = "https://stats.nba.com/stats/commonplayerinfo/"
    headers = {
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "x-nba-stats-token": "true",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
        "x-nba-stats-origin": "stats",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Referer": "https://stats.nba.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
    }
    parameters = {"playerId": str(player_id), "leagueId": "00"}
    return requests.get(url, params=parameters, headers=headers).json()


def check_player_json(player_json):
    assert "resultSets" in player_json.keys()
    assert player_json["resultSets"] is not None
    assert len(player_json["resultSets"]) == 3
    assert all([player_json["resultSets"][idx] is not None for idx in range(3)])
    assert all(len(player_json["resultSets"][idx]["rowSet"]) > 0 for idx in range(2))


def save_players_info(data, name):
    save_path = f"./data/player_{name}.csv"
    fieldnames = {key for elem in data for key in elem.keys()}
    with open(save_path, "a") as f:
        dict_writer = csv.DictWriter(f, fieldnames)
        dict_writer.writeheader()
        dict_writer.writerows(data)


def save_player_json(player_json, player_id):
    save_path = f"./data/bad_player_json/player_{player_id}.json"
    with open(save_path, "w") as outfile:
        json.dump(player_json, outfile)


def main():
    # player_ids = [76001, 76002, 76003, 51, 1505]
    with open("./data/nba_player_ids.csv", "r") as f:
        reader = csv.reader(f)
        player_ids = next(reader)

    common_player_info = list()
    player_headlines = list()
    player_seasons = list()

    for player_id in tqdm(player_ids):
        player_json = get_player_json(player_id)

        if player_json:
            common_player_info.append(extract_player_data(player_json, 0))
            player_headlines.append(extract_player_data(player_json, 1))
            player_seasons.append(get_player_seasons(player_json, player_id))

    save_players_info(common_player_info, "common_player_info")
    save_players_info(player_headlines, "player_headlines")
    save_players_info(player_seasons, "player_seasons")


if __name__ == "__main__":
    main()
