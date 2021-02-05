# Curriculum-guided Hindsight Experience Replay

## What is the Problem?
  - In sparse reward settings, it is difficult for agent to collect sufficient successful trajectories to learn from.

## Summary
  - Hindsight experience replay (HER) enables an agent to learn from failure by treating the final state of a failed trajectory as a pseudo goal. The authors propose Curriculum-guided HER (CHER), an extension of HER which selectively chooses the pseudo-goals to use based on goal-proximity and diversity objectives.

## Key Insights
  - HER samples from failed experiences uniformly; CHER proposes selective sampling based on 1) proximity to desired goals and 2) diversity based on curiosity to encourage exploration
  - Formulated as a combinatorial optimization problem to find subset of goals that maximizes objective function
  - Solving the optimization problem is NP-hard, compute near-optimal solution with greedy approach instead

## Limitations/Weaknesses
  - Selection depends on the definition of a similarity/distance function to measure likeness of goals. This will vary depending on the environment and task and thus requires injecting domain knowledge.
  - Evaluating the utility function is an expensive operation, scales with the size of replay buffer

## Summary of Key Results
  - CHER balances exploration and exploitation by selectively inserting psuedo goals based on proximity and diversity objectives. By adaptively controlling the weighting for each criteria, CHER induces a curriculum that enables faster learning.
  - Demonstrated good results on some continuous control robotics task with sparse reward as compared to other HER-based approaches and reported ablation results of varying lambda

## Open Questions