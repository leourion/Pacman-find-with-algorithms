"""
Entity classes for Player and Ghosts
"""
import pygame
import math as _math
from config import *

# Cache glow surfaces để tránh tạo mới mỗi frame
_glow_cache = {}

def _make_glow(radius, color_rgb, alpha=40):
    key = (radius, color_rgb, alpha)
    if key in _glow_cache:
        return _glow_cache[key]
    size = radius * 2 + 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    for r in range(radius, 0, -2):
        a = int(alpha * (r / radius) ** 0.5)
        pygame.draw.circle(surf, (*color_rgb, a), (radius+1, radius+1), r)
    _glow_cache[key] = surf
    return surf


class Player:
    """Player (Pac-Man) class"""
    
    def __init__(self, x, y, images):
        self.x = x
        self.y = y
        self.images = images
        self.direction = DIR_RIGHT
        self.direction_command = DIR_RIGHT
        self.speed = PLAYER_SPEED
        self.animation_counter = 0
        
    def reset(self, x=None, y=None):
        """Reset player to starting position"""
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        self.direction = DIR_RIGHT
        self.direction_command = DIR_RIGHT
        
    def get_center(self):
        """Get center position of player"""
        return (self.x + 23, self.y + 24)
    
    def get_grid_position(self):
        """Get grid position of player"""
        center_x, center_y = self.get_center()
        return (center_y // TILE_HEIGHT, center_x // TILE_WIDTH)
    
    def check_position(self, board):
        """Check which directions player can turn"""
        center_x, center_y = self.get_center()
        turns = [False, False, False, False]  # R, L, U, D
        num3 = 15
        
        if center_x // 30 < 29:
            # Check each direction
            if self.direction == DIR_RIGHT:
                if board.get_tile(center_y // TILE_HEIGHT, 
                                 (center_x - num3) // TILE_WIDTH) < 3:
                    turns[DIR_LEFT] = True
            if self.direction == DIR_LEFT:
                if board.get_tile(center_y // TILE_HEIGHT, 
                                 (center_x + num3) // TILE_WIDTH) < 3:
                    turns[DIR_RIGHT] = True
            if self.direction == DIR_UP:
                if board.get_tile((center_y + num3) // TILE_HEIGHT, 
                                 center_x // TILE_WIDTH) < 3:
                    turns[DIR_DOWN] = True
            if self.direction == DIR_DOWN:
                if board.get_tile((center_y - num3) // TILE_HEIGHT, 
                                 center_x // TILE_WIDTH) < 3:
                    turns[DIR_UP] = True
            
            # Additional turning checks based on alignment
            if self.direction in [DIR_UP, DIR_DOWN]:
                if 12 <= center_x % TILE_WIDTH <= 18:
                    if board.get_tile((center_y + num3) // TILE_HEIGHT, 
                                     center_x // TILE_WIDTH) < 3:
                        turns[DIR_DOWN] = True
                    if board.get_tile((center_y - num3) // TILE_HEIGHT, 
                                     center_x // TILE_WIDTH) < 3:
                        turns[DIR_UP] = True
                if 12 <= center_y % TILE_HEIGHT <= 18:
                    if board.get_tile(center_y // TILE_HEIGHT, 
                                     (center_x - TILE_WIDTH) // TILE_WIDTH) < 3:
                        turns[DIR_LEFT] = True
                    if board.get_tile(center_y // TILE_HEIGHT, 
                                     (center_x + TILE_WIDTH) // TILE_WIDTH) < 3:
                        turns[DIR_RIGHT] = True
            
            if self.direction in [DIR_RIGHT, DIR_LEFT]:
                if 12 <= center_x % TILE_WIDTH <= 18:
                    if board.get_tile((center_y + TILE_HEIGHT) // TILE_HEIGHT, 
                                     center_x // TILE_WIDTH) < 3:
                        turns[DIR_DOWN] = True
                    if board.get_tile((center_y - TILE_HEIGHT) // TILE_HEIGHT, 
                                     center_x // TILE_WIDTH) < 3:
                        turns[DIR_UP] = True
                if 12 <= center_y % TILE_HEIGHT <= 18:
                    if board.get_tile(center_y // TILE_HEIGHT, 
                                     (center_x - num3) // TILE_WIDTH) < 3:
                        turns[DIR_LEFT] = True
                    if board.get_tile(center_y // TILE_HEIGHT, 
                                     (center_x + num3) // TILE_WIDTH) < 3:
                        turns[DIR_RIGHT] = True
        else:
            turns[DIR_RIGHT] = True
            turns[DIR_LEFT] = True
        
        return turns
    
    def move(self, turns_allowed):
        """Move player based on direction and allowed turns"""
        if self.direction == DIR_RIGHT and turns_allowed[DIR_RIGHT]:
            self.x += self.speed
        elif self.direction == DIR_LEFT and turns_allowed[DIR_LEFT]:
            self.x -= self.speed
        if self.direction == DIR_UP and turns_allowed[DIR_UP]:
            self.y -= self.speed
        elif self.direction == DIR_DOWN and turns_allowed[DIR_DOWN]:
            self.y += self.speed
        
        # Handle wrap-around
        if self.x > 900:
            self.x = -47
        elif self.x < -50:
            self.x = 897
    
    def draw(self, screen):
        """Draw Pacman với hiệu ứng neon glow"""
        anim = (self.animation_counter // 3) % 8
        mouth_angle = [5, 15, 25, 35, 25, 15, 5, 0][anim]
        cx = self.x + 23
        cy = self.y + 23
        r  = 20
        rot = {DIR_RIGHT: 0, DIR_LEFT: 180, DIR_UP: 90, DIR_DOWN: 270}
        angle = rot.get(self.direction, 0)

        # Glow — dùng cache
        glow_surf = _make_glow(r + 12, PACMAN_COLOR[:3], alpha=40)
        screen.blit(glow_surf, (cx - r - 13, cy - r - 13))

        # Pacman polygon
        half = mouth_angle
        start_rad = _math.radians(half + angle)
        end_rad   = _math.radians(360 - half + angle)
        points = [(cx, cy)]
        for s in range(37):
            t = start_rad + (end_rad - start_rad) * s / 36
            points.append((cx + r * _math.cos(t), cy - r * _math.sin(t)))
        if len(points) > 2:
            pygame.draw.polygon(screen, PACMAN_COLOR, points)
            pygame.draw.polygon(screen, (255, 255, 180), points, 1)

        # Eye
        eye_angle = _math.radians(70 + angle)
        ex = int(cx + (r * 0.55) * _math.cos(eye_angle))
        ey = int(cy - (r * 0.55) * _math.sin(eye_angle))
        pygame.draw.circle(screen, (10, 10, 10), (ex, ey), 3)


class Ghost:
    """Ghost enemy class"""
    
    def __init__(self, x, y, target, speed, img, direction, ghost_id, name):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.target = target
        self.speed = speed
        self.img = img
        self.direction = direction
        self.ghost_id = ghost_id
        self.name = name
        self.dead = False
        self.in_box = False
        self.turns = [False, False, False, False]
        
    def reset(self):
        """Reset ghost to starting position"""
        self.x = self.start_x
        self.y = self.start_y
        self.dead = False
        self.in_box = False
        
    def get_center(self):
        """Get center position"""
        return (self.x + 22, self.y + 22)
    
    def get_grid_position(self):
        """Get grid position"""
        center_x, center_y = self.get_center()
        return (center_y // TILE_HEIGHT, center_x // TILE_WIDTH)
    
    def check_collisions(self, board):
        """Check available turns for ghost"""
        center_x, center_y = self.get_center()
        num3 = 15
        self.turns = [False, False, False, False]
        
        if 0 < center_x // 30 < 29:
            # Check gate passage
            if board.get_tile((center_y - num3) // TILE_HEIGHT, 
                            center_x // TILE_WIDTH) == TILE_GATE:
                self.turns[DIR_UP] = True
            
            # Check basic movements
            if (board.get_tile(center_y // TILE_HEIGHT, 
                             (center_x - num3) // TILE_WIDTH) < 3 or
                (board.get_tile(center_y // TILE_HEIGHT, 
                              (center_x - num3) // TILE_WIDTH) == TILE_GATE and 
                 (self.in_box or self.dead))):
                self.turns[DIR_LEFT] = True
                
            if (board.get_tile(center_y // TILE_HEIGHT, 
                             (center_x + num3) // TILE_WIDTH) < 3 or
                (board.get_tile(center_y // TILE_HEIGHT, 
                              (center_x + num3) // TILE_WIDTH) == TILE_GATE and 
                 (self.in_box or self.dead))):
                self.turns[DIR_RIGHT] = True
                
            if (board.get_tile((center_y + num3) // TILE_HEIGHT, 
                             center_x // TILE_WIDTH) < 3 or
                (board.get_tile((center_y + num3) // TILE_HEIGHT, 
                              center_x // TILE_WIDTH) == TILE_GATE and 
                 (self.in_box or self.dead))):
                self.turns[DIR_DOWN] = True
                
            if (board.get_tile((center_y - num3) // TILE_HEIGHT, 
                             center_x // TILE_WIDTH) < 3 or
                (board.get_tile((center_y - num3) // TILE_HEIGHT, 
                              center_x // TILE_WIDTH) == TILE_GATE and 
                 (self.in_box or self.dead))):
                self.turns[DIR_UP] = True
            
            # Additional alignment checks
            if self.direction in [DIR_UP, DIR_DOWN]:
                if 12 <= center_x % TILE_WIDTH <= 18:
                    if (board.get_tile((center_y + num3) // TILE_HEIGHT, 
                                     center_x // TILE_WIDTH) < 3 or
                        (board.get_tile((center_y + num3) // TILE_HEIGHT, 
                                      center_x // TILE_WIDTH) == TILE_GATE and 
                         (self.in_box or self.dead))):
                        self.turns[DIR_DOWN] = True
                    if (board.get_tile((center_y - num3) // TILE_HEIGHT, 
                                     center_x // TILE_WIDTH) < 3 or
                        (board.get_tile((center_y - num3) // TILE_HEIGHT, 
                                      center_x // TILE_WIDTH) == TILE_GATE and 
                         (self.in_box or self.dead))):
                        self.turns[DIR_UP] = True
                        
            if self.direction in [DIR_RIGHT, DIR_LEFT]:
                if 12 <= center_x % TILE_WIDTH <= 18:
                    if (board.get_tile((center_y + num3) // TILE_HEIGHT, 
                                     center_x // TILE_WIDTH) < 3 or
                        (board.get_tile((center_y + num3) // TILE_HEIGHT, 
                                      center_x // TILE_WIDTH) == TILE_GATE and 
                         (self.in_box or self.dead))):
                        self.turns[DIR_DOWN] = True
                    if (board.get_tile((center_y - num3) // TILE_HEIGHT, 
                                     center_x // TILE_WIDTH) < 3 or
                        (board.get_tile((center_y - num3) // TILE_HEIGHT, 
                                      center_x // TILE_WIDTH) == TILE_GATE and 
                         (self.in_box or self.dead))):
                        self.turns[DIR_UP] = True
                if 12 <= center_y % TILE_HEIGHT <= 18:
                    if (board.get_tile(center_y // TILE_HEIGHT, 
                                     (center_x - num3) // TILE_WIDTH) < 3 or
                        (board.get_tile(center_y // TILE_HEIGHT, 
                                      (center_x - num3) // TILE_WIDTH) == TILE_GATE and 
                         (self.in_box or self.dead))):
                        self.turns[DIR_LEFT] = True
                    if (board.get_tile(center_y // TILE_HEIGHT, 
                                     (center_x + num3) // TILE_WIDTH) < 3 or
                        (board.get_tile(center_y // TILE_HEIGHT, 
                                      (center_x + num3) // TILE_WIDTH) == TILE_GATE and 
                         (self.in_box or self.dead))):
                        self.turns[DIR_RIGHT] = True
        else:
            self.turns[DIR_RIGHT] = True
            self.turns[DIR_LEFT] = True
        
        # Check if in box
        if 350 < self.x < 550 and 370 < self.y < 480:
            self.in_box = True
        else:
            self.in_box = False
        
        return self.turns
    
    def move_towards_target(self):
        """Basic ghost movement towards target"""
        # Aggressive pursuit behavior
        if self.direction == DIR_RIGHT:
            if self.target[0] > self.x and self.turns[DIR_RIGHT]:
                self.x += self.speed
            elif not self.turns[DIR_RIGHT]:
                self._choose_new_direction()
            elif self.turns[DIR_RIGHT]:
                self.x += self.speed
                
        elif self.direction == DIR_LEFT:
            if self.target[0] < self.x and self.turns[DIR_LEFT]:
                self.x -= self.speed
            elif not self.turns[DIR_LEFT]:
                self._choose_new_direction()
            elif self.turns[DIR_LEFT]:
                self.x -= self.speed
                
        elif self.direction == DIR_UP:
            if self.target[1] < self.y and self.turns[DIR_UP]:
                self.y -= self.speed
            elif not self.turns[DIR_UP]:
                self._choose_new_direction()
            elif self.turns[DIR_UP]:
                self.y -= self.speed
                
        elif self.direction == DIR_DOWN:
            if self.target[1] > self.y and self.turns[DIR_DOWN]:
                self.y += self.speed
            elif not self.turns[DIR_DOWN]:
                self._choose_new_direction()
            elif self.turns[DIR_DOWN]:
                self.y += self.speed
        
        # Wrap around
        if self.x < -30:
            self.x = 900
        elif self.x > 900:
            self.x = -30
    
    def _choose_new_direction(self):
        """Choose new direction when blocked"""
        if self.target[1] > self.y and self.turns[DIR_DOWN]:
            self.direction = DIR_DOWN
            self.y += self.speed
        elif self.target[1] < self.y and self.turns[DIR_UP]:
            self.direction = DIR_UP
            self.y -= self.speed
        elif self.target[0] < self.x and self.turns[DIR_LEFT]:
            self.direction = DIR_LEFT
            self.x -= self.speed
        elif self.target[0] > self.x and self.turns[DIR_RIGHT]:
            self.direction = DIR_RIGHT
            self.x += self.speed
        elif self.turns[DIR_DOWN]:
            self.direction = DIR_DOWN
            self.y += self.speed
        elif self.turns[DIR_UP]:
            self.direction = DIR_UP
            self.y -= self.speed
        elif self.turns[DIR_LEFT]:
            self.direction = DIR_LEFT
            self.x -= self.speed
        elif self.turns[DIR_RIGHT]:
            self.direction = DIR_RIGHT
            self.x += self.speed
    
    def _draw_ghost_shape(self, screen, body_color, eye_color=(255,255,255),
                          pupil_color=(30,30,200), glow_color=None):
        """Vẽ ghost với hình dạng classic + neon glow"""
        cx = self.x + 22
        cy = self.y + 22
        r  = 18

        # Glow — dùng cache
        if glow_color:
            g = _make_glow(r + 10, glow_color[:3], alpha=35)
            screen.blit(g, (cx - r - 11, cy - r - 11))
        
        # Thân: nửa trên = hình tròn, nửa dưới = rạng cưa
        # Phần đầu tròn
        pygame.draw.circle(screen, body_color, (cx, cy - 2), r)
        pygame.draw.rect(screen, body_color,
                         (cx - r, cy - 2, r * 2, r + 4))
        
        # Rạng cưa dưới cùng (3 đỉnh)
        bot = cy + r + 2
        w3  = r * 2 // 3
        bumps = [
            (cx - r,      bot),
            (cx - r + w3, bot - 5),
            (cx - r + w3, bot),
            (cx,          bot - 5),
            (cx,          bot),
            (cx + w3,     bot - 5),
            (cx + w3,     bot),
            (cx + r,      bot),
            (cx + r,      cy - 2),
            (cx - r,      cy - 2),
        ]
        pygame.draw.polygon(screen, body_color, bumps)
        
        # Viền sáng
        pygame.draw.arc(screen, tuple(min(255, c + 60) for c in body_color),
                        (cx - r, cy - r - 2, r * 2, r * 2),
                        0, _math.pi, 1)
        
        # Mắt trái
        pygame.draw.ellipse(screen, eye_color,   (cx - 11, cy - 8,  10, 12))
        pygame.draw.ellipse(screen, pupil_color,  (cx - 9,  cy - 6,   6,  8))
        # Mắt phải
        pygame.draw.ellipse(screen, eye_color,   (cx + 1,  cy - 8,  10, 12))
        pygame.draw.ellipse(screen, pupil_color,  (cx + 3,  cy - 6,   6,  8))

    def draw(self, screen, powerup, eaten, spooked_img, dead_img):
        """Draw ghost với phong cách hiện đại"""
        # Map màu ghost theo ghost_id
        ghost_colors = [
            (220, 50,  50),   # Blinky — đỏ
            (60,  200, 180),  # Inky   — xanh cyan
            (230, 130, 200),  # Pinky  — hồng
            (230, 140, 40),   # Clyde  — cam
        ]
        glow_colors = [
            (200, 30,  30),
            (30,  180, 160),
            (210, 100, 180),
            (210, 120, 20),
        ]
        body_col = ghost_colors[self.ghost_id % 4]
        glow_col = glow_colors[self.ghost_id % 4]

        if self.dead:
            # Ghost chết: chỉ vẽ mắt mờ
            cx, cy = self.get_center()
            pygame.draw.ellipse(screen, (255,255,255), (cx - 11, cy - 8,  10, 12))
            pygame.draw.ellipse(screen, (30,30,200),   (cx - 9,  cy - 6,   6,  8))
            pygame.draw.ellipse(screen, (255,255,255), (cx + 1,  cy - 8,  10, 12))
            pygame.draw.ellipse(screen, (30,30,200),   (cx + 3,  cy - 6,   6,  8))
        elif powerup and not eaten:
            # Scared: xanh tím
            self._draw_ghost_shape(screen, (40, 40, 180),
                                   eye_color=(240,180,180),
                                   pupil_color=(200,50,50),
                                   glow_color=(20,20,120))
        else:
            self._draw_ghost_shape(screen, body_col,
                                   glow_color=glow_col)

        center_x, center_y = self.get_center()
        return pygame.Rect(center_x - 18, center_y - 18, 36, 36)
