"""
graph.py — Population graph renderer.

Draws a live line chart showing prey and predator population counts
over time (tick-by-tick) and generation markers on the x-axis.
Rendered into the right-hand panel of the window.
"""

import pygame                          # drawing primitives
from config import Config              # colours and dimensions


class PopulationGraph:
    """
    Maintains a rolling history of prey and predator counts and
    draws a line chart onto a pygame Surface / sub-surface.
    """

    def __init__(self):
        self.prey_history     = []     # list of prey  counts (one entry per tick)
        self.pred_history     = []     # list of predator counts
        self.gen_markers      = []     # tick indices where a new generation started
        self.max_history      = 1200   # keep at most this many data points
        self.font_small  = None        # loaded lazily after pygame.init()
        self.font_medium = None

    def _init_fonts(self):
        """Initialise fonts the first time draw() is called."""
        if self.font_small is None:
            self.font_small  = pygame.font.SysFont("monospace", 11)
            self.font_medium = pygame.font.SysFont("monospace", 13, bold=True)

    def record(self, prey_count, pred_count, new_generation=False):
        """
        Append current population counts.
        Call once per simulation tick.
        `new_generation=True` adds a vertical marker line on the chart.
        """
        self.prey_history.append(prey_count)
        self.pred_history.append(pred_count)

        if new_generation:
            self.gen_markers.append(len(self.prey_history) - 1)

        # Trim old data so the list doesn't grow forever
        if len(self.prey_history) > self.max_history:
            trim = len(self.prey_history) - self.max_history
            self.prey_history = self.prey_history[trim:]
            self.pred_history = self.pred_history[trim:]
            # Adjust generation marker indices after trimming
            self.gen_markers = [
                m - trim for m in self.gen_markers if m - trim >= 0
            ]

    def draw(self, surface, offset_x, offset_y):
        """
        Draw the complete graph panel.

        surface  — the main pygame display surface
        offset_x — x pixel where the graph panel starts
        offset_y — y pixel where the graph panel starts (usually 0)
        """
        self._init_fonts()

        panel_w = Config.GRAPH_WIDTH
        panel_h = Config.WINDOW_HEIGHT

        # ── Panel background ──────────────────────────────────────────
        panel_rect = pygame.Rect(offset_x, offset_y, panel_w, panel_h)
        pygame.draw.rect(surface, Config.GRAPH_BG, panel_rect)
        # Left border line
        pygame.draw.line(
            surface, Config.PANEL_BORDER,
            (offset_x, offset_y), (offset_x, offset_y + panel_h), 2
        )

        # ── Title ─────────────────────────────────────────────────────
        title = self.font_medium.render("Population over Time", True, Config.UI_TEXT_COLOR)
        surface.blit(title, (offset_x + 10, offset_y + 10))

        # ── Legend ───────────────────────────────────────────────────
        prey_label = self.font_small.render("● Prey", True, Config.GRAPH_PREY_LINE)
        pred_label = self.font_small.render("▲ Predators", True, Config.GRAPH_PRED_LINE)
        surface.blit(prey_label, (offset_x + 10, offset_y + 32))
        surface.blit(pred_label, (offset_x + 90, offset_y + 32))

        # ── Chart area ────────────────────────────────────────────────
        margin_left   = 45        # space for y-axis labels
        margin_bottom = 40        # space for x-axis labels
        margin_top    = 55        # space for title/legend
        margin_right  = 10

        chart_x = offset_x + margin_left
        chart_y = offset_y + margin_top
        chart_w = panel_w  - margin_left - margin_right
        chart_h = panel_h  - margin_top  - margin_bottom

        # Chart background
        pygame.draw.rect(surface, (18, 22, 35), (chart_x, chart_y, chart_w, chart_h))
        pygame.draw.rect(surface, Config.GRAPH_AXIS, (chart_x, chart_y, chart_w, chart_h), 1)

        if len(self.prey_history) < 2:
            # Not enough data yet — show waiting message
            msg = self.font_small.render("Collecting data...", True, Config.GRAPH_AXIS)
            surface.blit(msg, (chart_x + 10, chart_y + chart_h // 2))
            return

        # ── Y-axis: determine scale from max population seen ──────────
        max_pop = max(
            max(self.prey_history, default=1),
            max(self.pred_history, default=1),
            1                               # prevent division by zero
        )
        max_pop = max_pop * 1.15            # add 15% head-room above the peak

        def to_px(value):
            """Convert a population count to a y pixel coordinate (flipped)."""
            ratio = value / max_pop
            return int(chart_y + chart_h - ratio * chart_h)

        def to_x_px(index):
            """Convert a history index to an x pixel coordinate."""
            n = len(self.prey_history)
            return int(chart_x + (index / (n - 1)) * chart_w)

        # ── Draw horizontal grid lines ────────────────────────────────
        for tick_val in [0.25, 0.5, 0.75, 1.0]:
            gy = to_px(max_pop * tick_val)
            pygame.draw.line(
                surface, (*Config.GRAPH_AXIS, 60),  # dim grid line
                (chart_x, gy), (chart_x + chart_w, gy), 1
            )
            # Y-axis label
            label = self.font_small.render(
                str(int(max_pop * tick_val)), True, Config.GRAPH_AXIS
            )
            surface.blit(label, (offset_x + 2, gy - 6))

        # ── Draw generation marker lines ──────────────────────────────
        for gm in self.gen_markers:
            if 0 <= gm < len(self.prey_history):
                gx = to_x_px(gm)
                pygame.draw.line(
                    surface, (80, 100, 150),
                    (gx, chart_y), (gx, chart_y + chart_h), 1
                )

        # ── Draw prey population line ─────────────────────────────────
        prey_pts = [
            (to_x_px(i), to_px(v))
            for i, v in enumerate(self.prey_history)
        ]
        if len(prey_pts) >= 2:
            pygame.draw.lines(surface, Config.GRAPH_PREY_LINE, False, prey_pts, 2)

        # ── Draw predator population line ─────────────────────────────
        pred_pts = [
            (to_x_px(i), to_px(v))
            for i, v in enumerate(self.pred_history)
        ]
        if len(pred_pts) >= 2:
            pygame.draw.lines(surface, Config.GRAPH_PRED_LINE, False, pred_pts, 2)

        # ── Draw dots at the latest data points ───────────────────────
        if prey_pts:
            pygame.draw.circle(surface, Config.GRAPH_PREY_LINE, prey_pts[-1], 4)
        if pred_pts:
            pygame.draw.circle(surface, Config.GRAPH_PRED_LINE, pred_pts[-1], 4)

        # ── X-axis label ──────────────────────────────────────────────
        x_label = self.font_small.render(
            f"Ticks (last {len(self.prey_history)})", True, Config.GRAPH_AXIS
        )
        surface.blit(x_label, (chart_x + chart_w // 2 - 50, chart_y + chart_h + 8))

        # ── Current count readout ─────────────────────────────────────
        cur_prey = self.prey_history[-1] if self.prey_history else 0
        cur_pred = self.pred_history[-1] if self.pred_history else 0
        readout_y = offset_y + panel_h - 30

        prey_txt = self.font_medium.render(f"Prey: {cur_prey}", True, Config.GRAPH_PREY_LINE)
        pred_txt = self.font_medium.render(f"Pred: {cur_pred}", True, Config.GRAPH_PRED_LINE)
        surface.blit(prey_txt, (offset_x + 10,  readout_y))
        surface.blit(pred_txt, (offset_x + 130, readout_y))