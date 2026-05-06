"""
config.py — All simulation constants and tuning parameters.
Change values here to experiment with different behaviours.
"""

class Config:
    # ── Window layout ────────────────────────────────────────────────────
    SIM_WIDTH       = 900          # pixel width of the simulation arena
    SIM_HEIGHT      = 700          # pixel height of the simulation arena
    GRAPH_WIDTH     = 380          # pixel width of the right-hand graph panel
    WINDOW_WIDTH    = SIM_WIDTH + GRAPH_WIDTH   # total window width
    WINDOW_HEIGHT   = SIM_HEIGHT                # total window height
    FPS             = 30         # frames per second cap

    # ── Simulation lifetime ──────────────────────────────────────────────
    MAX_GENERATIONS = 50           # simulation stops after this many generations
    TICKS_PER_GEN   = 300          # number of update ticks that count as one generation

    # ── Population starting sizes ────────────────────────────────────────
    INITIAL_PREY      = 10         # how many prey agents spawn at the start
    INITIAL_PREDATORS = 10          # how many predator agents spawn at the start
    MAX_PREY          = 10000   #None      # population cap for prey (prevents explosion)
    MAX_PREDATORS     = 10000   #none     # population cap for predators

    # ── Energy ───────────────────────────────────────────────────────────
    PREY_START_ENERGY      = 120   # energy a new prey is born with
    PREDATOR_START_ENERGY  = 150   # energy a new predator is born with
    PREY_METABOLISM        = 0.15  # energy drained from prey each tick (idle cost)
    PREDATOR_METABOLISM    = 0.20  # energy drained from predator each tick
    MOVE_ENERGY_COST       = 0.05  # extra energy cost per pixel moved
    FOOD_ENERGY            = 40    # energy gained by prey eating one food item
    WATER_ENERGY           = 20    # energy gained by drinking water
    PREY_KILL_ENERGY       = 80    # energy a predator gains by catching a prey
    REPRODUCE_ENERGY_PREY  = 180   # prey needs at least this much energy to reproduce
    REPRODUCE_ENERGY_PRED  = 220   # predator needs at least this much energy to reproduce

    # ── Agent movement ───────────────────────────────────────────────────
    PREY_BASE_SPEED     = 2.8      # max pixels per tick a prey can move
    PREDATOR_BASE_SPEED = 3.2      # max pixels per tick a predator can move

    # ── Sensing ──────────────────────────────────────────────────────────
    PREY_SENSE_RADIUS      = 120   # how far (px) prey can detect threats/food
    PREDATOR_SENSE_RADIUS  = 150   # how far (px) predators can detect prey
    CATCH_RADIUS           = 14    # predator catches prey if within this distance

    # ── Food & water spawning ────────────────────────────────────────────
    FOOD_COUNT        = 25         # how many food items exist on the map at once
    WATER_COUNT       = 10         # how many water sources exist on the map
    FOOD_RESPAWN_TICK = 40         # every N ticks, eaten food respawns somewhere new

    # ── Minimax ──────────────────────────────────────────────────────────
    MINIMAX_DEPTH = 3              # lookahead depth (higher = smarter but slower)

    # ── Simulated Annealing ──────────────────────────────────────────────
    SA_INITIAL_TEMP  = 1.0         # starting "temperature" (exploration rate)
    SA_COOLING_RATE  = 0.995       # temperature multiplied by this each decision cycle
    SA_MIN_TEMP      = 0.01        # temperature floor — agent becomes fully greedy

    # ── Particle Swarm Optimisation ──────────────────────────────────────
    PSO_INERTIA    = 0.5           # how much the agent keeps its current velocity
    PSO_COGNITIVE  = 1.5           # pull toward the agent's own best-known position
    PSO_SOCIAL     = 1.5           # pull toward the swarm's global best position

    # ── Evolutionary algorithm ───────────────────────────────────────────
    MUTATION_RATE     = 0.15       # probability that any single gene mutates
    MUTATION_STRENGTH = 0.2        # max change applied when a gene mutates
    GENOME_SIZE       = 6          # number of genes in each agent's genome

    # ── Colours (R, G, B) ────────────────────────────────────────────────
    BG_COLOR         = (15, 20, 30)         # dark navy background
    GRID_COLOR       = (25, 35, 50)         # subtle grid lines
    PREY_COLOR       = (80, 200, 120)       # green circles for prey
    PREDATOR_COLOR   = (220, 70, 70)        # red triangles for predators
    FOOD_COLOR       = (240, 210, 60)       # yellow stars for food
    WATER_COLOR      = (60, 160, 240)       # blue drops for water
    UI_TEXT_COLOR    = (210, 210, 220)      # light text for HUD
    GRAPH_BG         = (20, 25, 38)         # graph panel background
    GRAPH_PREY_LINE  = (80, 200, 120)       # prey population line colour
    GRAPH_PRED_LINE  = (220, 70, 70)        # predator population line colour
    GRAPH_AXIS       = (90, 100, 120)       # axis and grid lines in graph
    PANEL_BORDER     = (50, 65, 90)         # border between sim and graph