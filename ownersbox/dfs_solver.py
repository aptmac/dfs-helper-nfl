#!/usr/bin/python3

import pandas as pd
import pulp
import sys

print('--- (1/4) Defining the problem ---')
players = pd.read_csv(sys.argv[1])

players = players.loc[:, ~players.columns.str.contains('^Unnamed')]

players["QB"] = (players["position"] == "QB").astype(float)
players["RB"] = (players["position"] == "RB").astype(float)
players["WR"] = (players["position"] == "WR").astype(float)
players["TE"] = (players["position"] == "TE").astype(float)
players["salary"] = players["salary"].astype(float)

model = pulp.LpProblem("DFS", pulp.LpMaximize)

total_points = {}
cost = {}
qb = {}
rb = {}
wr = {}
te = {}
dst = {}
num_players = {}

vars = []

for i, player in players.iterrows():
    var_name = 'x' + str(i)
    decision_var = pulp.LpVariable(var_name, cat='Binary')
    vars.append(decision_var)

    total_points[decision_var] = player["points"]
    cost[decision_var] = player["salary"]

    qb[decision_var] = player["QB"]
    rb[decision_var] = player["RB"]
    wr[decision_var] = player["WR"]
    te[decision_var] = player["TE"]
    num_players[decision_var] = 1.0

objective_function = pulp.LpAffineExpression(total_points)
model += objective_function

total_cost = pulp.LpAffineExpression(cost)
model += (total_cost <= 50000)

print('--- (2/4) Defining the constraints ---')
QB_constraint = pulp.LpAffineExpression(qb)
RB_constraint = pulp.LpAffineExpression(rb)
WR_constraint = pulp.LpAffineExpression(wr)
TE_constraint = pulp.LpAffineExpression(te)
total_players = pulp.LpAffineExpression(num_players)

# 1QB, 2RB, 2WR, 1TE, 2 Flex, 1 SuperFlex
model += (QB_constraint <= 2)
model += (RB_constraint <= 4) # Can have up to 4
model += (RB_constraint >= 2) # ..but must have 2
model += (WR_constraint <= 4)
model += (WR_constraint >= 2)
model += (TE_constraint <= 3)
model += (TE_constraint >= 1)
model += (total_players == 9)

print('--- (3/4) Solving the problem ---')
model.solve()

print('--- (4/4) Formatting the results ---')
players["is_drafted"] = 0.0

for var in model.variables():
    players.iloc[int(var.name[1:]), players.columns.get_loc('is_drafted')] = var.varValue

my_team = players[players["is_drafted"] == 1.0]
my_team = my_team[["name", "position", "team", "salary", "points"]]

print(my_team)
print("Total used amount of salary cap: {}".format(my_team["salary"].sum()))
print("Projected points: {}".format(my_team["points"].sum().round(1)))
print('--- Completed ---')