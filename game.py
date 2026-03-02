import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game with Obstacles (WASD)")

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
BLACK = (0, 0, 0)

# Clock and sizes
clock = pygame.time.Clock()
snake_size = 20
snake_speed = 10

# Fonts
font = pygame.font.SysFont("Arial", 20)

def draw_snake(snake_list):
    for x, y in snake_list:
        pygame.draw.rect(screen, GREEN, (x, y, snake_size, snake_size))

def message(text, color, x, y):
    msg = font.render(text, True, color)
    screen.blit(msg, (x, y))

def random_cell(exclude, width=WIDTH, height=HEIGHT):
    """Return a random cell (x,y) aligned to snake_size that is not in exclude set."""
    max_x = (width // snake_size) - 1
    max_y = (height // snake_size) - 1
    while True:
        rx = random.randint(0, max_x) * snake_size
        ry = random.randint(0, max_y) * snake_size
        if (rx, ry) not in exclude:
            return rx, ry

def game_loop():
    while True:
        # Game state
        x, y = WIDTH // 2, HEIGHT // 2
        dx, dy = 0, 0
        snake_list = [(x, y)]
        snake_length = 1
        score = 0

        # Create obstacles ensuring they don't overlap initial snake
        exclude = set(snake_list)
        obstacles = []
        for _ in range(10):
            ox, oy = random_cell(exclude)
            obstacles.append((ox, oy))
            exclude.add((ox, oy))

        # Place food not on snake or obstacles
        food_x, food_y = random_cell(exclude)
        exclude.add((food_x, food_y))

        game_over = False
        # track last direction to prevent immediate reverse
        last_dx, last_dy = 0, 0

        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    # WASD controls with prevention of immediate reverse
                    if event.key == pygame.K_w and not (last_dy == snake_size):
                        dx, dy = 0, -snake_size
                    elif event.key == pygame.K_s and not (last_dy == -snake_size):
                        dx, dy = 0, snake_size
                    elif event.key == pygame.K_a and not (last_dx == snake_size):
                        dx, dy = -snake_size, 0
                    elif event.key == pygame.K_d and not (last_dx == -snake_size):
                        dx, dy = snake_size, 0

            # Move snake
            x += dx
            y += dy

            # Update last direction only when moving
            if dx != 0 or dy != 0:
                last_dx, last_dy = dx, dy

            # Check boundaries
            if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
                game_over = True
                break

            # Update snake body (store tuples)
            snake_head = (x, y)
            snake_list.append(snake_head)
            if len(snake_list) > snake_length:
                del snake_list[0]

            # Collision with itself
            if snake_head in snake_list[:-1]:
                game_over = True
                break

            # Collision with obstacles (works because both are tuples)
            if snake_head in obstacles:
                game_over = True
                break

            # Eating food
            if snake_head == (food_x, food_y):
                score += 10
                snake_length += 1
                # place new food not on snake or obstacles
                exclude = set(snake_list) | set(obstacles)
                food_x, food_y = random_cell(exclude)

                # optional: add a new obstacle as difficulty increases
                if score % 50 == 0:
                    exclude.add((food_x, food_y))
                    new_ob = random_cell(exclude)
                    obstacles.append(new_ob)

            # Draw everything
            screen.fill(BLACK)
            draw_snake(snake_list)
            pygame.draw.rect(screen, RED, (food_x, food_y, snake_size, snake_size))
            for ox, oy in obstacles:
                pygame.draw.rect(screen, BLUE, (ox, oy, snake_size, snake_size))

            message(f"Score: {score}", WHITE, 10, 10)
            pygame.display.update()
            clock.tick(snake_speed)

        # Game over screen
        screen.fill(BLACK)
        message("Game Over! Press Q to Quit or R to Restart", RED, 50, HEIGHT // 2 - 10)
        message(f"Final Score: {score}", WHITE, 50, HEIGHT // 2 + 20)
        pygame.display.update()

        # Wait for restart or quit
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
                        # break to outer loop to restart game

if __name__ == "__main__":
    game_loop()