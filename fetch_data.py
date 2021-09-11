#!/usr/bin/python3

from bs4 import BeautifulSoup
from urllib.request import urlopen
import csv
import glob, os
import json
import numpy as np
import pandas as pd
import re

# Fantasy Pros player names include the abbreviation of their team; it needs to be removed
def strip_team_abb(name):
    # For some reason Patrick Mahomes has "II" in FP but not Yahoo, and they must be the same for merging dataframes
    # if player == "Patrick Mahomes II KC":
    #     return "Patrick Mahomes"
    player = re.findall('(.*)\s[A-Z]{2,3}', name)
    if player:
        return player[0]
    return name # this will be a DST

# Download all the positional data from Fantasy Pros
def download_fp_csv():
    # Make sure there's a csv folder to store all the data in
    if not os.path.exists('./csv'):
        os.makedirs('./csv')
    # Scrape the Fantasy Pros player score predictions and write them to .csv
    fp_base_url = 'https://www.fantasypros.com/nfl/projections/{}.php?&scoring=HALF'
    for position in ['qb', 'wr', 'rb', 'te', 'dst']:
        pd.read_html(fp_base_url.format(position))[0].to_csv('./csv/' + position + '_fp.csv', index=False)
        if position != 'dst':
            # FIXME: the new Fantasy Pros table has new column headers that throw a wrench into Pandas,
            # this hack of simply removing the first line of the .csv works, but is kind of ugly. 
            # Maybe fix this some day when you're bored ..
            lines = open('./csv/{}_fp.csv'.format(position)).readlines()
            with open('./csv/{}_fp.csv'.format(position), 'w') as f:
                f.writelines(lines[1:])
            f.close()

def main():
    print('--- (1/5) Retrieving data from Fantasy Pros ---')
    download_fp_csv()

    # # retrieve the Yahoo DFS information from API
    print('--- (2/5) Retrieving data from Yahoo API ---')
    url = "https://dfyql-ro.sports.yahoo.com/v2/external/playersFeed/nfl"
    jsonurl = urlopen(url)
    text = json.loads(jsonurl.read())

    # setup a dataframe with Yahoo DFS data and write to json
    print('--- (3/5) Processing Yahoo data ---')
    yh_df = pd.DataFrame(text['players']['result'])
    yh_df = yh_df[yh_df.gameStartTime.str.startswith('Sun')] # for simplicity, only consider the main Sunday DFS contests
    yh_df.drop(['sport', 'playerCode', 'gameCode', 'homeTeam', 'awayTeam', 'gameStartTime'], axis=1, inplace=True)
    yh_df['name'] = yh_df['name'].str.strip()
    yh_df.rename(columns = {'fppg':'yahoo'}, inplace=True)
    yh_df.sort_values(by=['salary'], ascending=False, inplace=True)
    yh_df.rename(columns = {'yahoo':'points'}).to_csv('./csv/yahoo.csv', encoding='utf-8', index=True)
    if not os.path.exists('./json'):
        os.makedirs('./json')
    yh_df.rename(columns = {'yahoo':'points'}).to_json('./json/yahoo.json', orient='table')

    # setup a dataframe with Fantasy Pros positional data
    print('--- (4/5) Processing Fantasy Pros data ---')
    fp_df = pd.concat(map(pd.read_csv, glob.glob(os.path.join('', './csv/*_fp.csv'))), sort=False)
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
    print('--- (5/5) Cleaning up JSON files for external use ---')
    for format in ['yahoo', 'fantasypros']:
        f = open('./json/' + format + '.json', 'r')
        data = json.load(f)
        f.close()

        # remove the dataframe generate schema
        del data['schema']

        # add a "roster" section with details about the roster requirements
        data['roster'] = {'maxSalary' : 200}

        # change the "data" attribute name to "players"
        data['players'] = data.pop('data')

        # write the files back
        with open('./json/' + format + '.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    print('--- Completed ---')

if __name__ == "__main__":
    main()
