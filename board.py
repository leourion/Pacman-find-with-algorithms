"""
Board module - Contains board layout and rendering logic
Complete implementation with all board management functions
"""
import pygame
import math
import copy
from config import *

# Original board layout
# 0 = empty black rectangle, 1 = dot, 2 = big dot (power pellet), 3 = vertical line,
# 4 = horizontal line, 5 = top right, 6 = top left, 7 = bot left, 8 = bot right, 9 = gate
BOARDS = [
    [6, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5],
    [3, 6, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 6, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 3],
    [3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3],
    [3, 3, 1, 6, 4, 4, 5, 1, 6, 4, 4, 4, 5, 1, 3, 3, 1, 6, 4, 4, 4, 5, 1, 6, 4, 4, 5, 1, 3, 3],
    [3, 3, 2, 3, 0, 0, 3, 1, 3, 0, 0, 0, 3, 1, 3, 3, 1, 3, 0, 0, 0, 3, 1, 3, 0, 0, 3, 2, 3, 3],
    [3, 3, 1, 7, 4, 4, 8, 1, 7, 4, 4, 4, 8, 1, 7, 8, 1, 7, 4, 4, 4, 8, 1, 7, 4, 4, 8, 1, 3, 3],
    [3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3],
    [3, 3, 1, 6, 4, 4, 5, 1, 6, 5, 1, 6, 4, 4, 4, 4, 4, 4, 5, 1, 6, 5, 1, 6, 4, 4, 5, 1, 3, 3],
    [3, 3, 1, 7, 4, 4, 8, 1, 3, 3, 1, 7, 4, 4, 5, 6, 4, 4, 8, 1, 3, 3, 1, 7, 4, 4, 8, 1, 3, 3],
    [3, 3, 1, 1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 1, 1, 3, 3],
    [3, 7, 4, 4, 4, 4, 5, 1, 3, 7, 4, 4, 5, 0, 3, 3, 0, 6, 4, 4, 8, 3, 1, 6, 4, 4, 4, 4, 8, 3],
    [3, 0, 0, 0, 0, 0, 3, 1, 3, 6, 4, 4, 8, 0, 7, 8, 0, 7, 4, 4, 5, 3, 1, 3, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 3, 1, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 1, 3, 0, 0, 0, 0, 0, 3],
    [8, 0, 0, 0, 0, 0, 3, 1, 3, 3, 0, 6, 4, 4, 9, 9, 4, 4, 5, 0, 3, 3, 1, 3, 0, 0, 0, 0, 0, 7],
    [4, 4, 4, 4, 4, 4, 8, 1, 7, 8, 0, 3, 0, 0, 0, 0, 0, 0, 3, 0, 7, 8, 1, 7, 4, 4, 4, 4, 4, 4],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [4, 4, 4, 4, 4, 4, 5, 1, 6, 5, 0, 3, 0, 0, 0, 0, 0, 0, 3, 0, 6, 5, 1, 6, 4, 4, 4, 4, 4, 4],
    [5, 0, 0, 0, 0, 0, 3, 1, 3, 3, 0, 7, 4, 4, 4, 4, 4, 4, 8, 0, 3, 3, 1, 3, 0, 0, 0, 0, 0, 6],
    [3, 0, 0, 0, 0, 0, 3, 1, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 1, 3, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 3, 1, 3, 3, 0, 6, 4, 4, 4, 4, 4, 4, 5, 0, 3, 3, 1, 3, 0, 0, 0, 0, 0, 3],
    [3, 6, 4, 4, 4, 4, 8, 1, 7, 8, 0, 7, 4, 4, 5, 6, 4, 4, 8, 0, 7, 8, 1, 7, 4, 4, 4, 4, 5, 3],
    [3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3],
    [3, 3, 1, 6, 4, 4, 5, 1, 6, 4, 4, 4, 5, 1, 3, 3, 1, 6, 4, 4, 4, 5, 1, 6, 4, 4, 5, 1, 3, 3],
    [3, 3, 1, 7, 4, 5, 3, 1, 7, 4, 4, 4, 8, 1, 7, 8, 1, 7, 4, 4, 4, 8, 1, 3, 6, 4, 8, 1, 3, 3],
    [3, 3, 2, 1, 1, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 1, 1, 2, 3, 3],
    [3, 7, 4, 5, 1, 3, 3, 1, 6, 5, 1, 6, 4, 4, 4, 4, 4, 4, 5, 1, 6, 5, 1, 3, 3, 1, 6, 4, 8, 3],
    [3, 6, 4, 8, 1, 7, 8, 1, 3, 3, 1, 7, 4, 4, 5, 6, 4, 4, 8, 1, 3, 3, 1, 7, 8, 1, 7, 4, 5, 3],
    [3, 3, 1, 1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 1, 1, 3, 3],
    [3, 3, 1, 6, 4, 4, 4, 4, 8, 7, 4, 4, 5, 1, 3, 3, 1, 6, 4, 4, 8, 7, 4, 4, 4, 4, 5, 1, 3, 3],
    [3, 3, 1, 7, 4, 4, 4, 4, 4, 4, 4, 4, 8, 1, 7, 8, 1, 7, 4, 4, 4, 4, 4, 4, 4, 4, 8, 1, 3, 3],
    [3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3],
    [3, 7, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 8, 3],
    [7, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 8]
]


class Board:
    """Manages the game board and rendering"""
    
    _glow_cache = {}  # Cache glow surfaces dùng chung

    def __init__(self):
        self.level = None
        self.original_board = copy.deepcopy(BOARDS)
        self.reset()
        
    def reset(self):
        """Reset board to initial state"""
        self.level = copy.deepcopy(self.original_board)
        
    # ------------------------------------------------------------------
    # Helpers vẽ hiệu ứng glow
    # ------------------------------------------------------------------

    @staticmethod
    def _make_glow(radius, color, alpha=80):
        """Tạo surface hình tròn mờ để làm hiệu ứng glow"""
        key = (radius, color, alpha)
        if key in Board._glow_cache:
            return Board._glow_cache[key]
        size = radius * 2 + 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        for r in range(radius, 0, -1):
            a = int(alpha * (r / radius) ** 0.5)
            pygame.draw.circle(surf, (*color, a), (radius + 1, radius + 1), r)
        Board._glow_cache[key] = surf
        return surf

    def _is_wall(self, row, col):
        """Kiểm tra ô (row,col) là tường hay không"""
        if row < 0 or row >= len(self.level) or col < 0 or col >= len(self.level[0]):
            return True
        return self.level[row][col] >= 3 and self.level[row][col] != TILE_GATE

    def draw(self, screen, flicker, color=MAZE_COLOR):
        """
        Vẽ maze đúng như hình mẫu Pac-Man:
        Kỹ thuật: nền XANH + đục hành lang đen bằng CAPSULE SHAPE
        (rect body + circle 2 đầu) cho mỗi H-run và V-run.
        Junction = rect vuông đen nối các capsule lại.
        Không có artifact, không có bánh răng.
        """
        rows = len(self.level)
        cols = len(self.level[0]) if rows else 0
        TW, TH = TILE_WIDTH, TILE_HEIGHT
        WW = 2   # wall thickness mỗi bên (px)

        WW = 0  # thinnest visual walls, widest corridors
        CH = TH - WW * 2  # corridor height
        CW = TW - WW * 2  # corridor width
        RH = CH // 2      # radius của H-capsule
        RV = CW // 2      # radius của V-capsule

        def is_path(r, c):
            if r < 0 or r >= rows or c < 0 or c >= cols:
                return False
            t = self.level[r][c]
            return t < 3 or t == TILE_GATE

        # --- 1. Nền xanh ---
        pygame.draw.rect(screen, MAZE_COLOR, (0, 0, cols * TW, rows * TH))

        # --- 2. H-capsules: mỗi horizontal run ---
        for i in range(rows):
            j = 0
            while j < cols:
                if is_path(i, j):
                    k = j
                    while k < cols and is_path(i, k):
                        k += 1
                    # Run: tiles j..k-1 ở row i
                    # Capsule centerline y = i*TH + TH//2
                    # Capsule: từ tâm tile j đến tâm tile k-1, radius = RH
                    cx0 = j * TW + TW // 2
                    cx1 = (k-1) * TW + TW // 2
                    cy  = i * TH + TH // 2

                    # Body rect
                    pygame.draw.rect(screen, BG_COLOR,
                                     (cx0, cy - RH, cx1 - cx0, CH))
                    # Cap trái
                    pygame.draw.circle(screen, BG_COLOR, (cx0, cy), RH)
                    # Cap phải
                    pygame.draw.circle(screen, BG_COLOR, (cx1, cy), RH)
                    j = k
                else:
                    j += 1

        # --- 3. V-capsules: mỗi vertical run ---
        for j in range(cols):
            i = 0
            while i < rows:
                if is_path(i, j):
                    k = i
                    while k < rows and is_path(k, j):
                        k += 1
                    # Run: tiles i..k-1 ở col j
                    cx  = j * TW + TW // 2
                    cy0 = i * TH + TH // 2
                    cy1 = (k-1) * TH + TH // 2

                    # Body rect
                    pygame.draw.rect(screen, BG_COLOR,
                                     (cx - RV, cy0, CW, cy1 - cy0))
                    # Cap trên
                    pygame.draw.circle(screen, BG_COLOR, (cx, cy0), RV)
                    # Cap dưới
                    pygame.draw.circle(screen, BG_COLOR, (cx, cy1), RV)
                    i = k
                else:
                    i += 1

        # --- 4. Junction fill + bo góc nhẹ ---
        for i in range(rows):
            for j in range(cols):
                if not is_path(i, j):
                    continue
                cx = j * TW + TW // 2
                cy = i * TH + TH // 2
                has_h = is_path(i, j-1) or is_path(i, j+1)
                has_v = is_path(i-1, j) or is_path(i+1, j)

                # Junction fill: nối H+V capsule
                if has_h and has_v:
                    pygame.draw.rect(screen, BG_COLOR,
                                     (cx - RV, cy - RH, CW, CH))



        # --- 5. Dots, power pellets, gate ---
        for i in range(rows):
            for j in range(cols):
                tile = self.level[i][j]
                cx = j * TW + TW // 2
                cy = i * TH + TH // 2

                if tile == TILE_DOT:
                    pygame.draw.circle(screen, DOT_COLOR, (cx, cy), 4)

                elif tile == TILE_POWER_PELLET and not flicker:
                    pygame.draw.circle(screen, PELLET_COLOR, (cx, cy), 8)

                elif tile == TILE_GATE:
                    gy = i * TH + TH // 2
                    pygame.draw.rect(screen, GATE_COLOR,
                                     (j * TW + 4, gy - 2, TW - 8, 4),
                                     border_radius=2)


    def is_walkable(self, row, col):
        """Check if a position is walkable (not a wall)"""
        if row < 0 or row >= len(self.level) or col < 0 or col >= len(self.level[0]):
            return False
        tile = self.level[row][col]
        # Walkable if: empty, dot, power pellet, or gate
        return tile < 3 or tile == TILE_GATE
    
    def get_tile(self, row, col):
        """Get tile type at position"""
        if row < 0 or row >= len(self.level) or col < 0 or col >= len(self.level[0]):
            return -1
        return self.level[row][col]
    
    def set_tile(self, row, col, value):
        """Set tile type at position"""
        if 0 <= row < len(self.level) and 0 <= col < len(self.level[0]):
            self.level[row][col] = value
    
    def is_complete(self):
        """Check if all dots and power pellets are collected"""
        for row in self.level:
            if TILE_DOT in row or TILE_POWER_PELLET in row:
                return False
        return True
    
    def get_all_dots(self):
        """Get positions of all dots and power pellets"""
        dots = []
        for i in range(len(self.level)):
            for j in range(len(self.level[i])):
                if self.level[i][j] in [TILE_DOT, TILE_POWER_PELLET]:
                    dots.append((i, j))
        return dots
    
    def get_random_walkable_position(self):
        """Get a random walkable position for goal setting (outside ghost house)"""
        import random
        walkable_positions = []
        for i in range(len(self.level)):
            for j in range(len(self.level[i])):
                tile = self.level[i][j]
                # Dùng cùng điều kiện với is_walkable_pacman: chỉ EMPTY/DOT/POWER_PELLET
                if tile in (TILE_EMPTY, TILE_DOT, TILE_POWER_PELLET):
                    # Loại trừ vùng ghost house (pixel boundary giống in_box check)
                    px, py = j * TILE_WIDTH, i * TILE_HEIGHT
                    if not (350 < px < 550 and 370 < py < 480):
                        walkable_positions.append((i, j))
        if walkable_positions:
            return random.choice(walkable_positions)
        return (15, 15)  # Default fallback
