package com.umestudios.dfsoptaplanner.solver;

import java.util.UUID;
import java.util.concurrent.ExecutionException;

import javax.inject.Inject;
import javax.ws.rs.Consumes;
import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;


import com.umestudios.dfsoptaplanner.domain.DFSSolution;

import org.optaplanner.core.api.solver.SolverJob;
import org.optaplanner.core.api.solver.SolverManager;

@Path("/dfs")
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
public class DFSResource {

    @Inject
    private SolverManager<DFSSolution, UUID> solverManager;

    @POST
    @Path("/solve")
    public DFSSolution solve(DFSSolution problem) {
        UUID problemId = UUID.randomUUID();
        // Submit the problem to start solving
        SolverJob<DFSSolution, UUID> solverJob = solverManager.solve(problemId, problem);
        DFSSolution solution;
        try {
            // Wait until the solving ends
            solution = solverJob.getFinalBestSolution();
        } catch (InterruptedException | ExecutionException e) {
            throw new IllegalStateException("Solving failed.", e);
        }
        return solution;
    }

    @GET
    @Produces(MediaType.TEXT_PLAIN)
    public String hello() {
        return "hello";
    }
}