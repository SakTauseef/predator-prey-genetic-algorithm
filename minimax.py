"""
minimax.py — Minimax algorithm with alpha-beta pruning.

Both prey (minimiser) and predator (maximiser) use this to choose
the best movement direction over a short lookahead horizon.

The "game state" here is lightweight: just positions and a depth counter.
We avoid simulating the full world state for performance reasons.
"""

import math                        # math: for distance calculation
from config import Config          # constants (MINIMAX_DEPTH, CATCH_RADIUS, etc.)


# ── Direction vectors the agents can choose from ─────────────────────────────
# Each is a (dx, dy) unit step.  We allow 8 compass directions + standing still.
DIRECTIONS = [
    ( 1,  0), (-1,  0), ( 0,  1), ( 0, -1),   # cardinal: E W S N
    ( 1,  1), (-1,  1), ( 1, -1), (-1, -1),   # diagonal: SE SW NE NW
    ( 0,  0),                                   # stay in place
]


def distance(ax, ay, bx, by):
    """Euclidean distance between two points."""
    return math.hypot(ax - bx, ay - by)


# ── Evaluation functions ─────────────────────────────────────────────────────

def evaluate_for_predator(pred_x, pred_y, prey_x, prey_y):
    """
    Static evaluation from the predator's perspective.
    Higher score = closer to prey = better for predator.
    Score is the negative distance — predator wants to MINIMISE distance.
    """
    dist = distance(pred_x, pred_y, prey_x, prey_y)
    if dist < Config.CATCH_RADIUS:
        return 10000           # caught! maximum reward
    return -dist               # closer = less negative = higher score


def evaluate_for_prey(prey_x, prey_y, pred_x, pred_y):
    """
    Static evaluation from the prey's perspective.
    Higher score = farther from predator = better for prey.
    """
    dist = distance(prey_x, prey_y, pred_x, pred_y)
    if dist < Config.CATCH_RADIUS:
        return -10000          # caught! maximum penalty
    return dist                # farther = more positive = higher score


# ── Core minimax with alpha-beta pruning ─────────────────────────────────────

def minimax_predator(pred_x, pred_y, prey_x, prey_y,
                     depth, alpha, beta, is_predator_turn, speed):
    """
    Minimax from the predator's perspective (maximiser).
    Predator moves to MAXIMISE score; prey moves to MINIMISE it.

    Parameters:
        pred_x/y        — current predator position
        prey_x/y        — current prey position (best-guess target)
        depth           — remaining search depth
        alpha           — best score the maximiser (predator) can guarantee
        beta            — best score the minimiser (prey) can guarantee
        is_predator_turn — whose turn it is in the lookahead
        speed           — step size in pixels per move
    """
    # ── Base case: depth exhausted or prey caught ─────────────────────
    # Return a default direction (1,0) instead of None so callers can
    # always safely unpack the tuple regardless of pruning outcome.
    if depth == 0 or distance(pred_x, pred_y, prey_x, prey_y) < Config.CATCH_RADIUS:
        return evaluate_for_predator(pred_x, pred_y, prey_x, prey_y), (1, 0)

    best_dir = DIRECTIONS[0]           # fallback direction

    if is_predator_turn:
        # Predator is the MAXIMISER — pick the move with the highest score
        best_val = -math.inf

        for dx, dy in DIRECTIONS:
            # Clamp new position to arena bounds
            nx = max(0, min(Config.SIM_WIDTH,  pred_x + dx * speed))
            ny = max(0, min(Config.SIM_HEIGHT, pred_y + dy * speed))

            # Recurse: prey moves next (not predator turn)
            val, _ = minimax_predator(
                nx, ny, prey_x, prey_y,
                depth - 1, alpha, beta, False, speed
            )

            if val > best_val:
                best_val = val         # found a better move
                best_dir  = (dx, dy)

            alpha = max(alpha, best_val)   # update alpha bound
            if beta <= alpha:
                break                      # beta cut-off — prune remaining branches

        return best_val, best_dir

    else:
        # Prey is the MINIMISER — pick the move that minimises predator score
        best_val = math.inf

        for dx, dy in DIRECTIONS:
            nx = max(0, min(Config.SIM_WIDTH,  prey_x + dx * speed))
            ny = max(0, min(Config.SIM_HEIGHT, prey_y + dy * speed))

            val, _ = minimax_predator(
                pred_x, pred_y, nx, ny,
                depth - 1, alpha, beta, True, speed
            )

            if val < best_val:
                best_val = val
                best_dir  = (dx, dy)

            beta = min(beta, best_val)     # update beta bound
            if beta <= alpha:
                break                      # alpha cut-off — prune

        return best_val, best_dir


def get_predator_move(predator, nearest_prey):
    """
    Public API: given a predator agent and its nearest prey agent,
    return the (dx, dy) direction the predator should move this tick.
    """
    if nearest_prey is None:
        return (0, 0)          # no prey visible — stand still

    _, best_dir = minimax_predator(
        predator.x, predator.y,
        nearest_prey.x, nearest_prey.y,
        depth=Config.MINIMAX_DEPTH,
        alpha=-math.inf,
        beta=math.inf,
        is_predator_turn=True,
        speed=predator.speed
    )
    return best_dir if best_dir is not None else (1, 0)  # never return None


def get_prey_evasion_move(prey, nearest_predator):
    """
    Public API: given a prey agent and its nearest predator,
    return the (dx, dy) direction the prey should move to evade.

    We call minimax from the prey's point of view — prey minimises the
    predator's score (i.e., maximises distance).
    """
    if nearest_predator is None:
        return (0, 0)          # no threat — no evasion needed

    _, best_dir = minimax_predator(
        nearest_predator.x, nearest_predator.y,
        prey.x, prey.y,
        depth=Config.MINIMAX_DEPTH,
        alpha=-math.inf,
        beta=math.inf,
        is_predator_turn=False,   # prey is moving first (minimiser)
        speed=prey.speed
    )
    return best_dir if best_dir is not None else (0, 1)  # never return None