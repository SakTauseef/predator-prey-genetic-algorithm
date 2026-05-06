"""
simulated_annealing.py — Simulated Annealing for tactical route / target decisions.

SA helps agents avoid local optima when choosing between competing options.
At high temperature the agent is "adventurous" — it may accept a worse option.
As temperature cools it becomes purely greedy (exploitative).

Each agent owns a personal SAState object that tracks its temperature.
"""

import math                        # math.exp for the acceptance probability formula
import random                      # random.random for probabilistic acceptance
from config import Config          # SA_INITIAL_TEMP, SA_COOLING_RATE, SA_MIN_TEMP


class SAState:
    """
    Holds the temperature for one agent's SA process.
    Call .cool() each tick to decay the temperature.
    Call .heat() when the agent should explore more (no threat / no prey).
    """

    def __init__(self, initial_temp=None):
        self.initial_temp = initial_temp if initial_temp else Config.SA_INITIAL_TEMP
        self.temperature  = self.initial_temp

    def cool(self):
        """Lower the temperature by the cooling rate, but not below SA_MIN_TEMP."""
        self.temperature = max(
            Config.SA_MIN_TEMP,
            self.temperature * Config.SA_COOLING_RATE
        )

    def heat(self, amount=None):
        """
        Raise the temperature to encourage exploration.
        Called when:
          - Prey detects no nearby predators (safe to explore boldly)
          - Predator sees no prey in range (needs to search more widely)

        amount — optional override; defaults to half of this agent's initial temp.
        Capped at the agent's own initial_temp so it never exceeds its starting value.
        """
        boost = amount if amount is not None else self.initial_temp * 0.5
        self.temperature = min(self.initial_temp, self.temperature + boost)

    def accept(self, current_score, candidate_score):
        """
        Decide whether to accept a candidate solution over the current one.

        If candidate is BETTER (higher score) → always accept.
        If candidate is WORSE  → accept with probability e^(delta / temperature).
          - At high temperature: almost always accept (explore).
          - At low  temperature: almost never accept (exploit best known).

        Returns True if we should move to the candidate.
        """
        if candidate_score >= current_score:
            return True                            # better or equal — always accept

        delta = candidate_score - current_score    # negative value (candidate is worse)
        probability = math.exp(delta / max(self.temperature, 1e-6))  # Boltzmann acceptance
        return random.random() < probability       # accept with that probability


# ── SA-based decision helpers ────────────────────────────────────────────────

def sa_choose_target(agent, candidates, score_fn):
    """
    Given a list of candidate targets (could be food patches, prey, etc.),
    use SA to pick one.

    score_fn(agent, candidate) → float: higher = more desirable target.

    Returns the chosen candidate, or None if the list is empty.
    """
    if not candidates:
        return None

    # Start with a random candidate as the "current" solution
    current = random.choice(candidates)
    current_score = score_fn(agent, current)

    # Run SA iterations — more iterations at high temperature = more exploration
    iterations = max(5, int(agent.sa_state.temperature * 20))

    for _ in range(iterations):
        candidate = random.choice(candidates)                  # random neighbour
        candidate_score = score_fn(agent, candidate)

        if agent.sa_state.accept(current_score, candidate_score):
            current       = candidate                          # move to new solution
            current_score = candidate_score

    agent.sa_state.cool()      # cool after every decision cycle
    return current


# ── Scoring helpers used by SA ───────────────────────────────────────────────

def score_food_for_prey(prey, food):
    """
    Score a food item for a prey agent.
    Closer food is better.
    """
    import math as _m
    dist = _m.hypot(prey.x - food.x, prey.y - food.y)
    base = -dist                       # closer = less negative = higher score
    return base


def score_prey_for_predator(predator, prey):
    """
    Score a prey agent as a target for a predator.
    Closer prey is better; energy-rich prey gives a bigger reward.
    """
    import math as _m
    dist = _m.hypot(predator.x - prey.x, predator.y - prey.y)
    base = -dist                       # closer = higher score
    energy_bonus = prey.energy * 0.05  # prefer energy-rich prey (bigger reward)
    return base + energy_bonus