"""
Moving Squares Simulation – Time‑Based with Visual Indicators

- 100 squares with random sizes
- Speed inversely proportional to size (time‑based)
- Jitter: random direction changes over time
- Fleeing: smaller squares run from larger ones
- Chasing: larger squares chase smaller ones
- Life span: each square lives 30‑180 seconds, then respawns
- Visual: circle shows perception range; line shows velocity vector
- Movement is time‑based (frame‑rate independent)
"""

import math
import random
import sys
from typing import List, Dict, Any

import pygame

# ========== Constants ==========
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
NUM_SQUARES = 100
MIN_SIZE = 10
MAX_SIZE = 50
GLOBAL_MAX_SPEED = 200.0          # pixels per second
JITTER_CHANCE_PER_SECOND = 0.5    # 50% chance per second
JITTER_MAX_ANGLE_DEG = 15         # degrees
FLEE_FORCE = 1.5
FLEE_DISTANCE = 150.0
CHASE_FORCE = 1.2
CHASE_DISTANCE = 200.0
LIFE_MIN_SEC = 30.0
LIFE_MAX_SEC = 180.0
BACKGROUND_COLOR = (20, 20, 30)

# Visual indicator settings
SHOW_PERCEPTION_CIRCLE = True      # show flee/chase detection range
SHOW_VELOCITY_VECTOR = True         # show line indicating movement direction
CIRCLE_ALPHA = 80                   # transparency of the circle (0‑255)
VECTOR_COLOR = (255, 255, 0)        # yellow line for velocity

FPS = 60

# ========== Helper Functions ==========

def create_square() -> Dict[str, Any]:
    """Create a new square with random properties."""
    size = random.randint(MIN_SIZE, MAX_SIZE)
    # Max speed: smaller = faster
    max_speed = GLOBAL_MAX_SPEED * (MIN_SIZE / size)
    # Random direction (angle in radians)
    angle = random.uniform(0, 2 * math.pi)
    # Start with half max speed to avoid too rapid movement
    vx = math.cos(angle) * max_speed * 0.5
    vy = math.sin(angle) * max_speed * 0.5
    x = random.uniform(0, SCREEN_WIDTH - size)
    y = random.uniform(0, SCREEN_HEIGHT - size)
    color = (random.randint(80, 255), random.randint(80, 255), random.randint(80, 255))
    lifespan = random.uniform(LIFE_MIN_SEC, LIFE_MAX_SEC)
    return {
        "x": x, "y": y, "size": size,
        "vx": vx, "vy": vy,
        "max_speed": max_speed,
        "color": color,
        "age": 0.0,
        "lifespan": lifespan,
        "dead": False
    }

def create_square_with_fixed_size(size: int) -> Dict[str, Any]:
    """Create a square with a predefined size (other attributes random)."""
    # Max speed: smaller = faster
    max_speed = GLOBAL_MAX_SPEED * (MIN_SIZE / size)   # MIN_SIZE is 10
    # Random direction (angle in radians)
    angle = random.uniform(0, 2 * math.pi)
    vx = math.cos(angle) * max_speed * 0.5
    vy = math.sin(angle) * max_speed * 0.5
    x = random.uniform(0, SCREEN_WIDTH - size)
    y = random.uniform(0, SCREEN_HEIGHT - size)
    color = (random.randint(80, 255), random.randint(80, 255), random.randint(80, 255))
    lifespan = random.uniform(LIFE_MIN_SEC, LIFE_MAX_SEC)
    return {
        "x": x, "y": y, "size": size,
        "vx": vx, "vy": vy,
        "max_speed": max_speed,
        "color": color,
        "age": 0.0,
        "lifespan": lifespan,
        "dead": False
    }

def create_mixed_squares() -> List[Dict[str, Any]]:
    squares = []
    # 5 squares of size 25
    for _ in range(5):
        sq = create_square_with_fixed_size(25)
        squares.append(sq)
    # 10 squares of size 10
    for _ in range(10):
        sq = create_square_with_fixed_size(10)
        squares.append(sq)
    # 30 squares of size 4
    for _ in range(30):
        sq = create_square_with_fixed_size(4)
        squares.append(sq)
    return squares

def update_square(square: Dict[str, Any], dt: float, all_squares: List[Dict[str, Any]]) -> None:
    """
    Update square: age, jitter, flee, chase, position, wall bounce.
    dt = time elapsed since last frame (seconds).
    """
    # Age and death
    square["age"] += dt
    if square["age"] >= square["lifespan"]:
        square["dead"] = True
        return

    # Collect flee and chase influences
    flee_x, flee_y = 0.0, 0.0
    chase_x, chase_y = 0.0, 0.0
    my_size = square["size"]

    for other in all_squares:
        if other is square:
            continue
        dx = square["x"] - other["x"]
        dy = square["y"] - other["y"]
        dist = math.hypot(dx, dy)
        # Flee from larger squares
        if other["size"] > my_size and dist < FLEE_DISTANCE and dist > 0:
            strength = FLEE_FORCE * (1 - dist / FLEE_DISTANCE)
            flee_x += (dx / dist) * strength
            flee_y += (dy / dist) * strength
        # Chase smaller squares
        if other["size"] < my_size and dist < CHASE_DISTANCE and dist > 0:
            strength = CHASE_FORCE * (1 - dist / CHASE_DISTANCE)
            # Chase vector points TOWARD the smaller square
            chase_x += (-dx / dist) * strength
            chase_y += (-dy / dist) * strength

    # Jitter (random direction change)
    if random.random() < JITTER_CHANCE_PER_SECOND * dt:
        angle = math.atan2(square["vy"], square["vx"])
        jitter_ang = math.radians(random.uniform(-JITTER_MAX_ANGLE_DEG, JITTER_MAX_ANGLE_DEG))
        new_angle = angle + jitter_ang
        speed = math.hypot(square["vx"], square["vy"])
        square["vx"] = math.cos(new_angle) * speed
        square["vy"] = math.sin(new_angle) * speed

    # Apply flee and chase forces to velocity (time‑based)
    square["vx"] += (flee_x + chase_x) * dt
    square["vy"] += (flee_y + chase_y) * dt

    # Clamp speed to max_speed
    speed = math.hypot(square["vx"], square["vy"])
    max_sp = square["max_speed"]
    if speed > max_sp and speed > 0:
        square["vx"] = square["vx"] / speed * max_sp
        square["vy"] = square["vy"] / speed * max_sp

    # Update position (time‑based)
    new_x = square["x"] + square["vx"] * dt
    new_y = square["y"] + square["vy"] * dt

    # Wall bounce with look‑ahead (prevents sticking outside)
    size = square["size"]
    if new_x <= 0 or new_x + size >= SCREEN_WIDTH:
        square["vx"] *= -1
        new_x = max(0, min(new_x, SCREEN_WIDTH - size))
    if new_y <= 0 or new_y + size >= SCREEN_HEIGHT:
        square["vy"] *= -1
        new_y = max(0, min(new_y, SCREEN_HEIGHT - size))

    square["x"] = new_x
    square["y"] = new_y


def draw_square(screen: pygame.Surface, square: Dict[str, Any]) -> None:
    """Draw a single square (filled rect)."""
    rect = pygame.Rect(square["x"], square["y"], square["size"], square["size"])
    pygame.draw.rect(screen, square["color"], rect)

    # Optional: draw velocity vector line
    if SHOW_VELOCITY_VECTOR:
        start = (square["x"] + square["size"]/2, square["y"] + square["size"]/2)
        # Scale vector so it's visible; use a fixed length cap
        speed = math.hypot(square["vx"], square["vy"])
        if speed > 0.1:
            scale = min(30.0, speed * 0.15)   # line length clamped
            dx = square["vx"] / speed * scale
            dy = square["vy"] / speed * scale
            end = (start[0] + dx, start[1] + dy)
            pygame.draw.line(screen, VECTOR_COLOR, start, end, 2)

    # Optional: draw perception range circle (for fleeing/chasing)
    if SHOW_PERCEPTION_CIRCLE:
        # Use the maximum of flee and chase distance for visualisation
        radius = int(max(FLEE_DISTANCE, CHASE_DISTANCE))
        center = (int(square["x"] + square["size"]/2), int(square["y"] + square["size"]/2))
        # Create a transparent surface for the circle
        surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        color_with_alpha = (255, 255, 255, CIRCLE_ALPHA)
        pygame.draw.circle(surf, color_with_alpha, (radius, radius), radius, 1)  # just outline
        screen.blit(surf, (center[0]-radius, center[1]-radius))


def draw_fps(screen: pygame.Surface, clock: pygame.time.Clock) -> None:
    """Display current FPS in top‑left corner."""
    font = pygame.font.SysFont(None, 24)
    fps_text = font.render(f"FPS: {clock.get_fps():.1f}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))


def rebirth_dead_squares(squares: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Replace dead squares with brand new ones.
    Returns a new list (safe iteration, no mutation during loop).
    """
    new_squares = []
    for sq in squares:
        if sq["dead"]:
            new_squares.append(create_square())
        else:
            new_squares.append(sq)
    return new_squares


# ========== Main Game Loop ==========
def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Moving Squares – Time‑Based with Vectors & Range Circles")
    clock = pygame.time.Clock()

    squares = create_mixed_squares()
    running = True

    while running:
        # dt in seconds, with a safety cap to avoid huge jumps on lag
        dt = clock.tick(FPS) / 1000.0
        if dt > 0.1:
            dt = 0.1

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    show_perception_circle = not show_perception_circle
                if event.key == pygame.K_v:
                    show_velocity_vector = not show_velocity_vector

        # Update all squares (flee & chase depend on all squares)
        for sq in squares:
            update_square(sq, dt, squares)

        # Rebirth dead squares (safe list replacement)
        squares = rebirth_dead_squares(squares)

        # Draw everything
        screen.fill(BACKGROUND_COLOR)
        for sq in squares:
            draw_square(screen, sq)
        draw_fps(screen, clock)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()