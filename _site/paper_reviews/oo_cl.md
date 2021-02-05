# Object-Oriented Curriculum Generation for RL

## What is the Problem?
  - Previous methods in building curricula do not take into account the transfer learning method.

## Summary
  - The authors propose a method for automatically generating a graph-based curriculum using object-oriented representations. They also introduce an approach for **automatic source task generation** and for utilizing the curriculum graph via Random Walk.

## Key Insights
  - Object-oriented representation enables better generalization through intuitive task descriptions.
  - Building a curriculum as a graph, rather than ordered list. Building task graph according to **transfer potential** metric.
  - Object-oriented transfer potential metric prioritizes tasks that are:
      - similar to the target task
      - dissimilar from the previously included tasks to avoid redundant knowledge
      - have smaller state space than target task

## Limitations/Weaknesses
  - Proposed method for automatic source task generation, but a human must still validate that the task is solvable
  -

## Summary of Key Results
  -

## Open Questions