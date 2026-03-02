import pygame
import random
import sys

pygame.init()

# Screen and grid
WIDTH, HEIGHT = 640, 480
SNAKE_SIZE = 20
COLS = WIDTH // SNAKE_SIZE
ROWS = HEIGHT // SNAKE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake — Map Select + Bonus Food")

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)        # normal food
YELLOW = (240, 200, 0)   # bonus food
BLUE = (0, 120, 200)     # walls
WHITE = (255, 255, 255)
HINT = (200, 50, 50)

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)

# ---------- Pattern functions (three maps) ----------
def pattern_border(exclude):
    obs = set()
    for c in range(COLS):
        obs.add((c * SNAKE_SIZE, 0))
        obs.add((c * SNAKE_SIZE, (ROWS - 1) * SNAKE_SIZE))
    for r in range(ROWS):
        obs.add((0, r * SNAKE_SIZE))
        obs.add(((COLS - 1) * SNAKE_SIZE, r * SNAKE_SIZE))
    return obs - exclude

def pattern_vertical_corridors(exclude):
    # vertical corridors: alternating wall columns leaving corridors
    obs = set()
    for c in range(0, COLS):
        if c % 4 == 0:  # wall column every 4 cols
            for r in range(0, ROWS):
                obs.add((c * SNAKE_SIZE, r * SNAKE_SIZE))
    return obs - exclude

def pattern_maze_deterministic(exclude):
    # deterministic pseudo-maze using fixed seed so map is repeatable
    obs = set()
    rnd = random.Random(42)
    # create several long wall segments
    for _ in range(8):
        cx = rnd.randrange(1, COLS - 1)
        cy = rnd.randrange(1, ROWS - 1)
        length = rnd.randint(max(COLS, ROWS) // 2, max(COLS, ROWS))
        for _ in range(length):
            obs.add((cx * SNAKE_SIZE, cy * SNAKE_SIZE))
            dir = rnd.choice([(1,0),(-1,0),(0,1),(0,-1)])
            nx, ny = cx + dir[0], cy + dir[1]
            if 1 <= nx < COLS - 1 and 1 <= ny < ROWS - 1:
                cx, cy = nx, ny
    return obs - exclude

PATTERNS = {
    1: ("Border", pattern_border),
    2: ("Vertical Corridors", pattern_vertical_corridors),
    3: ("Maze", pattern_maze_deterministic),
}

# ---------- Utility ----------
def random_cell(exclude):
    attempts = 0
    while True:
        rx = random.randrange(COLS) * SNAKE_SIZE
        ry = random.randrange(ROWS) * SNAKE_SIZE
        if (rx, ry) not in exclude:
            return rx, ry
        attempts += 1
        if attempts > 2000:
            # fallback: find any free cell
            for cx in range(COLS):
                for cy in range(ROWS):
                    cell = (cx * SNAKE_SIZE, cy * SNAKE_SIZE)
                    if cell not in exclude:
                        return cell

def wrap_position(x, y):
    if x < 0:
        x = WIDTH - SNAKE_SIZE
    elif x >= WIDTH:
        x = 0
    if y < 0:
        y = HEIGHT - SNAKE_SIZE
    elif y >= HEIGHT:
        y = 0
    return x, y

def draw_snake(snake):
    for x, y in snake:
        pygame.draw.rect(screen, GREEN, (x, y, SNAKE_SIZE, SNAKE_SIZE))

def draw_obstacles(obstacles):
    for ox, oy in obstacles:
        pygame.draw.rect(screen, BLUE, (ox, oy, SNAKE_SIZE, SNAKE_SIZE))

# ---------- Menu to choose map ----------
def menu_select_map():
    selected = None
    while selected not in (1,2,3):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected = 1
                elif event.key == pygame.K_2:
                    selected = 2
                elif event.key == pygame.K_3:
                    selected = 3
                elif event.key == pygame.K_q:
                    pygame.quit(); sys.exit()
        screen.fill(BLACK)
        title = font.render("Select Map (press 1 / 2 / 3). Q to quit.", True, WHITE)
        m1 = font.render("1 - Border", True, WHITE)
        m2 = font.render("2 - Vertical Corridors", True, WHITE)
        m3 = font.render("3 - Maze (deterministic)", True, WHITE)
        screen.blit(title, (20, 40))
        screen.blit(m1, (40, 100))
        screen.blit(m2, (40, 140))
        screen.blit(m3, (40, 180))
        pygame.display.update()
        clock.tick(30)
    return selected

# ---------- Main game ----------
def game_loop(selected_map_index):
    score = 0
    speed = 6  # base speed (lower = slower)
    # snake initial
    x = (COLS // 2) * SNAKE_SIZE
    y = (ROWS // 2) * SNAKE_SIZE
    snake = [(x, y)]
    snake_length = 3
    dx, dy = 0, 0
    last_dx, last_dy = 0, 0

    # pattern selection
    pattern_name, pattern_func = PATTERNS[selected_map_index]
    exclude = set(snake)
    obstacles = pattern_func(exclude)

    # normal food
    food_x, food_y = random_cell(exclude | obstacles)

    # bonus food state
    BONUS_DURATION_MS = 4000
    BONUS_EXTRA_POINTS = 5
    bonus_active = False
    bonus_pos = (0,0)
    bonus_spawn_time = 0
    # spawn bonus after every 5 normal points eaten (i.e., when score becomes multiple of 5)
    last_bonus_spawn_score = -1

    started = False
    running = True
    while running:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                # WASD controls with prevention of immediate reverse
                if event.key == pygame.K_w and not (last_dy == SNAKE_SIZE):
                    dx, dy = 0, -SNAKE_SIZE; started = True
                elif event.key == pygame.K_s and not (last_dy == -SNAKE_SIZE):
                    dx, dy = 0, SNAKE_SIZE; started = True
                elif event.key == pygame.K_a and not (last_dx == SNAKE_SIZE):
                    dx, dy = -SNAKE_SIZE, 0; started = True
                elif event.key == pygame.K_d and not (last_dx == -SNAKE_SIZE):
                    dx, dy = SNAKE_SIZE, 0; started = True
                if event.key == pygame.K_q:
                    pygame.quit(); sys.exit()

        # expire bonus after duration
        if bonus_active and now - bonus_spawn_time >= BONUS_DURATION_MS:
            bonus_active = False

        if started:
            x += dx; y += dy
            x, y = wrap_position(x, y)
            if dx != 0 or dy != 0:
                last_dx, last_dy = dx, dy

            head = (x, y)
            snake.append(head)
            if len(snake) > snake_length:
                del snake[0]

            # collisions
            if head in snake[:-1]:
                running = False
            if head in obstacles:
                running = False

            # eat normal food
            if head == (food_x, food_y):
                score += 1            # normal food = 1 point
                snake_length += 1
                speed = min(20, speed + 0.3)

                # keep obstacles consistent with current snake (remove any overlapping)
                exclude = set(snake)
                obstacles = pattern_func(exclude)

                # place new normal food
                food_x, food_y = random_cell(exclude | obstacles)

                # spawn bonus when score is a multiple of 5 (and not already spawned for this score)
                if score > 0 and score % 5 == 0 and last_bonus_spawn_score != score:
                    # spawn bonus (separate item) not overlapping snake/obstacles/food
                    bpos = random_cell(exclude | obstacles | {(food_x, food_y)})
                    bonus_pos = bpos
                    bonus_active = True
                    bonus_spawn_time = pygame.time.get_ticks()
                    last_bonus_spawn_score = score

            # eat bonus food
            if bonus_active and head == bonus_pos:
                score += BONUS_EXTRA_POINTS
                snake_length += 1
                bonus_active = False

        # draw
        screen.fill(BLACK)
        draw_snake(snake)
        pygame.draw.rect(screen, RED, (food_x, food_y, SNAKE_SIZE, SNAKE_SIZE))
        if bonus_active:
            bx, by = bonus_pos
            pygame.draw.rect(screen, YELLOW, (bx, by, SNAKE_SIZE, SNAKE_SIZE))
        draw_obstacles(obstacles)

        # HUD
        score_surf = font.render(f"Score: {score}", True, WHITE)
        pattern_surf = font.render(f"Map: {pattern_name}", True, WHITE)
        hint_surf = font.render("Press W/A/S/D to start. Q to quit.", True, HINT)
        screen.blit(score_surf, (10, 8))
        screen.blit(pattern_surf, (10, 30))
        screen.blit(hint_surf, (10, 52))

        # bonus info
        if bonus_active:
            remaining_ms = max(0, BONUS_DURATION_MS - (now - bonus_spawn_time))
            remaining_s = remaining_ms / 1000.0
            bonus_surf = font.render(f"Bonus +{BONUS_EXTRA_POINTS} (expires {remaining_s:.1f}s)", True, YELLOW)
            screen.blit(bonus_surf, (10, 76))
        else:
            info = font.render("Bonus spawns after every 5 normal points eaten", True, HINT)
            screen.blit(info, (10, 76))

        if not started:
            start_hint = font.render("Game paused — press W/A/S/D to start", True, HINT)
            screen.blit(start_hint, (WIDTH // 2 - start_hint.get_width() // 2, HEIGHT - 40))

        pygame.display.update()
        clock.tick(speed)

    # game over screen
    screen.fill(BLACK)
    go = font.render("Game Over - Press R to Restart or Q to Quit", True, HINT)
    final = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(go, (WIDTH // 8, HEIGHT // 2 - 20))
    screen.blit(final, (WIDTH // 2 - 60, HEIGHT // 2 + 10))
    pygame.display.update()

    # wait for restart or quit
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_r:
                    return  # return to outer loop to restart

# ---------- Program entry ----------
def main():
    while True:
        selected = menu_select_map()
        game_loop(selected)

if __name__ == "__main__":
    main()