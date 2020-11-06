package com.umestudios.dfsoptaplanner.solver;

import com.umestudios.dfsoptaplanner.domain.Player;
import com.umestudios.dfsoptaplanner.domain.Roster;

import org.optaplanner.core.api.score.buildin.hardsoft.HardSoftScore;
import org.optaplanner.core.api.score.stream.Constraint;
import org.optaplanner.core.api.score.stream.ConstraintCollectors;
import org.optaplanner.core.api.score.stream.ConstraintFactory;
import org.optaplanner.core.api.score.stream.ConstraintProvider;

public class DFSConstraintProvider implements ConstraintProvider {

    @Override
    public Constraint[] defineConstraints(ConstraintFactory constraintFactory) {
        return new Constraint[] {
            maxSalary(constraintFactory),
            maxPoints(constraintFactory)
        };
    }

    /**
     * Hard Constraints
     */
    private Constraint maxSalary(ConstraintFactory constraintFactory) {
        return constraintFactory.from(Player.class).filter(i -> i.getSelected())
                .groupBy(ConstraintCollectors.sum(i -> i.getSalary())).join(Roster.class)
                .filter((ws, k) -> ws > k.getMaxSalary())
                .penalize("Max Salary", HardSoftScore.ONE_HARD, (ws, k) -> ws - k.getMaxSalary());
    }

     /**
      * Soft Constraints
      */
    private Constraint maxPoints(ConstraintFactory constraintFactory) {
        return constraintFactory.from(Player.class)
                .filter(Player::getSelected)
                .reward("Max Points", HardSoftScore.ONE_SOFT, Player::getPoints);
    }
}