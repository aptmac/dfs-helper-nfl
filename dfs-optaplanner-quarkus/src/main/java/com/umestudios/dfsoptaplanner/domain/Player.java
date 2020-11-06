package com.umestudios.dfsoptaplanner.domain;

import org.optaplanner.core.api.domain.entity.PlanningEntity;
import org.optaplanner.core.api.domain.variable.PlanningVariable;

/**
 * Player
 */
@PlanningEntity
public class Player {

    private String name;

    private String position;

    private String team;

    private int salary;

    private float points;

    @PlanningVariable(valueRangeProviderRefs = "selected")
    private Boolean selected;

    public Player() {
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getPosition() {
        return position;
    }

    public void setPosition(String position) {
        this.position = position;
    }

    public String getTeam() {
        return team;
    }

    public void setTeam(String team) {
        this.team = team;
    }

    public int getSalary() {
        return salary;
    }

    public void setSalary(int salary) {
        this.salary = salary;
    }

    public int getPoints() {
        return (int) points;
    }

    public void setPoints(float points) {
        this.points = points;
    }

    public Boolean getSelected() {
        return selected;
    }

    public void setSelected(Boolean selected) {
        this.selected = selected;
    }
}