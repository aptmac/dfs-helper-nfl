#!/usr/bin/python3

from bs4 import BeautifulSoup
from urllib.request import urlopen
import csv
import glob, os
import json
import numpy as np
import pandas
import re

# Fantasy Pros player names include the abbreviation of their team; it needs to be removed
def strip_team_abb(player):
    # For some reason Patrick Mahomes has "II" in FP but not Yahoo, and they must be the same for merging dataframes
    if player == "Patrick Mahomes II KC":
        return "Patrick Mahomes"
    name = re.findall('(.*)\s[A-Z]{2,3}', player)
    if name:
        return name[0]
    return player

# Download all the positional data from Fantasy Pros
def download_fp_csv():
    # Scrape the Fantasy Pros player score predictions and write them to .csv
    fp_base_url = 'https://www.fantasypros.com/nfl/projections/{}.php?scoring=HALF'
    for position in ['qb', 'wr', 'rb', 'te', 'dst']:
        html_content = urlopen(fp_base_url.format(position)).read()
        soup = BeautifulSoup(html_content, 'lxml')
        table = soup.find('table', id={'data'})
        rows = table.findAll('tr')
        with open(position+'_fp.csv', 'wt+', newline='') as f:
            writer = csv.writer(f)
            header_skipped = False
            for row in rows:
                csv_row = []
                for cell in row.findAll(['td', 'th']):
                    csv_row.append(cell.get_text())
                if header_skipped is False and position != 'dst': # Fantasy Pros tables have an extra row for non-DST
                    header_skipped = True
                    continue
                writer.writerow(csv_row)

def main():
    download_fp_csv()

    # retrieve the Yahoo DFS information from API
    url = "https://dfyql-ro.sports.yahoo.com/v2/external/playersFeed/nfl"
    jsonurl = urlopen(url)
    text = json.loads(jsonurl.read())

    # setup a dataframe with Yahoo DFS data and write to json
    yh_df = pandas.DataFrame(text['players']['result'])
    yh_df = yh_df[yh_df.gameStartTime.str.startswith('Sun')] # for simplicity, only consider the main Sunday DFS contests
    yh_df.drop(['sport', 'playerCode', 'gameCode', 'homeTeam', 'awayTeam', 'gameStartTime'], axis=1, inplace=True)
    yh_df['name'] = yh_df['name'].str.strip()
    yh_df.rename(columns = {'fppg':'yahoo'}, inplace=True)
    yh_df.sort_values(by=['salary'], ascending=False, inplace=True)
    yh_df.rename(columns = {'yahoo':'points'}).to_csv('yahoo.csv', encoding='utf-8', index=True)
    yh_df.rename(columns = {'yahoo':'points'}).to_json('yahoo.json', orient='table')

    # setup a dataframe with Fantasy Pros positional data
    fp_df = pandas.concat(map(pandas.read_csv, glob.glob(os.path.join('', '*_fp.csv'))), sort=False)
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
    merged.to_csv('fantasypros.csv', encoding='utf-8', index=True)
    merged.to_json('fantasypros.json', orient='table')

if __name__ == "__main__":
    main()




