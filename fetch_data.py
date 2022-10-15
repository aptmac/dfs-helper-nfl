#!/usr/bin/python3

from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from urllib.request import urlopen
from webdriver_manager.chrome import ChromeDriverManager
import json, io, logging, os, re, sys, time
import pandas as pd

FP_BASE_URL = 'https://www.fantasypros.com/nfl/projections/{}.php?&scoring=HALF'
ROTOWIRE_BASE_URL = "https://www.rotowire.com/daily/nfl/value-report.php?site="
YAHOO_API_ENDPOINT = 'https://dfyql-ro.sports.yahoo.com/v2/external/playersFeed/nfl'

def fetch_yahoo_data():
    jsonurl = urlopen(YAHOO_API_ENDPOINT)
    data = json.loads(jsonurl.read())
    return data

def write_data(data, format):
    if not os.path.exists('./rawdata'):
        os.makedirs('./rawdata')
    data.to_csv('./rawdata/' + format + '-' + datetime.now().strftime("%d-%m-%Y-%Hh%Mm%Ss") + '.csv', encoding='utf-8', index=True)

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

# Fantasy Pros player names include the abbreviation of their team; it needs to be removed
def remove_team_abb(name):
    player = re.findall('(.*)\s[A-Z]{2,3}', name)
    if player:
        return player[0]
    return name # this will be a DST

# Given a URL, use Selenium to open a web browser, sleep for a bit to cause
# the JavaScript to run (and populate the table), then scrape the html
def selenium_scrape_html(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    logging.getLogger('WDM').setLevel(logging.NOTSET)
    os.environ['WDM_LOG'] = "false"
    try:
        s = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=s, options=options)
        driver.get(url)
        time.sleep(7) # lucky number 7, never fails
        html = driver.page_source
        driver.quit()
    except (Exception):
        print('Warning: Something happened while scraping Rotowire.')
        return []
    return html

def setup_fp_df():
    # setup a dataframe with Fantasy Pros positional data
    fp_df = fetch_fp_data()
    fp_df = fp_df[['Player', 'FPTS']]
    fp_df.columns = ['name', 'points']
    fp_df['name'] = fp_df['name'].str.strip()
    fp_df['name'] = fp_df['name'].apply(remove_team_abb)
    return fp_df

def merge_df(df, fp_df):
    # combine the Fantasy Pros dataframe with the OwnersBox one
    df.set_index('name', inplace=True)
    fp_df.set_index('name', inplace=True)
    merged = df.join(fp_df)
    merged.dropna(inplace=True)
    merged.sort_values(by=['salary'], ascending=False, inplace=True)
    return merged

def setup_rotowire_df(format):
    # retrieve the OwnersBox DFS information from Rotowire table
    html = selenium_scrape_html(ROTOWIRE_BASE_URL + format)

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
    df = pd.DataFrame(d).T.reset_index()
    df.columns = ['name', 'team', 'position', 'salary']
    return df

def setup_yahoo_df():
    jsonurl = urlopen(YAHOO_API_ENDPOINT)
    text = json.loads(jsonurl.read())

    df = pd.DataFrame(text['players']['result'])
    df = df[df.gameStartTime.str.startswith('Sun')]
    df.drop(['sport', 'playerCode', 'gameCode', 'homeTeam', 'awayTeam', 'gameStartTime'], axis=1, inplace=True)
    df['name'] = df['name'].str.strip()
    df.rename(columns = {'fppg':'yahoo'}, inplace=True)
    df.sort_values(by=['salary'], ascending=False, inplace=True)
    return df

def main():
    df = []
    format = 'yahoo'
    if len(sys.argv) == 2:
        if sys.argv[1] == '--ownersbox' or sys.argv[1] == '-o':
            format = 'ownersbox'
            df = setup_rotowire_df(format)
        elif sys.argv[1] == '--yahoo' or sys.argv[1] == '-y':
            df = setup_yahoo_df()
    else: # default to Yahoo DFS
        df = setup_yahoo_df()
    fp_df = setup_fp_df()
    merged = merge_df(df, fp_df)
    write_data(merged, format)

if __name__ == "__main__":
    main()
