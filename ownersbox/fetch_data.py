#!/usr/bin/python3

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import io, os, re, time
import pandas as pd

FP_BASE_URL = 'https://www.fantasypros.com/nfl/projections/{}.php?&scoring=HALF'
ROTOWIRE_OWNERSBOX_URL = "https://www.rotowire.com/daily/nfl/value-report.php?site=OwnersBox"

# Fantasy Pros player names include the abbreviation of their team; it needs to be removed
def strip_team_abb(name):
    player = re.findall('(.*)\s[A-Z]{2,3}', name)
    if player:
        return player[0]
    return name # this will be a DST

# Fetch all positional data from FP, return a DataFrame containing all the data for the week
def fetch_fp_data():
    dfs = []
    for position in ['qb', 'wr', 'rb', 'te', 'dst']:
        df = pd.read_html(FP_BASE_URL.format(position))[0]
        if position != 'dst':
            # The new Fantasy Pros table (2021) has new column headers that throw a wrench into Pandas,
            # this hack of simply removing the first line of the .csv works, but is kind of ugly.
            csv = df.to_csv(index=False)
            csv = csv[csv.find('\n')+1:csv.rfind('\n')]
            buffer = io.StringIO(csv)
            df = pd.read_csv(buffer)
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True, sort=False)

# Given a URL, use Selenium to open a web browser, sleep for a bit to cause
# the JavaScript to run (and populate the table), then scrape the html
def selenium_scrape_html(url):
    options = Options()
    options.add_argument('--headless')
    try:
        s = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=s, chrome_options=options)
        driver.get(url)
        time.sleep(7) # lucky number 7, never fails
        html = driver.page_source
        driver.quit()
    except (Exception):
        print('Warning: Something happened while scraping Rotowire.')
        return []
    return html

def main():
    # retrieve the OwnersBox DFS information from Rotowire table
    print('--- (1/4) Retrieving OwnersBox data from Rotowire ---')
    html = selenium_scrape_html(ROTOWIRE_OWNERSBOX_URL)

    # setup a dataframe with OwnersBox DFS data and write to json
    print('--- (2/4) Processing OwnersBox data ---')
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('div', {'class': 'players-table'}).find('div', {'class', 'webix_ss_body'})

    players = table.find('div', {'class': 'name'})
    salaries = table.find('div', {'class': 'salary'}).find_all('div')
    positions = table.find('div', {'class': 'position'}).find_all('div')
    teams = table.find('div', {'class': 'team'}).find_all('div')

    i = 0
    d = {}
    for player in players.findAll('div'):
        d[player.find('span')['data-name']] = teams[i].string, positions[i].string, salaries[i].string[1:]
        i = i + 1
    ob_df = pd.DataFrame(d).T.reset_index()
    ob_df.columns = ['name', 'team', 'position', 'salary']

    # setup a dataframe with Fantasy Pros positional data
    print('--- (3/4) Fetching the Fantasy Pros data ---')
    fp_df = fetch_fp_data()
    fp_df = fp_df[['Player', 'FPTS']]
    fp_df.columns = ['name', 'points']
    fp_df['name'] = fp_df['name'].str.strip()
    fp_df['name'] = fp_df['name'].apply(strip_team_abb)

    print('--- (4/4) Combining DataFrames ---')
    # combine the Fantasy Pros dataframe with the OwnersBox one
    ob_df.set_index('name', inplace=True)
    fp_df.set_index('name', inplace=True)
    merged = ob_df.join(fp_df)
    merged.dropna(inplace=True)
    merged.sort_values(by=['salary'], ascending=False, inplace=True)

    # save Fantasy Pros data with the OwnersBox salaries intact
    if not os.path.exists('./csv'):
        os.makedirs('./csv')
    merged.to_csv('./csv/fantasypros.csv', encoding='utf-8', index=True)
    print('--- Completed ---')

if __name__ == "__main__":
    main()
