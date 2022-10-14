# Daily Fantasy Helper (NFL)

## What is it?

This repository contains a couple of Python scripts that automate the creation of daily fantasy football rosters. Designed to maximize the provided raw data, this application was created with 1v1 and small contests in mind.

Currently supports Yahoo main slate Sunday matches and OwnersBox Thursday thru Monday games.

## How to use:

`> python fetch_data.py <format>`

`> python dfs-solver.py <file> <format>`

Where format is either `--ownersbox` || `-o`, or `--yahoo` || `-y`. If not specified it will default to Yahoo format.

Where file is the path to the rawdata `.csv` file. 

## Example output:
```
                     name position team  salary  points
4         Patrick Mahomes       QB   KC    36.0    23.7
32           Keenan Allen       WR  LAC    26.0    16.2
34           James Conner       RB  PIT    26.0    16.5
46          Darren Waller       TE   LV    23.0    13.1
53         Terry McLaurin       WR  WAS    22.0    14.4
56         Todd Gurley II       RB  ATL    21.0    14.0
110        Robby Anderson       WR  CAR    19.0    13.2
140      David Montgomery       RB  CHI    16.0    13.5
219  Jacksonville Jaguars      DEF  JAX    11.0     6.3
Total used amount of salary cap: 200.0
Projected points: 130.9
```

## Past Achievements
### 2021

![2021](https://user-images.githubusercontent.com/10425301/195481619-48b12822-7c6a-4bd4-a84a-4b0e32d80f1d.png)

Yahoo Diamond Rank (99th Percentile)

Placed 504/223186 in the 2021 Yahoo cup.

### 2020

![2020](https://user-images.githubusercontent.com/10425301/124058137-c974f680-d9f6-11eb-9a15-3876a86e101e.png)

Yahoo Diamond Rank (95th Percentile)

Placed 972/142,492 in the BetMGM 2020 Yahoo Cup