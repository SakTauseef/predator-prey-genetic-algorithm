"""
simulation.py — The main simulation controller.

Owns all agents and resources, runs the per-tick update loop,
handles reproduction and death, manages generation transitions,
and renders everything to the screen.
"""

import random                          # random spawn positions
import pygame                          # rendering
from config import Config              # constants
from agents import Prey, Predator, reset_swarms   # agent classes
from resources import spawn_food, spawn_water      # resource factories
from evolution import reproduce, select_parents    # evolutionary operators
from graph import PopulationGraph                  # live population graph


class Simulation:
    """
    Top-level object that owns the simulation state.
    Call update() each tick, draw() each frame.
    """

    def __init__(self, screen):
        self.screen     = screen
        self.paused     = False
        self.generation = 0
        self.tick       = 0
        self.total_tick = 0
        self.graph      = PopulationGraph()
        self.font_hud   = None
        self.font_big   = None
        self._init_fonts()
        self.reset()

    def _init_fonts(self):
        self.font_hud = pygame.font.SysFont("monospace", 13)
        self.font_big = pygame.font.SysFont("monospace", 22, bold=True)

    # ── Initialisation / reset ────────────────────────────────────────────
    def reset(self):
        """Create a fresh simulation from scratch."""
        reset_swarms()
        self.prey = [
            Prey(
                random.randint(20, Config.SIM_WIDTH  - 20),
                random.randint(20, Config.SIM_HEIGHT - 20)
            )
            for _ in range(Config.INITIAL_PREY)
        ]
        self.predators = [
            Predator(
                random.choice([
                    random.randint(20, 80),
                    random.randint(Config.SIM_WIDTH - 80, Config.SIM_WIDTH - 20)
                ]),
                random.randint(20, Config.SIM_HEIGHT - 20)
            )
            for _ in range(Config.INITIAL_PREDATORS)
        ]
        self.food  = spawn_food(Config.FOOD_COUNT)
        self.water = spawn_water(Config.WATER_COUNT)
        self.generation = 0
        self.tick       = 0
        self.total_tick = 0
        self.graph      = PopulationGraph()

    # ── Per-tick update ───────────────────────────────────────────────────
    def update(self):
        """Advance the simulation by one tick."""
        self.tick       += 1
        self.total_tick += 1

        # ── Update all prey ───────────────────────────────────────────
        for prey in self.prey:
            prey.update(self.predators, self.food, self.water)

        # ── Update all predators ──────────────────────────────────────
        for pred in self.predators:
            pred.update(self.prey)

        # ── Respawn consumed food items ───────────────────────────────
        if self.tick % Config.FOOD_RESPAWN_TICK == 0:
            for item in self.food:
                if item.consumed:
                    item.respawn()

        # ── Remove dead agents ────────────────────────────────────────
        self.prey      = [p for p in self.prey      if p.alive]
        self.predators = [p for p in self.predators if p.alive]

        # ── Reproduction: always attempted, naturally gated by energy ─
        # No hard population cap — population is regulated by energy,
        # predation, and starvation instead.
        self._try_reproduce_prey()
        self._try_reproduce_predators()

        # ── Extinction recovery ───────────────────────────────────────
        # self._prevent_extinction()

        # ── Record population data for the graph ─────────────────────
        new_gen = (self.tick >= Config.TICKS_PER_GEN)
        self.graph.record(
            len(self.prey),
            len(self.predators),
            new_generation=new_gen
        )

        # ── Generation transition ─────────────────────────────────────
        if new_gen:
            self.generation += 1
            self.tick        = 0

    # ── Reproduction helpers ──────────────────────────────────────────────
    def _try_reproduce_prey(self):
        ready = [p for p in self.prey if p.can_reproduce()]
        if len(ready) < 2:
            return
        pa, pb = select_parents(ready)
        if pa is None:
            return
        child_genome = reproduce(pa, pb)
        parent = pa
        child_x = parent.x + random.uniform(-20, 20)
        child_y = parent.y + random.uniform(-20, 20)
        child   = Prey(child_x, child_y, genome=child_genome)
        pa.energy -= 30
        pb.energy -= 20
        self.prey.append(child)

    def _try_reproduce_predators(self):
        ready = [p for p in self.predators if p.can_reproduce()]
        if len(ready) < 2:
            return
        pa, pb = select_parents(ready)
        if pa is None:
            return
        child_genome = reproduce(pa, pb)
        parent  = pa
        child_x = parent.x + random.uniform(-25, 25)
        child_y = parent.y + random.uniform(-25, 25)
        child   = Predator(child_x, child_y, genome=child_genome)
        pa.energy -= 50
        pb.energy -= 40
        self.predators.append(child)

    # def _prevent_extinction(self):
    #     """Inject a rescue group if either population collapses completely."""
    #     if len(self.prey) == 0:
    #         for _ in range(8):
    #             self.prey.append(
    #                 Prey(
    #                     random.randint(Config.SIM_WIDTH  // 4, 3 * Config.SIM_WIDTH  // 4),
    #                     random.randint(Config.SIM_HEIGHT // 4, 3 * Config.SIM_HEIGHT // 4)
    #                 )
    #             )

    #     if len(self.predators) == 0:
    #         for _ in range(3):
    #             self.predators.append(
    #                 Predator(
    #                     random.choice([
    #                         random.randint(10, 50),
    #                         random.randint(Config.SIM_WIDTH - 50, Config.SIM_WIDTH - 10)
    #                     ]),
    #                     random.randint(10, Config.SIM_HEIGHT - 10)
    #                 )
    #             )

    # ── Rendering ─────────────────────────────────────────────────────────
    def draw(self):
        """Render the full frame: arena + HUD + graph panel."""
        self.screen.fill(Config.BG_COLOR)

        # ── Subtle grid ───────────────────────────────────────────────
        grid_spacing = 60
        for gx in range(0, Config.SIM_WIDTH, grid_spacing):
            pygame.draw.line(self.screen, Config.GRID_COLOR,
                             (gx, 0), (gx, Config.SIM_HEIGHT))
        for gy in range(0, Config.SIM_HEIGHT, grid_spacing):
            pygame.draw.line(self.screen, Config.GRID_COLOR,
                             (0, gy), (Config.SIM_WIDTH, gy))

        # ── Resources ─────────────────────────────────────────────────
        for item in self.water:
            item.draw(self.screen)
        for item in self.food:
            item.draw(self.screen)

        # ── Agents ────────────────────────────────────────────────────
        for prey in self.prey:
            prey.draw(self.screen)
        for pred in self.predators:
            pred.draw(self.screen)

        # ── HUD ───────────────────────────────────────────────────────
        self._draw_hud()

        # ── Graph panel ───────────────────────────────────────────────
        self.graph.draw(self.screen, Config.SIM_WIDTH, 0)

    def _draw_hud(self):
        lines = [
            f"Generation : {self.generation} / {Config.MAX_GENERATIONS}",
            f"Tick       : {self.tick} / {Config.TICKS_PER_GEN}",
            f"Prey       : {len(self.prey)}",
            f"Predators  : {len(self.predators)}",
            "",
            "[SPACE] Pause   [R] Reset   [ESC] Quit",
        ]
        if self.paused:
            pause_surf = self.font_big.render("PAUSED", True, (255, 200, 50))
            self.screen.blit(pause_surf, (Config.SIM_WIDTH // 2 - 50, 10))
        y = 8
        for line in lines:
            colour = (160, 170, 200) if line.startswith("[") else Config.UI_TEXT_COLOR
            surf = self.font_hud.render(line, True, colour)
            self.screen.blit(surf, (8, y))
            y += 16

    # ── Controls ──────────────────────────────────────────────────────────
    def toggle_pause(self):
        self.paused = not self.paused

    # ── End screen ────────────────────────────────────────────────────────
    def show_final_screen(self):
        print(f"\n{'='*50}")
        print(f"SIMULATION COMPLETE - FINAL STATISTICS")
        print(f"{'='*50}")
        print(f"Total Generations: {self.generation}")
        print(f"Final Population: {len(self.prey) + len(self.predators)}")
        print(f"  - Predators: {len(self.predators)}")
        print(f"  - Prey: {len(self.prey)}")
        print(f"{'='*50}\n")
        overlay = pygame.Surface(
            (Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((10, 10, 20, 210))
        self.screen.blit(overlay, (0, 0))
        lines = [
            "── Simulation Complete ──",
            f"Generations run : {self.generation}",
            f"Surviving prey  : {len(self.prey)}",
            f"Surviving preds : {len(self.predators)}",
            "",
            "Closing in 5 seconds…",
        ]
        y = Config.WINDOW_HEIGHT // 2 - len(lines) * 18
        for line in lines:
            surf = self.font_big.render(line, True, (220, 230, 255))
            rect = surf.get_rect(centerx=Config.WINDOW_WIDTH // 2, y=y)
            self.screen.blit(surf, rect)
            y += 36
        pygame.display.flip()