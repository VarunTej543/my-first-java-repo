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
pygame.display.set_caption("Snake — Border Walls Only (WASD)")

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 120, 200)
WHITE = (255, 255, 255)
HINT = (200, 50, 50)

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)

def draw_snake(snake):
    for x, y in snake:
        pygame.draw.rect(screen, GREEN, (x, y, SNAKE_SIZE, SNAKE_SIZE))

def draw_obstacles(obstacles):
    for ox, oy in obstacles:
        pygame.draw.rect(screen, BLUE, (ox, oy, SNAKE_SIZE, SNAKE_SIZE))

def random_cell(exclude):
    attempts = 0
    while True:
        rx = random.randrange(COLS) * SNAKE_SIZE
        ry = random.randrange(ROWS) * SNAKE_SIZE
        if (rx, ry) not in exclude:
            return rx, ry
        attempts += 1
        if attempts > 1000:
            for cx in range(COLS):
                for cy in range(ROWS):
                    cell = (cx * SNAKE_SIZE, cy * SNAKE_SIZE)
                    if cell not in exclude:
                        return cell

def pattern_border(exclude):
    """Return border wall cells (as (x,y) tuples) excluding any in exclude."""
    obs = set()
    for c in range(COLS):
        obs.add((c * SNAKE_SIZE, 0))
        obs.add((c * SNAKE_SIZE, (ROWS - 1) * SNAKE_SIZE))
    for r in range(ROWS):
        obs.add((0, r * SNAKE_SIZE))
        obs.add(((COLS - 1) * SNAKE_SIZE, r * SNAKE_SIZE))
    return obs - exclude

def wrap_position(x, y):
    """Wrap coordinates so crossing an edge teleports to the opposite side."""
    if x < 0:
        x = WIDTH - SNAKE_SIZE
    elif x >= WIDTH:
        x = 0
    if y < 0:
        y = HEIGHT - SNAKE_SIZE
    elif y >= HEIGHT:
        y = 0
    return x, y

def game_loop():
    score = 0
    speed = 6  # slower default

    # initial snake (center)
    x = (COLS // 2) * SNAKE_SIZE
    y = (ROWS // 2) * SNAKE_SIZE
    snake = [(x, y)]
    snake_length = 3
    dx, dy = 0, 0
    last_dx, last_dy = 0, 0

    # Use border pattern only
    exclude = set(snake)
    obstacles = pattern_border(exclude)

    # place food not on snake or obstacles
    food_x, food_y = random_cell(exclude | obstacles)

    started = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # WASD controls with prevention of immediate reverse
                if event.key == pygame.K_w and not (last_dy == SNAKE_SIZE):
                    dx, dy = 0, -SNAKE_SIZE
                    started = True
                elif event.key == pygame.K_s and not (last_dy == -SNAKE_SIZE):
                    dx, dy = 0, SNAKE_SIZE
                    started = True
                elif event.key == pygame.K_a and not (last_dx == SNAKE_SIZE):
                    dx, dy = -SNAKE_SIZE, 0
                    started = True
                elif event.key == pygame.K_d and not (last_dx == -SNAKE_SIZE):
                    dx, dy = SNAKE_SIZE, 0
                    started = True

                # Quit key
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

        # Only move when started
        if started:
            x += dx
            y += dy

            # Wrap around edges
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

            # eat food
            if head == (food_x, food_y):
                score += 10
                snake_length += 1
                # gentle speed increase
                speed = min(20, speed + 0.4)

                # border pattern remains the same but ensure it doesn't overlap the snake
                exclude = set(snake)
                obstacles = pattern_border(exclude)

                # place new food not on snake or obstacles
                food_x, food_y = random_cell(exclude | obstacles)

        # draw
        screen.fill(BLACK)
        draw_snake(snake)
        pygame.draw.rect(screen, RED, (food_x, food_y, SNAKE_SIZE, SNAKE_SIZE))
        draw_obstacles(obstacles)

        # HUD
        score_surf = font.render(f"Score: {score}", True, WHITE)
        pattern_surf = font.render("Pattern: Border (fixed)", True, WHITE)
        hint_surf = font.render("Press W/A/S/D to start. Q to quit.", True, HINT)

        screen.blit(score_surf, (10, 8))
        screen.blit(pattern_surf, (10, 30))
        screen.blit(hint_surf, (10, 52))

        if not started:
            start_hint = font.render("Game paused — press W/A/S/D to start", True, HINT)
            screen.blit(start_hint, (WIDTH // 2 - start_hint.get_width() // 2, HEIGHT - 40))

        pygame.display.update()
        clock.tick(speed)

    # game over
    screen.fill(BLACK)
    go = font.render("Game Over - Press R to Restart or Q to Quit", True, HINT)
    final = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(go, (WIDTH // 8, HEIGHT // 2 - 20))
    screen.blit(final, (WIDTH // 2 - 60, HEIGHT // 2 + 10))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    waiting = False
                    return game_loop()

if __name__ == "__main__":
    game_loop()