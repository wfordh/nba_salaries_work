import csv
import requests
from bs4 import BeautifulSoup


def get_realgm_salary_caps():
    """
    Scrapes and returns the headers and rows from RealGM's NBA salary cap page.
    """
    resp = requests.get("https://basketball.realgm.com/nba/info/salary_cap")
    soup = BeautifulSoup(resp.content, "html.parser")
    table = soup.find("table", {"class": "basketball compact"})
    headers = [tr.text for tr in table.find("thead").find_all("tr")[1].find_all("th")]
    headers = [col + " MLE" if col in headers[-3:] else col for col in headers]
    rows = [
        [td.text for td in tr.find_all("td") if td.text != "-"]
        for tr in table.find("tbody").find_all("tr")
    ]
    return headers, rows


def save_salary_caps(headers, rows):
    """
    Saves the NBA salary cap data locally as a CSV file.
    """
    with open("./data/NBA_yearly_salary_caps.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def main():
    headers, rows = get_realgm_salary_caps()
    save_salary_caps(headers, rows)


if __name__ == "__main__":
    main()
