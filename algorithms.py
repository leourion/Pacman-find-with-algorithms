"""
Search algorithms module - BFS, DFS, UCS, A*, Minimax, Alpha-Beta Pruning
Complete implementation with all required algorithms

FIXES applied:
  FIX #1 - UCS dùng weighted cost map thay vì cost = 1 đồng nhất,
            nên kết quả thực sự khác BFS (tìm đường tổng cost thấp nhất,
            ưu tiên đi qua ô có chấm, tránh vùng ghost house).
  FIX #2 - is_walkable_for_pacman() tách riêng khỏi is_walkable() của ghost,
            Pacman không được đi qua TILE_GATE nữa.
  FIX #3 - reconstruct_path trả về None khi không tìm thấy đường,
            phân biệt rõ "không có đường" vs "đã ở đích".
  FIX #4 - visited_nodes tích lũy (không reset mỗi lần replan) giúp
            visualize rõ sự khác biệt giữa A* và UCS.
  FIX #5 - Thêm switch heuristic bằng phím H (Manhattan ↔ Euclidean).
  FIX #6 - Fallback khi không tìm được đường: log rõ ràng + set new goal.
  FIX #7 - Thêm thống kê thời gian tìm đường (ms).
"""
from collections import deque
import heapq
import math
import time
from config import *


# ---------------------------------------------------------------------------
# Heuristic functions
# ---------------------------------------------------------------------------

def _wrapped_delta_col(pos1, pos2, board=None):
    """Khoang cach cot ngan nhat, co tinh tunnel wrap-around neu co board."""
    dx = abs(pos1[1] - pos2[1])
    if board is None or not board.level:
        return dx
    max_col = len(board.level[0])
    return min(dx, max_col - dx)

def manhattan_distance(pos1, pos2, board=None):
    """Khoảng cách Manhattan giữa hai ô lưới"""
    return abs(pos1[0] - pos2[0]) + _wrapped_delta_col(pos1, pos2, board)

def euclidean_distance(pos1, pos2, board=None):
    """Khoảng cách Euclidean giữa hai ô lưới"""
    dy = abs(pos1[0] - pos2[0])
    dx = _wrapped_delta_col(pos1, pos2, board)
    return math.sqrt(dy**2 + dx**2)


# ---------------------------------------------------------------------------
# Board helpers
# ---------------------------------------------------------------------------

def is_walkable_pacman(row, col, board):
    """
    FIX #2: Pacman KHÔNG đi qua TILE_GATE.
    Hàm riêng cho pathfinding của Pacman, khác với is_walkable() của ghost.
    """
    if row < 0 or row >= len(board.level) or col < 0 or col >= len(board.level[0]):
        return False
    tile = board.level[row][col]
    # Pacman chỉ đi được qua: EMPTY, DOT, POWER_PELLET
    return tile in (TILE_EMPTY, TILE_DOT, TILE_POWER_PELLET)


def get_neighbors(pos, board):
    """
    Trả về danh sách ô kề có thể đi được (dành cho Pacman).
    Dùng is_walkable_pacman — Pacman không qua cổng ghost house.
    Xử lý wrap-around: cột âm hoặc >= max_col được wrap lại.
    """
    row, col = pos
    max_col = len(board.level[0]) if board.level else 30
    # Clamp col về [0, max_col-1] nếu player vừa wrap màn hình
    if col < 0 or col >= max_col:
        col = col % max_col
    neighbors = []
    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nr, nc = row + dr, col + dc
        # Wrap ngang (tunnel trái-phải)
        nc = nc % max_col
        if is_walkable_pacman(nr, nc, board):
            neighbors.append((nr, nc))
    return neighbors


def get_tile_cost(row, col, board):
    """
    FIX #1: Trả về cost thực tế của ô (row, col) cho UCS.
    - Ô có chấm (DOT, POWER_PELLET): cost = 1 → ưu tiên đi qua
    - Ô trống (EMPTY): cost = 2 → ít ưu tiên hơn
    - Ô trong vùng ghost house: cộng thêm GHOST_HOUSE_COST
    Kết quả: UCS tìm đường ưu tiên ăn chấm, tránh vùng ghost house.
    """
    tile = board.level[row][col]
    base_cost = UCS_TILE_COSTS.get(tile, 1)

    # Tăng cost nếu ô nằm trong vùng ghost house
    if (GHOST_HOUSE_ROW_MIN <= row <= GHOST_HOUSE_ROW_MAX and
            GHOST_HOUSE_COL_MIN <= col <= GHOST_HOUSE_COL_MAX):
        base_cost += GHOST_HOUSE_COST

    return base_cost


def reconstruct_path(came_from, start, goal):
    """
    FIX #3: Trả về path (list) hoặc None nếu không tìm được đường.
    - Trả về [] chỉ khi start == goal (đã ở đích).
    - Trả về None khi goal không có trong came_from (không có đường).
    """
    if goal not in came_from and goal != start:
        return None   # Không tìm được đường

    path = []
    current = goal
    while current != start and current in came_from:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path


# ---------------------------------------------------------------------------
# BFS
# ---------------------------------------------------------------------------

class BFS:
    """Breadth-First Search — tìm đường ngắn nhất (số bước)"""

    @staticmethod
    def search(start, goal, board, return_trace=False):
        """
        Returns: (path, visited_nodes)
          path: list các ô từ ô kế start đến goal, hoặc [] nếu không có đường
          visited_nodes: set các ô đã thăm
        """
        queue = deque([start])
        came_from = {start: None}
        visited = {start}

        while queue:
            current = queue.popleft()
            if current == goal:
                path = reconstruct_path(came_from, start, goal)
                return (path if path is not None else []), visited

            for neighbor in get_neighbors(current, board):
                if neighbor not in visited:
                    visited.add(neighbor)
                    came_from[neighbor] = current
                    queue.append(neighbor)

        return [], visited  # Không có đường


# ---------------------------------------------------------------------------
# DFS
# ---------------------------------------------------------------------------

class DFS:
    """Depth-First Search — tìm đường (không đảm bảo tối ưu)"""

    @staticmethod
    def search(start, goal, board, max_depth=100):
        """
        Returns: (path, visited_nodes)
        """
        stack = [(start, [start])]
        visited = {start}

        while stack:
            current, path = stack.pop()
            if current == goal:
                return path[1:], visited
            if len(path) > max_depth:
                continue
            for neighbor in get_neighbors(current, board):
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append((neighbor, path + [neighbor]))

        return [], visited


# ---------------------------------------------------------------------------
# UCS — FIX #1: dùng weighted cost map, kết quả thực sự khác BFS
# ---------------------------------------------------------------------------

class UCS:
    """
    Uniform Cost Search (Dijkstra).

    FIX #1: Mỗi ô có cost khác nhau (xem get_tile_cost).
    UCS tìm đường có tổng cost thấp nhất, không phải ít bước nhất.
    Khi báo cáo: UCS ưu tiên đường qua nhiều chấm (cost = 1),
    tránh ô trống (cost = 2) và vùng ghost house (cost = 5+).
    """

    @staticmethod
    def search(start, goal, board, return_trace=False):
        """
        Returns: (path, visited_nodes, total_cost)
          total_cost: tổng chi phí đường đi (để hiển thị so sánh với A*)
        """
        # Priority queue: (cost, position)
        pq = [(0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0}
        visited = {}
        trace = []

        while pq:
            current_cost, current = heapq.heappop(pq)

            if current in visited:
                continue
            visited[current] = None
            trace.append({"node": current, "parent": came_from.get(current),
                          "g": current_cost, "h": 0, "f": current_cost})

            if current == goal:
                path = reconstruct_path(came_from, start, goal)
                if return_trace:
                    return (path if path is not None else []), visited, current_cost, trace
                return (path if path is not None else []), visited, current_cost

            for neighbor in get_neighbors(current, board):
                # FIX #1: dùng cost thực của ô neighbor, không phải 1 đồng nhất
                step_cost = get_tile_cost(neighbor[0], neighbor[1], board)
                new_cost = current_cost + step_cost

                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    heapq.heappush(pq, (new_cost, neighbor))
                    came_from[neighbor] = current

        if return_trace:
            return [], visited, float('inf'), trace
        return [], visited, float('inf')


# ---------------------------------------------------------------------------
# A* — FIX #2: get_neighbors dùng is_walkable_pacman (không qua TILE_GATE)
# ---------------------------------------------------------------------------

class GBFS:
    """
    Greedy Best-First Search.

    Chon node theo f(n) = h(n), tuc la chi nhin uoc luong khoang cach toi goal.
    Khac UCS va A*: GBFS khong dung g(n) de sap xep frontier, nen nhanh va huong dich
    tot, nhung khong dam bao duong di toi uu.
    """

    @staticmethod
    def search(start, goal, board, heuristic=manhattan_distance, return_trace=False):
        """
        Returns: (path, visited_nodes, total_cost)
          total_cost: chi phi weighted cua path tim duoc, chi de hien thi/so sanh.
        """
        pq = [(heuristic(start, goal, board), 0, start)]
        came_from = {start: None}
        visited = {}
        trace = []
        counter = 1

        while pq:
            h_value, _, current = heapq.heappop(pq)

            if current in visited:
                continue
            visited[current] = None
            trace.append({"node": current, "parent": came_from.get(current),
                          "g": None, "h": h_value, "f": h_value})

            if current == goal:
                path = reconstruct_path(came_from, start, goal)
                if path is None:
                    if return_trace:
                        return [], visited, float('inf'), trace
                    return [], visited, float('inf')
                total_cost = sum(get_tile_cost(row, col, board) for row, col in path)
                if return_trace:
                    return path, visited, total_cost, trace
                return path, visited, total_cost

            for neighbor in get_neighbors(current, board):
                if neighbor in visited or neighbor in came_from:
                    continue
                came_from[neighbor] = current
                heapq.heappush(pq, (heuristic(neighbor, goal, board), counter, neighbor))
                counter += 1

        if return_trace:
            return [], visited, float('inf'), trace
        if return_trace:
            return [], visited, float('inf'), trace
        return [], visited, float('inf')


class AStar:
    """
    A* Search — tìm đường tối ưu với heuristic.
    f(n) = g(n) + h(n)
      g(n): cost thực từ start đến n (giống UCS, dùng uniform cost = 1/bước)
      h(n): ước lượng cost từ n đến goal (Manhattan hoặc Euclidean)

    Lưu ý: A* dùng cost đồng nhất (g = số bước) để đảm bảo admissible
    với Manhattan heuristic. UCS dùng weighted cost để minh họa sự khác biệt.
    """

    @staticmethod
    def search(start, goal, board, heuristic=manhattan_distance, return_trace=False):
        """
        Returns: (path, visited_nodes, total_cost)
          heuristic: hàm heuristic — manhattan_distance hoặc euclidean_distance
        """
        # Priority queue: (f_score, g_score, position)
        # Thêm g_score như tie-breaker để sort ổn định
        pq = [(heuristic(start, goal, board), 0, start)]
        came_from = {start: None}
        g_score = {start: 0}
        visited = {}
        trace = []

        while pq:
            f, g, current = heapq.heappop(pq)

            if current in visited:
                continue
            visited[current] = None
            h_value = heuristic(current, goal, board)
            trace.append({"node": current, "parent": came_from.get(current),
                          "g": g, "h": h_value, "f": f})

            if current == goal:
                path = reconstruct_path(came_from, start, goal)
                if return_trace:
                    return (path if path is not None else []), visited, g, trace
                return (path if path is not None else []), visited, g

            for neighbor in get_neighbors(current, board):
                tentative_g = g_score[current] + get_tile_cost(neighbor[0], neighbor[1], board)

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, goal, board)
                    heapq.heappush(pq, (f_score, tentative_g, neighbor))
                    came_from[neighbor] = current

        if return_trace:
            return [], visited, float('inf'), trace
        return [], visited, float('inf')


# ---------------------------------------------------------------------------
# Minimax & Alpha-Beta (không thay đổi logic, chỉ dùng get_neighbors mới)
# ---------------------------------------------------------------------------

class Minimax:
    """Minimax Algorithm for adversarial search"""

    @staticmethod
    def evaluate_state(player_pos, ghost_positions, board):
        score = 0
        if ghost_positions:
            min_ghost_dist = min(manhattan_distance(player_pos, g) for g in ghost_positions)
            score += min_ghost_dist * 10
        dots = board.get_all_dots()
        if dots:
            min_dot_dist = min(manhattan_distance(player_pos, d) for d in dots)
            score -= min_dot_dist * 5
        neighbors = get_neighbors(player_pos, board)
        score += len(neighbors) * 2
        return score

    @staticmethod
    def minimax(player_pos, ghost_positions, board, depth, is_maximizing):
        if depth == 0:
            return Minimax.evaluate_state(player_pos, ghost_positions, board), player_pos

        if is_maximizing:
            max_eval = float('-inf')
            best_move = player_pos
            for neighbor in get_neighbors(player_pos, board):
                eval_score, _ = Minimax.minimax(neighbor, ghost_positions, board,
                                                depth - 1, False)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = neighbor
            return max_eval, best_move
        else:
            min_eval = float('inf')
            new_ghost_positions = []
            for ghost_pos in ghost_positions:
                ghost_neighbors = get_neighbors(ghost_pos, board)
                if ghost_neighbors:
                    closest = min(ghost_neighbors,
                                  key=lambda p: manhattan_distance(p, player_pos))
                    new_ghost_positions.append(closest)
                else:
                    new_ghost_positions.append(ghost_pos)
            eval_score, _ = Minimax.minimax(player_pos, new_ghost_positions, board,
                                            depth - 1, True)
            return min(min_eval, eval_score), player_pos

    @staticmethod
    def get_best_move(player_pos, ghost_positions, board, depth=MINIMAX_DEPTH):
        _, best_move = Minimax.minimax(player_pos, ghost_positions, board, depth, True)
        return best_move


class AlphaBeta:
    """Alpha-Beta Pruning optimization of Minimax"""

    @staticmethod
    def evaluate_state(player_pos, ghost_positions, board):
        return Minimax.evaluate_state(player_pos, ghost_positions, board)

    @staticmethod
    def alphabeta(player_pos, ghost_positions, board, depth, alpha, beta, is_maximizing):
        if depth == 0:
            return AlphaBeta.evaluate_state(player_pos, ghost_positions, board), player_pos

        if is_maximizing:
            max_eval = float('-inf')
            best_move = player_pos
            for neighbor in get_neighbors(player_pos, board):
                eval_score, _ = AlphaBeta.alphabeta(neighbor, ghost_positions, board,
                                                     depth - 1, alpha, beta, False)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = neighbor
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            new_ghost_positions = []
            for ghost_pos in ghost_positions:
                ghost_neighbors = get_neighbors(ghost_pos, board)
                if ghost_neighbors:
                    closest = min(ghost_neighbors,
                                  key=lambda p: manhattan_distance(p, player_pos))
                    new_ghost_positions.append(closest)
                else:
                    new_ghost_positions.append(ghost_pos)
            eval_score, _ = AlphaBeta.alphabeta(player_pos, new_ghost_positions, board,
                                                depth - 1, alpha, beta, True)
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            return min_eval, player_pos

    @staticmethod
    def get_best_move(player_pos, ghost_positions, board, depth=ALPHABETA_DEPTH):
        _, best_move = AlphaBeta.alphabeta(player_pos, ghost_positions, board,
                                           depth, float('-inf'), float('inf'), True)
        return best_move


# ---------------------------------------------------------------------------
# PathfindingAgent — tổng hợp tất cả fixes
# ---------------------------------------------------------------------------

class PathfindingAgent:
    """
    Agent điều khiển Pacman bằng các thuật toán tìm đường.

    Fixes tổng hợp:
      FIX #4 - accumulated_visited: visited nodes tích lũy không reset,
               giúp visualize rõ vùng A* vs UCS đã explore.
      FIX #5 - heuristic_mode: toggle Manhattan/Euclidean bằng phím H.
      FIX #6 - Xử lý không tìm được đường: log + set new goal tự động.
      FIX #7 - last_search_time_ms: thống kê thời gian tìm đường.
      FIX #7 - last_path_cost: tổng cost đường đi (UCS/A*).
    """

    def __init__(self, algorithm_mode=MODE_MANUAL):
        self.algorithm_mode = algorithm_mode
        self.current_path = []
        self.path_index = 0
        self.visited_nodes = set()
        self.visited_order = []
        self.search_trace = []
        self.visited_edges = []
        self.accumulated_visited = set()  # FIX #4: tích lũy qua nhiều lần tìm
        self.last_direction = None
        self.heuristic_mode = 'manhattan'   # FIX #5: 'manhattan' hoặc 'euclidean'
        self.last_search_time_ms = 0.0      # FIX #7: thời gian tìm đường
        self.last_path_cost = 0             # FIX #7: tổng cost đường đi
        self.no_path_count = 0             # FIX #6: đếm lần không tìm được đường

    def set_algorithm(self, mode):
        """Đổi thuật toán — reset path và visited"""
        self.algorithm_mode = mode
        self.current_path = []
        self.path_index = 0
        self.visited_nodes = set()
        self.visited_order = []
        self.search_trace = []
        self.visited_edges = []
        self.accumulated_visited = set()
        self.last_direction = None
        self.last_search_time_ms = 0.0
        self.last_path_cost = 0
        self.no_path_count = 0

    def toggle_heuristic(self):
        """FIX #5: Toggle Manhattan ↔ Euclidean, reset path để recompute"""
        if self.heuristic_mode == 'manhattan':
            self.heuristic_mode = 'euclidean'
        else:
            self.heuristic_mode = 'manhattan'
        # Reset để buộc tìm đường lại với heuristic mới
        self.current_path = []
        self.path_index = 0
        self.visited_nodes = set()
        self.visited_order = []
        self.search_trace = []
        self.visited_edges = []
        self.accumulated_visited = set()
        print(f"[A*] Heuristic switched to: {self.heuristic_mode}")

    def get_heuristic_fn(self):
        """Trả về hàm heuristic hiện tại"""
        return manhattan_distance if self.heuristic_mode == 'manhattan' else euclidean_distance

    def find_nearest_dot(self, player_pos, board):
        """Tìm chấm gần nhất theo tọa độ pixel player"""
        dots = board.get_all_dots()
        if not dots:
            return None
        center_x = player_pos[0] + TILE_WIDTH // 2
        center_y = player_pos[1] + TILE_HEIGHT // 2
        player_grid = (center_y // TILE_HEIGHT, center_x // TILE_WIDTH)
        return min(dots, key=lambda d: manhattan_distance(player_grid, d))

    def _run_search(self, player_grid, goal, board):
        """
        Chạy thuật toán đã chọn, đo thời gian, cập nhật thống kê.
        FIX #6: Xử lý khi không tìm được đường.
        FIX #7: Đo thời gian bằng time.perf_counter.
        Returns: path (list hoặc []) — đã xử lý None thành [].
        """
        t_start = time.perf_counter()
        path = []
        cost = 0
        trace = []

        if self.algorithm_mode == MODE_BFS:
            path, self.visited_nodes = BFS.search(player_grid, goal, board)

        elif self.algorithm_mode == MODE_DFS:
            path, self.visited_nodes = DFS.search(player_grid, goal, board)

        elif self.algorithm_mode == MODE_UCS:
            path, self.visited_nodes, cost, trace = UCS.search(
                player_grid, goal, board, return_trace=True)

        elif self.algorithm_mode == MODE_ASTAR:
            hfn = self.get_heuristic_fn()
            path, self.visited_nodes, cost, trace = AStar.search(
                player_grid, goal, board, hfn, return_trace=True)

        elif self.algorithm_mode == MODE_GBFS:
            hfn = self.get_heuristic_fn()
            path, self.visited_nodes, cost, trace = GBFS.search(
                player_grid, goal, board, hfn, return_trace=True)

        t_end = time.perf_counter()
        self.last_search_time_ms = (t_end - t_start) * 1000
        self.last_path_cost = cost
        if isinstance(self.visited_nodes, dict):
            self.visited_order = list(self.visited_nodes.keys())
            self.visited_nodes = set(self.visited_order)
        else:
            self.visited_order = list(self.visited_nodes)
        self.search_trace = trace
        self.visited_edges = [(item["parent"], item["node"]) for item in trace
                              if item.get("parent") is not None]

        # FIX #4: tích lũy visited nodes
        self.accumulated_visited |= self.visited_nodes

        # FIX #6: log khi không tìm được đường
        if path is None or (len(path) == 0 and player_grid != goal):
            self.no_path_count += 1
            print(f"[{self.algorithm_mode}] Không tìm được đường từ {player_grid} đến {goal} "
                  f"(lần {self.no_path_count})")
            return []

        self.no_path_count = 0
        algo_name = {MODE_BFS: "BFS", MODE_DFS: "DFS",
                     MODE_UCS: "UCS", MODE_ASTAR: "A*",
                     MODE_GBFS: "GBFS"}.get(self.algorithm_mode, "?")
        hname = f" [{self.heuristic_mode}]" if self.algorithm_mode in (MODE_ASTAR, MODE_GBFS) else ""
        print(f"[{algo_name}{hname}] {player_grid}→{goal} | "
              f"steps={len(path)} | visited={len(self.visited_nodes)} | "
              f"cost={cost} | time={self.last_search_time_ms:.2f}ms")
        return path

    def get_next_move(self, player_pos, ghost_positions, board, goal=None):
        """
        Tính bước đi tiếp theo dựa trên thuật toán đang chọn.
        Returns: direction (0-3) hoặc None nếu không có nước đi.
        """
        center_x = player_pos[0] + TILE_WIDTH // 2
        center_y = player_pos[1] + TILE_HEIGHT // 2
        player_grid = (center_y // TILE_HEIGHT, center_x // TILE_WIDTH)

        # --- Minimax / Alpha-Beta ---
        if self.algorithm_mode == MODE_MINIMAX:
            ghost_grids = []
            for g in ghost_positions:
                gx = g[0] + TILE_WIDTH // 2
                gy = g[1] + TILE_HEIGHT // 2
                ghost_grids.append((gy // TILE_HEIGHT, gx // TILE_WIDTH))

            next_pos = AlphaBeta.get_best_move(player_grid, ghost_grids, board)
            direction = self._position_to_direction(player_grid, next_pos) if next_pos else None

            if direction is None:
                direction = self._fallback_direction(player_grid, ghost_grids, board)

            self.last_direction = direction
            return direction

        # --- Pathfinding (BFS / DFS / UCS / A*) ---
        need_replan = (
            not self.current_path or
            self.path_index >= len(self.current_path)
        )

        if need_replan:
            if goal is None:
                goal = self.find_nearest_dot((player_pos[0], player_pos[1]), board)
            if not goal:
                return None

            self.current_path = self._run_search(player_grid, goal, board)
            self.path_index = 0

            # FIX #6: Không tìm được đường → tự tìm goal khác
            if not self.current_path:
                return None

        # Bước theo path node-by-node
        if self.current_path and self.path_index < len(self.current_path):
            next_grid = self.current_path[self.path_index]

            if player_grid == next_grid:
                self.path_index += 1
                if self.path_index >= len(self.current_path):
                    return None
                next_grid = self.current_path[self.path_index]

            # Nếu path bị lỗi (khoảng cách > 1) → replan
            if abs(next_grid[0] - player_grid[0]) + abs(next_grid[1] - player_grid[1]) > 1:
                if goal is None:
                    goal = self.find_nearest_dot((player_pos[0], player_pos[1]), board)
                if not goal:
                    return None
                self.current_path = self._run_search(player_grid, goal, board)
                self.path_index = 0
                if not self.current_path:
                    return None
                next_grid = self.current_path[self.path_index]

            dr = next_grid[0] - player_grid[0]
            dc = next_grid[1] - player_grid[1]
            if dc == 1:
                self.last_direction = DIR_RIGHT; return DIR_RIGHT
            elif dc == -1:
                self.last_direction = DIR_LEFT; return DIR_LEFT
            elif dr == -1:
                self.last_direction = DIR_UP; return DIR_UP
            elif dr == 1:
                self.last_direction = DIR_DOWN; return DIR_DOWN

        return None

    def _position_to_direction(self, current, target):
        """Chuyển từ vị trí grid sang direction"""
        dr = target[0] - current[0]
        dc = target[1] - current[1]
        if dc > 0: return DIR_RIGHT
        if dc < 0: return DIR_LEFT
        if dr < 0: return DIR_UP
        if dr > 0: return DIR_DOWN
        return None

    def _fallback_direction(self, player_grid, ghost_grids, board):
        """Fallback khi Minimax không trả về bước đi hợp lệ"""
        candidates = get_neighbors(player_grid, board)
        if not candidates:
            return None

        def opposite(d):
            return {DIR_RIGHT: DIR_LEFT, DIR_LEFT: DIR_RIGHT,
                    DIR_UP: DIR_DOWN, DIR_DOWN: DIR_UP}.get(d)

        def pos_to_dir(cur, nxt):
            dr, dc = nxt[0] - cur[0], nxt[1] - cur[1]
            if dc == 1: return DIR_RIGHT
            if dc == -1: return DIR_LEFT
            if dr == -1: return DIR_UP
            if dr == 1: return DIR_DOWN
            return None

        dots = board.get_all_dots()

        def dot_dist(p):
            return min((manhattan_distance(p, d) for d in dots), default=0)

        def ghost_dist(p):
            return min((manhattan_distance(p, g) for g in ghost_grids), default=10)

        scored = []
        for nxt in candidates:
            d = pos_to_dir(player_grid, nxt)
            reverse_penalty = (5 if self.last_direction is not None
                               and d == opposite(self.last_direction)
                               and len(candidates) > 1 else 0)
            score = (-2 * dot_dist(nxt) + 1.0 * ghost_dist(nxt)
                     + 0.3 * len(get_neighbors(nxt, board)) - reverse_penalty)
            scored.append((score, nxt, d))

        scored.sort(reverse=True, key=lambda t: t[0])
        return scored[0][2]
