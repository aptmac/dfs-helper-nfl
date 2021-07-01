# Daily Fantasy Helper

## What is it?

This repository contains a couple of Python scripts that automate the creation of daily fantasy football rosters.

## How to use:

`> python fetch_data.py`

`> python dfs-solver.py <file>`

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

## Does it work?

### Post 2020 season thoughts ..

After using this for the remainder of the 2020 season, yes it works. As I mentioned below back in November 2020 I noticed that the Yahoo projected points were terrible, and that trend continued. The Fantasy Pros projected scores however were quite good, and I ran their projections into the solver without modifications for the rest of the season. I ended up winning ~70% of the contests I entered, which was actually enough to be Diamond rank (top 5%) on Yahoo DFS.

### Mid 2020 season (November) thoughts..

Yeah, kind of.

The Yahoo projected points are hot garbage, so I wouldn't advice using them.

The Fantasy Pros ones are great out of the box. I went undefeated in the Yahoo DFS placement matches, and have since won a couple of larger paid contests and for-money head-to-head matches. The coolest win so far has been in the BetMGM Yahoo Cup, which is a free to enter contest and only awards money to the top scorers. I placed 972 out of 142,492 which ended up giving me a whopping $1, but free money is free money and that placement was very cool!