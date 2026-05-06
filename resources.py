"""
resources.py — Food and Water resource items that spawn in the arena.

Both are simple objects with a position.  They are consumed by agents
and respawn at a new random location after a cooldown.
"""

import random                          # random.randint for spawn positions
import pygame                          # drawing
import math                            # math.pi for star-point calculation
from config import Config              # arena dimensions and colours


class Food:
    """
    A food item: a small star drawn in yellow.
    Prey gain FOOD_ENERGY by walking over it.
    """

    def __init__(self, x=None, y=None):
        # If no position given, spawn randomly within the arena
        self.x = x if x is not None else random.randint(10, Config.SIM_WIDTH  - 10)
        self.y = y if y is not None else random.randint(10, Config.SIM_HEIGHT - 10)
        self.consumed = False          # set to True by the prey that eats it

    def respawn(self):
        """Move this food item to a new random position and mark it available."""
        self.x        = random.randint(10, Config.SIM_WIDTH  - 10)
        self.y        = random.randint(10, Config.SIM_HEIGHT - 10)
        self.consumed = False

    def draw(self, surface):
        """Draw a small 5-pointed star."""
        if self.consumed:
            return                    # don't draw consumed items

        cx, cy = int(self.x), int(self.y)
        outer_r = 7                   # outer radius of the star
        inner_r = 3                   # inner (concave) radius of the star
        points  = []

        for i in range(10):           # 5 outer + 5 inner points = 10 total
            angle = math.pi / 5 * i - math.pi / 2   # start pointing upward
            r     = outer_r if i % 2 == 0 else inner_r
            px    = cx + r * math.cos(angle)
            py    = cy + r * math.sin(angle)
            points.append((px, py))

        pygame.draw.polygon(surface, Config.FOOD_COLOR, points)
        # Bright centre dot
        pygame.draw.circle(surface, (255, 240, 100), (cx, cy), 2)


class Water:
    """
    A water source: a small teardrop / diamond drawn in blue.
    Prey gain WATER_ENERGY by standing on it.  Water is not consumed
    (it replenishes naturally) — it just sits on the map permanently.
    """

    def __init__(self, x=None, y=None):
        self.x = x if x is not None else random.randint(10, Config.SIM_WIDTH  - 10)
        self.y = y if y is not None else random.randint(10, Config.SIM_HEIGHT - 10)

    def draw(self, surface):
        """Draw a small diamond/teardrop shape in blue."""
        cx, cy = int(self.x), int(self.y)
        size = 6
        # Diamond: top, right, bottom, left
        pts = [
            (cx,        cy - size),   # top point
            (cx + size, cy),          # right point
            (cx,        cy + size),   # bottom point
            (cx - size, cy),          # left point
        ]
        pygame.draw.polygon(surface, Config.WATER_COLOR, pts)
        pygame.draw.polygon(surface, (100, 200, 255), pts, 1)  # lighter outline
        # Small highlight
        pygame.draw.circle(surface, (180, 230, 255), (cx - 1, cy - 2), 2)


def spawn_food(count):
    """Create `count` Food items at random positions."""
    return [Food() for _ in range(count)]


def spawn_water(count):
    """Create `count` Water items at random positions."""
    return [Water() for _ in range(count)]