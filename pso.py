"""
pso.py — Particle Swarm Optimisation for group navigation.

PSO gives agents "swarm memory": each agent tracks its personal best
position and the swarm's global best position, biasing movement toward
known good areas (food patches for prey, prey clusters for predators).

Each group (all prey / all predators) shares a SwarmMemory instance.
Each individual agent has a PSOParticle that stores its velocity and
personal best.
"""

import random                      # random.uniform for stochastic velocity updates
import math                        # math.hypot for distance checks
from config import Config          # PSO_INERTIA, PSO_COGNITIVE, PSO_SOCIAL


class PSOParticle:
    """
    Velocity state for one agent acting as a PSO particle.
    Stored on each agent object.
    """

    def __init__(self):
        self.vx = random.uniform(-1, 1)    # initial x velocity (pixels/tick)
        self.vy = random.uniform(-1, 1)    # initial y velocity (pixels/tick)
        self.best_x = None                  # personal best position (x)
        self.best_y = None                  # personal best position (y)
        self.best_score = -float('inf')     # score at the personal best position


class SwarmMemory:
    """
    Shared memory across all agents of the same species.
    Stores the global best position found by ANY agent in the swarm.
    """

    def __init__(self):
        self.global_best_x = None          # x of the swarm's best known location
        self.global_best_y = None          # y of the swarm's best known location
        self.global_best_score = -float('inf')  # score at that location

    def update(self, x, y, score):
        """
        Agents call this whenever they discover a position worth recording.
        Updates the global best if the new score is higher.
        """
        if score > self.global_best_score:
            self.global_best_score = score
            self.global_best_x     = x
            self.global_best_y     = y


def pso_velocity_update(particle, agent_x, agent_y, swarm_memory, genome):
    """
    Update a particle's velocity using the standard PSO formula:

        v_new = inertia * v_old
              + cognitive * r1 * (personal_best - current)
              + social    * r2 * (global_best   - current)

    The genome's GENE_SOCIAL value biases how much the agent follows the
    swarm vs. its own memory.

    Returns the updated (vx, vy).
    """
    r1 = random.random()           # random weight for cognitive component
    r2 = random.random()           # random weight for social component

    # Genome-based social bias: higher GENE_SOCIAL = follows swarm more
    social_weight = Config.PSO_SOCIAL * genome[5]  # index 5 = GENE_SOCIAL

    # ── Cognitive component (toward personal best) ────────────────────
    if particle.best_x is not None:
        cog_x = Config.PSO_COGNITIVE * r1 * (particle.best_x - agent_x)
        cog_y = Config.PSO_COGNITIVE * r1 * (particle.best_y - agent_y)
    else:
        cog_x = cog_y = 0.0       # no personal best yet — no cognitive pull

    # ── Social component (toward global best) ────────────────────────
    if swarm_memory.global_best_x is not None:
        soc_x = social_weight * r2 * (swarm_memory.global_best_x - agent_x)
        soc_y = social_weight * r2 * (swarm_memory.global_best_y - agent_y)
    else:
        soc_x = soc_y = 0.0       # no global best yet — no social pull

    # ── Apply inertia + combine components ───────────────────────────
    new_vx = Config.PSO_INERTIA * particle.vx + cog_x + soc_x
    new_vy = Config.PSO_INERTIA * particle.vy + cog_y + soc_y

    # ── Clamp velocity so agents don't teleport ───────────────────────
    max_v = 3.0                    # hard cap on velocity magnitude
    speed  = math.hypot(new_vx, new_vy)
    if speed > max_v:
        scale  = max_v / speed
        new_vx *= scale
        new_vy *= scale

    particle.vx = new_vx
    particle.vy = new_vy
    return new_vx, new_vy


def pso_update_personal_best(particle, agent_x, agent_y, score):
    """
    If the agent's current position has a higher score than its recorded
    personal best, update the personal best.
    """
    if score > particle.best_score:
        particle.best_score = score
        particle.best_x     = agent_x
        particle.best_y     = agent_y


# ── Score functions used to evaluate positions ───────────────────────────────

def score_position_prey(x, y, food_list, water_list):
    """
    How good is position (x, y) for a prey agent?
    Score increases near food and water, clipped to nearby items only.
    """
    score = 0.0
    for item in food_list:
        dist = math.hypot(x - item.x, y - item.y)
        if dist < Config.PREY_SENSE_RADIUS:
            score += Config.FOOD_ENERGY / (dist + 1)   # inverse-distance weighting
    for item in water_list:
        dist = math.hypot(x - item.x, y - item.y)
        if dist < Config.PREY_SENSE_RADIUS:
            score += Config.WATER_ENERGY / (dist + 1)
    return score


def score_position_predator(x, y, prey_list):
    """
    How good is position (x, y) for a predator?
    Score increases near prey agents within sensing range.
    """
    score = 0.0
    for prey in prey_list:
        dist = math.hypot(x - prey.x, y - prey.y)
        if dist < Config.PREDATOR_SENSE_RADIUS:
            score += Config.PREY_KILL_ENERGY / (dist + 1)
    return score