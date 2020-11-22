Neuroevolution of Self-Interpretable Agents
GECCO 2020

## What is the Problem?
  - The intuition is to leverage the idea of inattentive blindness to create an informative bottleneck which directs the agent's attention to the relevant parts of the observation.

## Summary
  - Three step architecture: 1) transform input into patches, 2) select the top k patches based on weighting from self-attention and 3) action generation

  - 1) Resize and segment image into patches
  - 2) Self-attention module -> queries and keys, applying softmax turns it into a probability distribution and sum over the columns to get an importance vector
  - 3) Extract patch features, uses spatial information but not the content information. Use LSTM as controller

## Key Insights
  - Self-attention is a promising module for creating RL agents
  - Model has significantly fewer learnable weights compared to other SOTA methods that do well in CarRacing and Doom
  - Interpretable results in pixel space, can visualize the patches that the agent is attending to
  - Use neuroevolution to train agents because there are some operations that are not differentiable
  - Results are generalizable even if the environment is perturbed in certain ways

## Limitations/Weaknesses
  - Generalizability capabilities are limited
  - Fails in the case with two lanes and Youtube video background

## Summary of Key Results
  -

## Open Questions
  -