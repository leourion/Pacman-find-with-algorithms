"""
Pac-Man AI Game with Search Algorithms
Main game loop with pathfinding visualization

FIXES (từ lần trước):
  FIX #1-7: xem algorithms.py

TÍNH NĂNG MỚI:
  FEAT #1 - Step-by-step mode (phím SPACE): AI đi từng bước một, dừng lại
            để người xem thấy rõ thuật toán expand node như thế nào.
  FEAT #2 - Bảng so sánh A* vs UCS (phím TAB): tích lũy kết quả nhiều lần
            tìm đường, hiển thị bảng so sánh steps/visited/cost/time.
  FEAT #3 - Export CSV (phím E): xuất toàn bộ log kết quả ra results.csv
            để dùng làm bằng chứng thực nghiệm trong báo cáo.
"""
import pygame
import csv
import os
from datetime import datetime
from config import *
from board import Board
from entities import Player, Ghost
from algorithms import PathfindingAgent, get_tile_cost


class StatsTracker:
    """
    FEAT #2 & #3: Theo dõi và tích lũy kết quả tìm đường của từng thuật toán.
    Lưu từng lần search: algo, heuristic, steps, visited, cost, time_ms.
    """

    def __init__(self):
        self.records = []          # Toàn bộ log (dùng cho CSV)
        self.summary = {}          # {algo_key: {steps, visited, cost, time, count}}

    def record(self, algo_mode, heuristic, steps, visited, cost, time_ms):
        """Ghi lại một lần tìm đường"""
        algo_name = {
            MODE_BFS:   "BFS",
            MODE_DFS:   "DFS",
            MODE_UCS:   "UCS",
            MODE_ASTAR: f"A*({heuristic})",
            MODE_GBFS:  f"GBFS({heuristic})",
        }.get(algo_mode, "?")

        entry = {
            "algo":      algo_name,
            "heuristic": heuristic if algo_mode in (MODE_ASTAR, MODE_GBFS) else "-",
            "steps":     steps,
            "visited":   visited,
            "cost":      round(cost, 2) if isinstance(cost, float) else cost,
            "time_ms":   round(time_ms, 3),
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }
        self.records.append(entry)

        # Cập nhật summary (trung bình cộng)
        key = algo_name
        if key not in self.summary:
            self.summary[key] = {"steps": 0, "visited": 0, "cost": 0,
                                 "time_ms": 0, "count": 0}
        s = self.summary[key]
        s["count"]   += 1
        s["steps"]   += steps
        s["visited"] += visited
        s["cost"]    += (cost if cost != float('inf') else 0)
        s["time_ms"] += time_ms

    def get_avg(self, key, field):
        """Trả về trung bình của field cho algo key"""
        s = self.summary.get(key)
        if not s or s["count"] == 0:
            return 0
        return s[field] / s["count"]

    def export_csv(self, filepath="results.csv"):
        """FEAT #3: Xuất toàn bộ records ra CSV"""
        if not self.records:
            return False
        fieldnames = ["timestamp", "algo", "heuristic", "steps",
                      "visited", "cost", "time_ms"]
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.records)
        return True

    def reset(self):
        self.records.clear()
        self.summary.clear()


class PacManGame:
    """Main game class with search algorithm visualization"""

    def __init__(self):
        pygame.init()
        self.base_surface = pygame.Surface((WIDTH, HEIGHT))
        self.window_size = self._compute_window_size()
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Pac-Man AI - Search Algorithms")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        self.small_font = pygame.font.Font('freesansbold.ttf', 16)
        self.tiny_font = pygame.font.Font('freesansbold.ttf', 13)
        self.big_font = pygame.font.Font('freesansbold.ttf', 42)  # Cache — không tạo mỗi frame

        self.player_images = self._load_player_images()
        self.ghost_images  = self._load_ghost_images()

        self.board  = Board()
        self.player = None
        self.ghosts = []
        self.agent  = PathfindingAgent(MODE_MANUAL)

        # Game state
        self.score        = 0
        self.lives        = 3
        self.powerup      = False
        self.permanent_powerup = False
        self.power_counter = 0
        self.eaten_ghosts  = [False, False, False, False]
        self.startup_counter = 0
        self.moving       = False
        self.game_over    = False
        self.game_won     = False
        self.counter      = 0
        self.flicker      = False

        # AI / visualization
        self.ai_mode        = MODE_MANUAL
        self.show_path      = True
        self.show_visited   = True
        self.show_visited_lines = False
        self.show_accumulated = True
        self.show_info_panel = False
        self.goal_position  = None
        self.path_complete  = False

        # FEAT #1 — Step-by-step
        self.step_mode      = False   # True = dừng lại sau mỗi bước
        self.step_ready     = False   # True = sẵn sàng thực thi bước kế
        self.step_frame_wait = 0      # Đếm frame delay giữa các bước (auto-step)
        self.step_delay     = 3       # Số frame giữa 2 bước khi giữ Space (nhanh hơn)
        self._last_step_executed = False  # BUG FIX: track frame này có bước không

        # FEAT #2 — Bảng so sánh
        self.show_compare   = False   # True = hiện bảng so sánh
        self.stats          = StatsTracker()

        # FEAT #3 — CSV export feedback
        self.export_msg     = ""      # Thông báo sau khi export
        self.export_msg_timer = 0     # Frame còn hiện thông báo

        self._initialize_entities()

    # ------------------------------------------------------------------
    # Setup helpers
    # ------------------------------------------------------------------

    def _compute_window_size(self):
        display_info = pygame.display.Info()
        max_w = max(640, display_info.current_w - 40)
        max_h = max(480, display_info.current_h - 80)
        scale = min(max_w / WIDTH, max_h / HEIGHT, 1.0)
        return (int(WIDTH * scale), int(HEIGHT * scale))

    def _load_player_images(self):
        images = []
        try:
            for i in range(1, 5):
                img = pygame.image.load(f'assets/player_images/{i}.png')
                images.append(pygame.transform.scale(img, (45, 45)))
        except (pygame.error, FileNotFoundError, OSError):
            for _ in range(4):
                s = pygame.Surface((45, 45), pygame.SRCALPHA)
                pygame.draw.circle(s, YELLOW, (22, 22), 20)
                images.append(s)
        return images

    def _load_ghost_images(self):
        images = {}
        colors = ['red', 'pink', 'blue', 'orange']
        color_defaults = [RED, PINK, CYAN, ORANGE]
        try:
            for color in colors:
                img = pygame.image.load(f'assets/ghost_images/{color}.png')
                images[color] = pygame.transform.scale(img, (45, 45))
            images['powerup'] = pygame.transform.scale(
                pygame.image.load('assets/ghost_images/powerup.png'), (45, 45))
            images['dead'] = pygame.transform.scale(
                pygame.image.load('assets/ghost_images/dead.png'), (45, 45))
        except (pygame.error, FileNotFoundError, OSError):
            for i, color in enumerate(colors):
                s = pygame.Surface((45, 45), pygame.SRCALPHA)
                pygame.draw.circle(s, color_defaults[i], (22, 22), 20)
                images[color] = s
            for key, col in [('powerup', BLUE), ('dead', WHITE)]:
                s = pygame.Surface((45, 45), pygame.SRCALPHA)
                pygame.draw.circle(s, col, (22, 22), 20)
                images[key] = s
        return images

    def _initialize_entities(self):
        self.player = Player(PLAYER_START_X, PLAYER_START_Y, self.player_images)
        self.ghosts = [
            Ghost(BLINKY_START_X, BLINKY_START_Y, (PLAYER_START_X, PLAYER_START_Y),
                  GHOST_SPEED, self.ghost_images['red'],    DIR_RIGHT, 0, "Blinky"),
            Ghost(INKY_START_X,   INKY_START_Y,   (PLAYER_START_X, PLAYER_START_Y),
                  GHOST_SPEED, self.ghost_images['blue'],   DIR_UP,    1, "Inky"),
            Ghost(PINKY_START_X,  PINKY_START_Y,  (PLAYER_START_X, PLAYER_START_Y),
                  GHOST_SPEED, self.ghost_images['pink'],   DIR_UP,    2, "Pinky"),
            Ghost(CLYDE_START_X,  CLYDE_START_Y,  (PLAYER_START_X, PLAYER_START_Y),
                  GHOST_SPEED, self.ghost_images['orange'], DIR_UP,    3, "Clyde"),
        ]

    # ------------------------------------------------------------------
    # Goal management
    # ------------------------------------------------------------------

    def set_new_goal(self):
        dots = self.board.get_all_dots()
        if dots:
            player_grid = self.player.get_grid_position()
            dots.sort(key=lambda d: abs(d[0]-player_grid[0]) + abs(d[1]-player_grid[1]))
            goal_index = min(len(dots)-1, max(0, len(dots) - len(dots)//5))
            self.goal_position = dots[goal_index]
        else:
            self.goal_position = self.board.get_random_walkable_position()
        self.path_complete = False
        self.agent.current_path = []
        self.agent.path_index   = 0

    def plan_current_path(self):
        """Compute and show the current path without moving Pacman."""
        if self.ai_mode == MODE_MANUAL:
            return
        if self.goal_position is None:
            self.set_new_goal()
        if self.goal_position is None:
            return
        player_grid = self.player.get_grid_position()
        self.agent.current_path = self.agent._run_search(player_grid, self.goal_position, self.board)
        self.agent.path_index = 0

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def ghosts_are_eatable(self):
        return self.powerup or self.permanent_powerup

    def set_permanent_powerup(self, enabled):
        self.permanent_powerup = enabled
        if enabled:
            self.powerup = False
            self.power_counter = 0
            self.eaten_ghosts = [False, False, False, False]
            for ghost in self.ghosts:
                if not ghost.dead:
                    ghost.speed = GHOST_SPEED_SCARED
        elif not self.powerup:
            self.eaten_ghosts = [False, False, False, False]
            for ghost in self.ghosts:
                if not ghost.dead:
                    ghost.speed = GHOST_SPEED

    def toggle_permanent_powerup(self):
        self.set_permanent_powerup(not self.permanent_powerup)
        print(f"[Power] Permanent ghost-eat mode: {'ON' if self.permanent_powerup else 'OFF'}")

    def reset_game(self):
        self.board.reset()
        self.player.reset(PLAYER_START_X, PLAYER_START_Y)
        for ghost in self.ghosts:
            ghost.reset()
        self.score = 0
        self.lives = 3
        self.powerup = False
        self.permanent_powerup = False
        self.power_counter = 0
        self.eaten_ghosts = [False, False, False, False]
        self.startup_counter = 0
        self.moving = False
        self.game_over = False
        self.game_won  = False
        self.agent.current_path = []
        self.agent.visited_nodes = set()
        self.agent.accumulated_visited = set()
        self.goal_position = None
        self.path_complete = False
        # Reset step mode state
        self.step_mode = False          # FIX: reset step mode khi restart
        self.step_ready = False
        self.step_frame_wait = 0
        self._last_step_executed = False

    def reset_positions(self):
        self.player.reset(PLAYER_START_X, PLAYER_START_Y)
        for ghost in self.ghosts:
            ghost.reset()
        self.powerup = False
        self.power_counter = 0
        self.eaten_ghosts = [False, False, False, False]
        self.startup_counter = 0
        self.agent.current_path = []
        self.goal_position = None
        self.path_complete = False
        self.step_ready = False

    # ------------------------------------------------------------------
    # Collision checks
    # ------------------------------------------------------------------

    def check_collisions(self):
        center_x, center_y = self.player.get_center()
        grid_row = center_y // TILE_HEIGHT
        grid_col = center_x // TILE_WIDTH
        if 0 < self.player.x < 870:
            tile = self.board.get_tile(grid_row, grid_col)
            if tile == TILE_DOT:
                self.board.set_tile(grid_row, grid_col, TILE_EMPTY)
                self.score += SCORE_DOT
            elif tile == TILE_POWER_PELLET:
                self.board.set_tile(grid_row, grid_col, TILE_EMPTY)
                self.score += SCORE_POWER_PELLET
                self.power_counter = 0
                if not self.permanent_powerup:
                    self.powerup = True
                self.eaten_ghosts = [False, False, False, False]
                for ghost in self.ghosts:
                    if not ghost.dead:
                        ghost.speed = GHOST_SPEED_SCARED

    def check_ghost_collisions(self):
        player_center = self.player.get_center()
        player_rect = pygame.Rect(player_center[0]-18, player_center[1]-18, 36, 36)
        for ghost in self.ghosts:
            ghost_center = ghost.get_center()
            ghost_rect = pygame.Rect(ghost_center[0]-18, ghost_center[1]-18, 36, 36)
            if player_rect.colliderect(ghost_rect):
                if self.ghosts_are_eatable() and not ghost.dead and not self.eaten_ghosts[ghost.ghost_id]:
                    ghost.dead = True
                    self.eaten_ghosts[ghost.ghost_id] = True
                    n = self.eaten_ghosts.count(True)
                    self.score += (2 ** (n-1)) * SCORE_GHOST_BASE
                    ghost.speed = GHOST_SPEED_DEAD
                elif not self.ghosts_are_eatable() and not ghost.dead:
                    self.lives -= 1
                    if self.lives > 0:
                        self.reset_positions()
                    else:
                        self.game_over = True
                        self.moving = False
                elif self.ghosts_are_eatable() and self.eaten_ghosts[ghost.ghost_id] and not ghost.dead:
                    self.lives -= 1
                    if self.lives > 0:
                        self.reset_positions()
                    else:
                        self.game_over = True
                        self.moving = False

    # ------------------------------------------------------------------
    # Ghost AI
    # ------------------------------------------------------------------

    def update_ghost_targets(self):
        player_x, player_y = self.player.x, self.player.y
        runaway_x = 900 if player_x < 450 else 0
        runaway_y = 900 if player_y < 450 else 0
        return_target = (380, 400)
        for ghost in self.ghosts:
            if self.ghosts_are_eatable():
                if not ghost.dead and not self.eaten_ghosts[ghost.ghost_id]:
                    targets = [(runaway_x, runaway_y), (runaway_x, player_y),
                               (player_x, runaway_y), (450, 450)]
                    ghost.target = targets[ghost.ghost_id]
                elif not ghost.dead and self.eaten_ghosts[ghost.ghost_id]:
                    ghost.target = (400, 100) if (340 < ghost.x < 560 and 340 < ghost.y < 500) \
                                   else (player_x, player_y)
                else:
                    ghost.target = return_target
            else:
                if not ghost.dead:
                    ghost.target = (400, 100) if (340 < ghost.x < 560 and 340 < ghost.y < 500) \
                                   else (player_x, player_y)
                else:
                    ghost.target = return_target

    def update_ghosts(self):
        for ghost in self.ghosts:
            ghost.check_collisions(self.board)
            if ghost.in_box and ghost.dead:
                ghost.dead = False
                if self.permanent_powerup:
                    self.eaten_ghosts[ghost.ghost_id] = False
                ghost.speed = GHOST_SPEED_SCARED if self.ghosts_are_eatable() else GHOST_SPEED
            if self.moving:
                ghost.move_towards_target()

    # ------------------------------------------------------------------
    # FEAT #2 — Vẽ bảng so sánh A* vs UCS
    # ------------------------------------------------------------------

    def draw_comparison_table(self):
        """
        Vẽ bảng so sánh kết quả tìm đường trung bình của UCS và A*.
        Chỉ hiện khi show_compare = True (phím TAB).
        """
        # Các algo cần so sánh (ưu tiên UCS và A*)
        keys_order = ["UCS", "A*(manhattan)", "A*(euclidean)", "BFS", "DFS"]
        present = [k for k in keys_order if k in self.stats.summary]
        if not present:
            # Chưa có dữ liệu — vẽ thông báo nhỏ
            msg = self.small_font.render("No data yet - run AI then press TAB", True, YELLOW)
            self.base_surface.blit(msg, (200, 460))
            return

        # Kích thước bảng
        col_w   = [110, 70, 80, 70, 90, 40]  # algo, steps, visited, cost, time, count
        headers = ["Algorithm", "Steps", "Visited", "Cost", "Time(ms)", "N"]
        row_h   = 22
        pad     = 8
        table_w = sum(col_w) + pad * 2
        n_rows  = len(present) + 1  # header + data rows
        table_h = n_rows * row_h + pad * 2 + 4
        tx      = (WIDTH - table_w) // 2
        ty      = 430

        # Nền bảng
        pygame.draw.rect(self.base_surface, (20, 20, 50),
                         (tx-2, ty-2, table_w+4, table_h+4), border_radius=8)
        pygame.draw.rect(self.base_surface, (60, 60, 120),
                         (tx-2, ty-2, table_w+4, table_h+4), 2, border_radius=8)

        # Header row
        hx = tx + pad
        hy = ty + pad
        pygame.draw.rect(self.base_surface, (40, 40, 100),
                         (tx, ty, table_w, row_h))
        for i, (h, w) in enumerate(zip(headers, col_w)):
            surf = self.tiny_font.render(h, True, CYAN)
            self.base_surface.blit(surf, (hx, hy + 3))
            hx += w

        # Data rows
        for row_idx, key in enumerate(present):
            ry = ty + pad + row_h * (row_idx + 1)
            # Nền xen kẽ
            bg_color = (25, 25, 60) if row_idx % 2 == 0 else (30, 30, 70)
            pygame.draw.rect(self.base_surface, bg_color,
                             (tx, ry, table_w, row_h))

            s = self.stats.summary[key]
            n = s["count"]
            avg_steps   = s["steps"]   / n
            avg_visited = s["visited"] / n
            avg_cost    = s["cost"]    / n
            avg_time    = s["time_ms"] / n

            row_data = [
                key,
                f"{avg_steps:.1f}",
                f"{avg_visited:.1f}",
                f"{avg_cost:.1f}",
                f"{avg_time:.3f}",
                str(n),
            ]
            # Màu nổi bật cho A* (tốt nhất về visited)
            text_color = (255, 220, 80) if key.startswith("A*") else WHITE

            cx = tx + pad
            for val, w in zip(row_data, col_w):
                surf = self.tiny_font.render(val, True, text_color)
                self.base_surface.blit(surf, (cx, ry + 4))
                cx += w

        # Ghi chú phía dưới bảng
        note = self.tiny_font.render(
            "Average over multiple searches  |  E: export CSV", True, (150, 150, 200))
        self.base_surface.blit(note, (tx, ty + table_h + 2))

    # ------------------------------------------------------------------
    # Draw UI
    # ------------------------------------------------------------------

    def _draw_panel(self, rect, alpha=200, border_color=UI_ACCENT):
        """Vẽ panel nền tối bo góc"""
        s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        s.fill((*UI_BG, alpha))
        self.base_surface.blit(s, (rect[0], rect[1]))
        pygame.draw.rect(self.base_surface, border_color,
                         rect, 1, border_radius=6)

    def _draw_neon_text(self, text, font, color, glow_color, pos):
        """Vẽ text với viền glow nhẹ"""
        glow = font.render(text, True, glow_color)
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            self.base_surface.blit(glow, (pos[0]+dx, pos[1]+dy))
        surf = font.render(text, True, color)
        self.base_surface.blit(surf, pos)

    def _tile_cost_breakdown(self):
        counts = {TILE_DOT: 0, TILE_POWER_PELLET: 0, TILE_EMPTY: 0, "ghost": 0}
        total = 0
        for row, col in self.agent.current_path:
            tile = self.board.get_tile(row, col)
            if tile in counts:
                counts[tile] += 1
            if (GHOST_HOUSE_ROW_MIN <= row <= GHOST_HOUSE_ROW_MAX and
                    GHOST_HOUSE_COL_MIN <= col <= GHOST_HOUSE_COL_MAX):
                counts["ghost"] += 1
            total += get_tile_cost(row, col, self.board)
        return counts, total

    def draw_info_panel(self):
        if not self.show_info_panel or self.ai_mode == MODE_MANUAL:
            return

        formulas = {
            MODE_UCS: ("UCS", "f(n)=g(n)", "h(n)=0"),
            MODE_ASTAR: ("A*", "f(n)=g(n)+h(n)", f"h={self.agent.heuristic_mode} distance"),
            MODE_GBFS: ("GBFS", "f(n)=h(n)", f"h={self.agent.heuristic_mode} distance"),
            MODE_BFS: ("BFS", "f(n)=depth", "edge cost=1"),
            MODE_DFS: ("DFS", "stack search", "not cost optimal"),
        }
        name, formula, heuristic_note = formulas.get(self.ai_mode, ("AI", "-", "-"))
        player_grid = self.player.get_grid_position()
        counts, computed_cost = self._tile_cost_breakdown()
        path_steps = len(self.agent.current_path)
        visited_count = len(self.agent.visited_nodes)
        total_visited = len(self.agent.accumulated_visited)
        cost_value = self.agent.last_path_cost if self.agent.last_path_cost != 0 else computed_cost

        x, y, w, h = 500, 48, 390, 260
        self._draw_panel((x, y, w, h), alpha=225, border_color=(70, 160, 255))

        rows = [
            (f"{name} TRACE", UI_HIGHLIGHT),
            (f"Priority: {formula}    {heuristic_note}", PELLET_GLOW),
            (f"Start {player_grid}  ->  Goal {self.goal_position}", UI_TEXT),
            (f"Path: {path_steps} steps | cost {cost_value} | visited {visited_count}/{total_visited}", UI_GREEN),
            ("edge weight: DOT=1, POWER=1, EMPTY=2, ghost-house +5", UI_TEXT),
            (f"path cost: DOT {counts[TILE_DOT]} + POWER {counts[TILE_POWER_PELLET]} + EMPTY {counts[TILE_EMPTY]}x2 + GH {counts['ghost']}x5", UI_TEXT),
            ("pop order table:", UI_HIGHLIGHT),
            ("#   node       parent     edge   g      h      f", (120, 190, 255)),
        ]

        for idx, item in list(enumerate(self.agent.search_trace, start=1))[-8:]:
            g = "-" if item["g"] is None else f"{item['g']:.0f}"
            h_val = "-" if item["h"] is None else f"{item['h']:.1f}"
            f_val = "-" if item["f"] is None else f"{item['f']:.1f}"
            parent = item.get("parent")
            edge = "-"
            if parent is not None:
                edge = str(get_tile_cost(item["node"][0], item["node"][1], self.board))
            rows.append((f"{idx:<3} {str(item['node']):<10} {str(parent):<10} {edge:<6} {g:<6} {h_val:<6} {f_val:<6}", UI_TEXT))

        rows.extend([
            ("Press I to hide this panel.", (160, 160, 190)),
        ])

        cy = y + 12
        for text, color in rows:
            surf = self.tiny_font.render(text, True, color)
            self.base_surface.blit(surf, (x + 12, cy))
            cy += 17

    def draw_ui(self):
        # --- Bottom status bar ---
        bar_y = HEIGHT - 46
        self._draw_panel((0, bar_y, WIDTH, 46), alpha=220, border_color=UI_ACCENT)

        # Score
        self._draw_neon_text(f'SCORE', self.tiny_font, UI_ACCENT, (20,40,120), (14, bar_y + 4))
        self._draw_neon_text(f'{self.score:06d}', self.font, SCORE_COLOR, (100,80,0), (14, bar_y + 18))

        # Lives (Pacman icons)
        import math as _m
        for i in range(self.lives):
            lx = 180 + i * 38
            ly = bar_y + 14
            pygame.draw.circle(self.base_surface, PACMAN_COLOR, (lx, ly), 12)
            pts = [(lx, ly)]
            for s2 in range(20):
                a2 = _m.radians(30 + s2 * (300 / 19))
                pts.append((lx + 13 * _m.cos(a2), ly - 13 * _m.sin(a2)))
            pygame.draw.polygon(self.base_surface, BG_COLOR, pts)

        if self.ghosts_are_eatable():
            pygame.draw.circle(self.base_surface, PELLET_GLOW, (290, bar_y + 14), 10)
            pygame.draw.circle(self.base_surface, PELLET_COLOR, (290, bar_y + 14), 7)
            if self.permanent_powerup:
                perm_surf = self.tiny_font.render("PERMA", True, PELLET_GLOW)
                self.base_surface.blit(perm_surf, (305, bar_y + 8))

        # Algo mode badge
        algo_name = ALGORITHM_NAMES[self.ai_mode]
        badge_surf = self.small_font.render(algo_name, True, UI_TEXT)
        bw = badge_surf.get_width() + 14
        bx = WIDTH - bw - 8
        self._draw_panel((bx - 2, bar_y + 4, bw + 4, 20), alpha=180, border_color=UI_ACCENT)
        self.base_surface.blit(badge_surf, (bx + 5, bar_y + 6))

        # --- Top HUD panel ---
        cur_y = 28

        # Heuristic (chỉ A*)
        if self.ai_mode in (MODE_ASTAR, MODE_GBFS):
            h_name = "Manhattan" if self.agent.heuristic_mode == 'manhattan' else "Euclidean"
            h_text = self.small_font.render(f'Heuristic: {h_name}  [H: doi]', True, PELLET_GLOW)
            self.base_surface.blit(h_text, (10, cur_y))
            cur_y += 18

        # FEAT #1 — Step mode indicator
        if self.step_mode and self.ai_mode != MODE_MANUAL:
            step_color = UI_ORANGE
            step_label = "[||] STEP MODE  [SPACE: next step | S: off]"
            step_surf = self.small_font.render(step_label, True, step_color)
            self.base_surface.blit(step_surf, (10, cur_y))
            cur_y += 18

        # Phím tắt (rút gọn)
        inst = self.tiny_font.render(
            "1-6:Algo | G:Goal | V:Visited | L:VisitLine | P:Path | A:Accum | "
            "I:Info | F:GhostEat | S:Step | TAB:Compare | E:CSV | R:Reset",
            True, (120, 120, 160))
        self.base_surface.blit(inst, (10, cur_y))
        cur_y += 16

        # Thống kê lần tìm cuối
        if self.ai_mode != MODE_MANUAL:
            if len(self.agent.accumulated_visited) > 0:
                vis_surf = self.small_font.render(
                    f'Visited: {len(self.agent.visited_nodes)} (total: {len(self.agent.accumulated_visited)})',
                    True, UI_HIGHLIGHT)
                self.base_surface.blit(vis_surf, (10, cur_y))
                cur_y += 18

            if self.agent.current_path:
                path_surf = self.small_font.render(
                    f'Path: {len(self.agent.current_path)} steps', True, UI_HIGHLIGHT)
                self.base_surface.blit(path_surf, (10, cur_y))
                cur_y += 18

            if self.agent.last_search_time_ms > 0:
                time_surf = self.small_font.render(
                    f'Time: {self.agent.last_search_time_ms:.2f} ms', True, (180, 255, 180))
                self.base_surface.blit(time_surf, (10, cur_y))
                cur_y += 18

            if self.ai_mode in (MODE_UCS, MODE_ASTAR, MODE_GBFS) and self.agent.last_path_cost > 0:
                cost_surf = self.small_font.render(
                    f'Cost: {self.agent.last_path_cost}', True, (180, 255, 180))
                self.base_surface.blit(cost_surf, (10, cur_y))

        # FEAT #2 — Bảng so sánh
        if self.show_compare:
            self.draw_comparison_table()

        # FEAT #3 — Thông báo export
        if self.export_msg and self.export_msg_timer > 0:
            msg_surf = self.small_font.render(self.export_msg, True, UI_GREEN)
            msg_rect = msg_surf.get_rect(center=(WIDTH // 2, 890))
            pygame.draw.rect(self.base_surface, UI_BG,
                             msg_rect.inflate(16, 8), border_radius=6)
            self.base_surface.blit(msg_surf, msg_rect)
            self.export_msg_timer -= 1

        # Game over / won overlay
        if self.game_over or self.game_won:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.base_surface.blit(overlay, (0, 0))
            bx, by, bw, bh = 100, 360, 700, 160
            pygame.draw.rect(self.base_surface, UI_BG, (bx, by, bw, bh), border_radius=16)
            if self.game_over:
                pygame.draw.rect(self.base_surface, RED, (bx, by, bw, bh), 2, border_radius=16)
                self._draw_neon_text('GAME OVER', self.big_font, RED, (80,0,0), (bx+185, by+30))
                self.base_surface.blit(
                    self.small_font.render('Bam R de choi lai', True, UI_TEXT), (bx+250, by+100))
            else:
                pygame.draw.rect(self.base_surface, UI_GREEN, (bx, by, bw, bh), 2, border_radius=16)
                self._draw_neon_text('CHIEN THANG!', self.big_font, UI_GREEN, (0,60,20), (bx+165, by+30))
                self.base_surface.blit(
                    self.small_font.render('Bam R de choi lai', True, UI_TEXT), (bx+250, by+100))

    # ------------------------------------------------------------------
    # Draw AI visualization
    # ------------------------------------------------------------------

    def draw_ai_visualization(self):
        if self.ai_mode == MODE_MANUAL:
            return

        # Goal (đỏ)
        if self.goal_position:
            gx = int(self.goal_position[1] * TILE_WIDTH  + TILE_WIDTH  // 2)
            gy = int(self.goal_position[0] * TILE_HEIGHT + TILE_HEIGHT // 2)
            pygame.draw.circle(self.base_surface, RED,          (gx, gy), 12, 3)
            pygame.draw.circle(self.base_surface, (255,100,100),(gx, gy), 8)

        # Visited nodes
        visited_source = (self.agent.accumulated_visited
                          if self.show_accumulated else self.agent.visited_nodes)
        if self.show_visited_lines:
            for parent, node in self.agent.visited_edges:
                if parent not in visited_source or node not in visited_source:
                    continue
                x1 = int(parent[1] * TILE_WIDTH + TILE_WIDTH // 2)
                y1 = int(parent[0] * TILE_HEIGHT + TILE_HEIGHT // 2)
                x2 = int(node[1] * TILE_WIDTH + TILE_WIDTH // 2)
                y2 = int(node[0] * TILE_HEIGHT + TILE_HEIGHT // 2)
                if abs(x2 - x1) > TILE_WIDTH * 2:
                    continue
                pygame.draw.line(self.base_surface, (70, 160, 255), (x1, y1), (x2, y2), 2)

        if self.show_visited:
            if self.show_accumulated:
                for node in self.agent.accumulated_visited:
                    x = int(node[1] * TILE_WIDTH  + TILE_WIDTH  // 2)
                    y = int(node[0] * TILE_HEIGHT + TILE_HEIGHT // 2)
                    pygame.draw.circle(self.base_surface, (60, 80, 180), (x, y), 3)
            for node in self.agent.visited_nodes:
                x = int(node[1] * TILE_WIDTH  + TILE_WIDTH  // 2)
                y = int(node[0] * TILE_HEIGHT + TILE_HEIGHT // 2)
                pygame.draw.circle(self.base_surface, (100,150,255), (x, y), 4)

        # Path (xanh lá)
        if self.show_path and self.agent.current_path:
            pts = self.agent.current_path
            for i in range(len(pts) - 1):
                x1 = int(pts[i][1]   * TILE_WIDTH  + TILE_WIDTH  // 2)
                y1 = int(pts[i][0]   * TILE_HEIGHT + TILE_HEIGHT // 2)
                x2 = int(pts[i+1][1] * TILE_WIDTH  + TILE_WIDTH  // 2)
                y2 = int(pts[i+1][0] * TILE_HEIGHT + TILE_HEIGHT // 2)
                pygame.draw.line(self.base_surface, (0,255,0), (x1,y1), (x2,y2), 3)
            for pos in pts:
                x = int(pos[1] * TILE_WIDTH  + TILE_WIDTH  // 2)
                y = int(pos[0] * TILE_HEIGHT + TILE_HEIGHT // 2)
                pygame.draw.circle(self.base_surface, (0,200,0), (x, y), 5)

            # FEAT #1 — Tô đậm node kế tiếp sẽ đi (cam)
            if self.step_mode and self.agent.path_index < len(pts):
                next_node = pts[self.agent.path_index]
                nx = int(next_node[1] * TILE_WIDTH  + TILE_WIDTH  // 2)
                ny = int(next_node[0] * TILE_HEIGHT + TILE_HEIGHT // 2)
                pygame.draw.circle(self.base_surface, ORANGE, (nx, ny), 9)
                pygame.draw.circle(self.base_surface, (255,200,0), (nx, ny), 6)

        # Start (xanh lá viền)
        pg = self.player.get_grid_position()
        sx = int(pg[1] * TILE_WIDTH  + TILE_WIDTH  // 2)
        sy = int(pg[0] * TILE_HEIGHT + TILE_HEIGHT // 2)
        pygame.draw.circle(self.base_surface, (0,255,0), (sx, sy), 10, 3)

    # ------------------------------------------------------------------
    # Input handling
    # ------------------------------------------------------------------

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            # Điều khiển thủ công
            if self.ai_mode == MODE_MANUAL:
                key_dir = {
                    pygame.K_RIGHT: DIR_RIGHT, pygame.K_LEFT: DIR_LEFT,
                    pygame.K_UP:    DIR_UP,     pygame.K_DOWN: DIR_DOWN,
                }
                if event.key in key_dir:
                    self.player.direction_command = key_dir[event.key]

            # Chọn thuật toán
            algo_map = {
                pygame.K_1: (MODE_MANUAL,  False),
                pygame.K_2: (MODE_BFS,     True),
                pygame.K_3: (MODE_DFS,     True),
                pygame.K_4: (MODE_UCS,     True),
                pygame.K_5: (MODE_ASTAR,   True),
                pygame.K_6: (MODE_GBFS,    True),
            }
            if event.key in algo_map:
                mode, needs_goal = algo_map[event.key]
                previous_goal = self.goal_position
                self.ai_mode = mode
                self.agent.set_algorithm(mode)
                self.step_ready = False
                # FIX: tắt step_mode khi chuyển sang Manual hoặc Minimax
                if mode == MODE_MANUAL:
                    self.step_mode = False
                if not needs_goal:
                    self.goal_position = None
                elif previous_goal is not None:
                    self.goal_position = previous_goal
                    self.path_complete = False
                else:
                    self.set_new_goal()
                if mode in (MODE_UCS, MODE_ASTAR, MODE_GBFS):
                    self.show_path = True
                    self.plan_current_path()

            # Toggle heuristic A*
            elif event.key == pygame.K_h:
                if self.ai_mode in (MODE_ASTAR, MODE_GBFS):
                    self.agent.toggle_heuristic()
                    self.show_path = True
                    self.plan_current_path()

            # New goal
            elif event.key == pygame.K_g:
                if self.ai_mode != MODE_MANUAL:
                    self.set_new_goal()
                    self.show_path = True
                    self.plan_current_path()

            # Toggle visualizations
            elif event.key == pygame.K_v:
                self.show_visited = not self.show_visited
            elif event.key == pygame.K_l:
                self.show_visited_lines = not self.show_visited_lines
            elif event.key == pygame.K_p:
                self.show_path = not self.show_path
            elif event.key == pygame.K_a:
                if self.ai_mode != MODE_MANUAL:
                    self.show_accumulated = not self.show_accumulated
            elif event.key == pygame.K_i:
                self.show_info_panel = not self.show_info_panel
            elif event.key == pygame.K_f:
                self.toggle_permanent_powerup()

            # FEAT #1 — Step mode: phím S bật/tắt, SPACE bước tiếp
            elif event.key == pygame.K_s:
                if self.ai_mode != MODE_MANUAL:
                    self.step_mode = not self.step_mode
                    self.step_ready = False
                    if self.step_mode:
                        self.show_path = True
                        self.plan_current_path()
                    print(f"[Step] {'ON' if self.step_mode else 'OFF'}")

            elif event.key == pygame.K_SPACE:
                if self.step_mode and self.ai_mode != MODE_MANUAL:
                    self.step_ready = True

            # FEAT #2 — Toggle bảng so sánh
            elif event.key == pygame.K_TAB:
                self.show_compare = not self.show_compare

            # FEAT #3 — Export CSV
            elif event.key == pygame.K_e:
                self._export_csv()

            elif event.key == pygame.K_r:
                self.reset_game()

        elif event.type == pygame.KEYUP:
            if self.ai_mode == MODE_MANUAL:
                key_dir = {
                    pygame.K_RIGHT: DIR_RIGHT, pygame.K_LEFT: DIR_LEFT,
                    pygame.K_UP:    DIR_UP,     pygame.K_DOWN: DIR_DOWN,
                }
                if event.key in key_dir and self.player.direction_command == key_dir[event.key]:
                    self.player.direction_command = self.player.direction

    # ------------------------------------------------------------------
    # FEAT #3 — Export CSV helper
    # ------------------------------------------------------------------

    def _export_csv(self):
        if not self.stats.records:
            self.export_msg = "No data! Run AI first."
            self.export_msg_timer = 120
            return
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.csv")
        ok = self.stats.export_csv(filepath)
        if ok:
            n = len(self.stats.records)
            self.export_msg = f"Exported {n} records -> results.csv"
            print(f"[Export] {n} records → {filepath}")
        else:
            self.export_msg = "Export error!"
        self.export_msg_timer = 180

    # ------------------------------------------------------------------
    # FEAT #1 — Kiểm tra xem frame này có được phép bước không
    # ------------------------------------------------------------------

    def _can_step(self):
        """
        Trả về True nếu được phép thực thi 1 bước AI trong frame này.
        - Normal mode: luôn True
        - Step mode: True chỉ khi SPACE được bấm/giữ
        Cũng set self._last_step_executed để player.move() biết có freeze không.
        """
        if not self.step_mode:
            self._last_step_executed = True
            return True
        if self.step_ready:
            self.step_ready = False
            self._last_step_executed = True
            return True
        # Giữ SPACE → auto-step chậm
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.step_frame_wait += 1
            if self.step_frame_wait >= self.step_delay:
                self.step_frame_wait = 0
                self._last_step_executed = True
                return True
        else:
            self.step_frame_wait = 0
        self._last_step_executed = False
        return False

    # ------------------------------------------------------------------
    # Update loop
    # ------------------------------------------------------------------

    def update(self):
        # Animation counter
        if self.counter < 19:
            self.counter += 1
            self.flicker = self.counter <= 3
        else:
            self.counter = 0
            self.flicker = True
        self.player.animation_counter = self.counter

        # Powerup timer
        if self.powerup and not self.permanent_powerup:
            self.power_counter += 1
            if self.power_counter >= POWERUP_DURATION:
                self.power_counter = 0
                self.powerup = False
                self.eaten_ghosts = [False, False, False, False]
                for ghost in self.ghosts:
                    if not ghost.dead:
                        ghost.speed = GHOST_SPEED

        # Startup delay
        if self.game_over or self.game_won:
            self.moving = False  # BUG FIX: dừng hẳn khi game kết thúc
        elif self.startup_counter < STARTUP_DURATION:
            self.moving = False
            self.startup_counter += 1
        else:
            self.moving = True

        if self.board.is_complete():
            self.game_won = True
            self.moving = False

        # Ghost speeds
        for i, ghost in enumerate(self.ghosts):
            if ghost.dead:
                ghost.speed = GHOST_SPEED_DEAD
            elif self.ghosts_are_eatable():
                ghost.speed = GHOST_SPEED if self.eaten_ghosts[i] else GHOST_SPEED_SCARED
            else:
                ghost.speed = GHOST_SPEED

        if self.moving:
            if self.ai_mode != MODE_MANUAL:
                # Đặt goal nếu chưa có
                if self.goal_position is None:
                    self.set_new_goal()

                # Kiểm tra đến goal
                player_grid = self.player.get_grid_position()
                if self.goal_position and player_grid == self.goal_position:
                    self.path_complete = True
                    self.set_new_goal()

                # Fallback no-path
                if self.agent.no_path_count >= 3:
                    self.agent.no_path_count = 0
                    self.set_new_goal()

                # FEAT #1 — Chỉ lấy bước đi nếu được phép
                if self._can_step():
                    ghost_positions = [(g.x, g.y) for g in self.ghosts if not g.dead]
                    ai_direction = self.agent.get_next_move(
                        (self.player.x, self.player.y),
                        ghost_positions, self.board, self.goal_position)

                    if ai_direction is not None:
                        self.player.direction_command = ai_direction

                    # FEAT #2 — Ghi thống kê mỗi khi có search mới
                    if self.agent.last_search_time_ms > 0 and self.ai_mode in (
                            MODE_BFS, MODE_DFS, MODE_UCS, MODE_ASTAR, MODE_GBFS):
                        self.stats.record(
                            algo_mode  = self.ai_mode,
                            heuristic  = self.agent.heuristic_mode,
                            steps      = len(self.agent.current_path),
                            visited    = len(self.agent.visited_nodes),
                            cost       = self.agent.last_path_cost,
                            time_ms    = self.agent.last_search_time_ms,
                        )
                        # Reset để không ghi lại lần sau
                        self.agent.last_search_time_ms = 0.0

            # Di chuyển player
            # BUG FIX: khi step mode mà chưa được phép bước → dừng player hoàn toàn
            step_frozen = (self.step_mode
                           and self.ai_mode != MODE_MANUAL
                           and not self._last_step_executed)

            turns_allowed = self.player.check_position(self.board)
            if not step_frozen:
                dir_map = {DIR_RIGHT: DIR_RIGHT, DIR_LEFT: DIR_LEFT,
                           DIR_UP: DIR_UP, DIR_DOWN: DIR_DOWN}
                for d in dir_map:
                    if self.player.direction_command == d and turns_allowed[d]:
                        self.player.direction = d
                        break
                self.player.move(turns_allowed)

            self.update_ghost_targets()
            self.update_ghosts()
            if not step_frozen:
                self.check_collisions()
                self.check_ghost_collisions()

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self):
        self.base_surface.fill(BG_COLOR)
        self.board.draw(self.base_surface, self.flicker)
        self.draw_ai_visualization()
        self.draw_info_panel()
        self.player.draw(self.base_surface)
        ghost_eatable = self.ghosts_are_eatable()
        for i, ghost in enumerate(self.ghosts):
            ghost.draw(self.base_surface, ghost_eatable, self.eaten_ghosts[i],
                       self.ghost_images['powerup'], self.ghost_images['dead'])
        self.draw_ui()

        if self.window_size != (WIDTH, HEIGHT):
            frame = pygame.transform.smoothscale(self.base_surface, self.window_size)
            self.screen.blit(frame, (0, 0))
        else:
            self.screen.blit(self.base_surface, (0, 0))
        pygame.display.flip()

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.handle_input(event)
            self.update()
            self.draw()
        pygame.quit()


def main():
    game = PacManGame()
    game.run()


if __name__ == "__main__":
    main()
