#!/usr/bin/python3

from datetime import datetime
from pathlib import Path
import pandas as pd
import os, pulp, sys

def open_csv():
    players = pd.read_csv(sys.argv[1])
    players = players.loc[:, ~players.columns.str.contains('^Unnamed')]
    return players

def define_problem(players, format):
    players["QB"] = (players["position"] == "QB").astype(float)
    players["RB"] = (players["position"] == "RB").astype(float)
    players["WR"] = (players["position"] == "WR").astype(float)
    players["TE"] = (players["position"] == "TE").astype(float)
    players["DST"] = (players["position"] == "DEF").astype(float)
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
        dst[decision_var] = player["DST"]
        num_players[decision_var] = 1.0

    objective_function = pulp.LpAffineExpression(total_points)
    model += objective_function

    total_cost = pulp.LpAffineExpression(cost)
    QB_constraint = pulp.LpAffineExpression(qb)
    RB_constraint = pulp.LpAffineExpression(rb)
    WR_constraint = pulp.LpAffineExpression(wr)
    TE_constraint = pulp.LpAffineExpression(te)
    DST_constraint = pulp.LpAffineExpression(dst)
    total_players = pulp.LpAffineExpression(num_players)

    if format == 'ownersbox':
        model += (total_cost <= 50000)
        # 1QB, 2RB, 2WR, 1TE, 2 Flex, 1 SuperFlex
        model += (QB_constraint <= 2)
        model += (RB_constraint <= 4) # Can have up to 4
        model += (RB_constraint >= 2) # ..but must have 2
        model += (WR_constraint <= 4)
        model += (WR_constraint >= 2)
        model += (TE_constraint <= 3)
        model += (TE_constraint >= 1)
        model += (total_players == 9)
    else:
        model += (total_cost <= 200)
        model += (QB_constraint == 1)
        model += (RB_constraint <= 3)
        model += (WR_constraint <= 4)
        model += (TE_constraint == 1)
        model += (DST_constraint == 1)
        model += (total_players == 9)
    return model

def solve(players, model):
    model.solve(pulp.PULP_CBC_CMD(msg=False))
    players["is_drafted"] = 0.0

    for var in model.variables():
        players.iloc[int(var.name[1:]), players.columns.get_loc('is_drafted')] = var.varValue

    my_team = players[players["is_drafted"] == 1.0]
    my_team = my_team[["name", "position", "team", "salary", "points"]]
    return my_team

def write_results_to_console(results):
    print(results)
    print("Total used amount of salary cap: {}".format(results["salary"].sum()))
    print("Projected points: {}".format(results["points"].sum().round(1)))

def write_results_to_json(results, format):
    if not os.path.exists('./results'):
        os.makedirs('./results')
    results.to_json('./results/' + format + '-' + datetime.now().strftime("%d-%m-%Y-%Hh%Mm%Ss") + '.json', indent=2, orient='table')

def main():
    # At the moment, default to Yahoo and opt-in to OwnersBox by using args
    format = 'yahoo'
    if len(sys.argv) == 2:
        if Path(sys.argv[1]).stem == 'ownersbox':
            format = 'ownersbox'
    if len(sys.argv) == 3: 
        if sys.argv[2] == '--ownersbox' or sys.argv[2] == '-o':
            format = 'ownersbox'
    players = open_csv()
    model = define_problem(players, format)
    results = solve(players, model)
    write_results_to_console(results)
    write_results_to_json(results, format)

if __name__ == "__main__":
    main()
