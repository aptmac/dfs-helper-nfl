#!/usr/bin/python3

from bs4 import BeautifulSoup
from urllib.request import urlopen
import csv
import io
import glob, os
import json
import numpy as np
import pandas as pd
import re

FP_BASE_URL = 'https://www.fantasypros.com/nfl/projections/{}.php?&scoring=HALF'
MAX_SALARY = 200
GAME_DAY = 'Sun'

# Fantasy Pros player names include the abbreviation of their team; it needs to be removed
def strip_team_abb(name):
    # For some reason Patrick Mahomes has "II" in FP but not Yahoo, and they must be the same for merging dataframes
    # if player == "Patrick Mahomes II KC":
    #     return "Patrick Mahomes"
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

def main():
    # # retrieve the Yahoo DFS information from API
    print('--- (1/4) Retrieving data from Yahoo API ---')
    url = "https://dfyql-ro.sports.yahoo.com/v2/external/playersFeed/nfl"
    jsonurl = urlopen(url)
    text = json.loads(jsonurl.read())

    # setup a dataframe with Yahoo DFS data and write to json
    print('--- (2/4) Processing Yahoo data ---')
    yh_df = pd.DataFrame(text['players']['result'])
    yh_df = yh_df[yh_df.gameStartTime.str.startswith(GAME_DAY)]
    yh_df.drop(['sport', 'playerCode', 'gameCode', 'homeTeam', 'awayTeam', 'gameStartTime'], axis=1, inplace=True)
    yh_df['name'] = yh_df['name'].str.strip()
    yh_df.rename(columns = {'fppg':'yahoo'}, inplace=True)
    yh_df.sort_values(by=['salary'], ascending=False, inplace=True)
    yh_df.rename(columns = {'yahoo':'points'}).to_csv('./csv/yahoo.csv', encoding='utf-8', index=True)
    if not os.path.exists('./json'):
        os.makedirs('./json')
    yh_df.rename(columns = {'yahoo':'points'}).to_json('./json/yahoo.json', orient='table')

    # setup a dataframe with Fantasy Pros positional data
    print('--- (3/4) Fetching the Fantasy Pros data ---')
    fp_df = fetch_fp_data()
    fp_df = fp_df[['Player', 'FPTS']]
    fp_df.columns = ['name', 'points']
    fp_df['name'] = fp_df['name'].str.strip()
    fp_df['name'] = fp_df['name'].apply(strip_team_abb)

    # combine the Fantasy Pros dataframe with the Yahoo one
    yh_df.set_index('name', inplace=True)
    fp_df.set_index('name', inplace=True)
    merged = yh_df.join(fp_df)
    merged.dropna(inplace=True)
    merged.drop(['yahoo'], axis=1, inplace=True)
    merged.sort_values(by=['salary'], ascending=False, inplace=True)

    # save Fantasy Pros data with the Yahoo salaries intact
    merged.to_csv('./csv/fantasypros.csv', encoding='utf-8', index=True)
    merged.to_json('./json/fantasypros.json', orient='table')

    # format the json files to comply nicely with external tooling
    print('--- (4/4) Cleaning up JSON files for external use ---')
    for format in ['yahoo', 'fantasypros']:
        f = open('./json/' + format + '.json', 'r')
        data = json.load(f)
        f.close()

        # remove the dataframe generate schema
        del data['schema']

        # add a "roster" section with details about the roster requirements
        data['roster'] = {'maxSalary' : MAX_SALARY}

        # change the "data" attribute name to "players"
        data['players'] = data.pop('data')

        # write the files back
        with open('./json/' + format + '.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    print('--- Completed ---')

if __name__ == "__main__":
    main()
