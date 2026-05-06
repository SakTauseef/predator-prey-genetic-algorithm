"""
evolution.py — Genome representation, fitness scoring, and evolutionary operators.

Each agent carries a genome: a list of float values (genes) that control
its behavioural tendencies.  When an agent reproduces, we use crossover
and mutation to produce a child genome.
"""

import random                          # random: used for mutation and crossover rolls
import math                            # math: used in fitness normalisation
from config import Config              # simulation constants


# ── Genome gene indices (makes code readable) ────────────────────────────────
GENE_SPEED        = 0    # multiplier applied to base movement speed  (0.5–1.5)
GENE_AGGRESSION   = 1    # for predators: how hard they chase; prey: how far they flee
GENE_RISK_TOL     = 2    # willingness to take risky short routes (SA temperature bias)
GENE_SENSE_MULT   = 3    # multiplier on sensing radius  (0.5–1.5)
GENE_REPRO_DRIVE  = 4    # energy threshold modifier — lower = reproduces sooner
GENE_SOCIAL       = 5    # PSO social weight bias — higher = follows the swarm more


def random_genome():
    """Return a fresh randomised genome list."""
    return [random.uniform(0.5, 1.5) for _ in range(Config.GENOME_SIZE)]
    # each gene is a float in [0.5, 1.5]: a multiplier around the neutral value of 1.0


def crossover(genome_a, genome_b):
    """
    Single-point crossover: pick a random split point, take the first
    portion from parent A and the rest from parent B.
    """
    point = random.randint(1, Config.GENOME_SIZE - 1)   # split point (not at edges)
    child = genome_a[:point] + genome_b[point:]          # splice the two halves
    return child


def mutate(genome):
    """
    Iterate over each gene and, with probability MUTATION_RATE, add a
    small random perturbation.  Clamp the result to [0.1, 2.0] so genes
    never go degenerate.
    """
    mutated = genome[:]                                  # copy so original is unchanged
    for i in range(len(mutated)):
        if random.random() < Config.MUTATION_RATE:      # roll for mutation
            delta = random.uniform(
                -Config.MUTATION_STRENGTH,
                 Config.MUTATION_STRENGTH
            )                                            # small positive or negative nudge
            mutated[i] = max(0.1, min(2.0, mutated[i] + delta))  # clamp to safe range
    return mutated


def reproduce(parent_a, parent_b):
    """
    Produce one child genome from two parent genomes via crossover then mutation.
    Used whenever two agents have enough energy to reproduce.
    """
    child_genome = crossover(parent_a.genome, parent_b.genome)   # mix parents
    child_genome = mutate(child_genome)                            # add variation
    return child_genome


def compute_fitness_prey(agent):
    """
    Prey fitness formula:
        fitness = (energy * survival_ticks) / (times_chased + 1)

    Rewards prey that accumulate energy AND stay alive AND avoid predators.
    The +1 in the denominator prevents division-by-zero.
    """
    return (agent.energy * agent.age) / (agent.times_chased + 1)


def compute_fitness_predator(agent):
    """
    Predator fitness formula:
        fitness = (kills * energy_gained_from_kills) / (energy_spent + 1)

    Rewards predators that hunt efficiently — many kills with low energy cost.
    """
    return (agent.kills * Config.PREY_KILL_ENERGY) / (agent.energy_spent + 1)


def select_parents(population):
    """
    Tournament selection: randomly pick 4 candidates, return the best 2.
    This gives fitter agents a higher reproduction chance without being elitist.
    Returns (parent_a, parent_b) or None if the population is too small.
    """
    if len(population) < 2:
        return None, None                                # can't reproduce with < 2 agents

    # pick 4 random candidates (with replacement allowed if pop is small)
    candidates = random.choices(population, k=min(4, len(population)))

    # sort by fitness descending; take the top two
    if hasattr(candidates[0], 'kills'):                  # predator check
        candidates.sort(key=compute_fitness_predator, reverse=True)
    else:
        candidates.sort(key=compute_fitness_prey, reverse=True)

    return candidates[0], candidates[1]                  # two fittest from the tournament