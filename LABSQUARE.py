"""
Moving Squares Simulation – Time‑Based with Mouse‑Toggleable Indicators

- Mixed squares: 5x25, 10x10, 30x4 (Exercise 1)
- Speed inversely proportional to size (time‑based)
- Jitter, fleeing, chasing, lifespan + rebirth
- Two clickable buttons (mouse) to toggle perception circle and velocity vector
- Velocity vector: fixed length, starts from circle edge, same colour as circle
- All original time‑based logic unchanged
"""

import math
import random
import sys
from typing import List, Dict, Any

import pygame

# ========== Constants (unchanged) ==========
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
NUM_SQUARES = 45                     # 5+10+30 (Exercise 1)
MIN_SIZE = 10
MAX_SIZE = 50
GLOBAL_MAX_SPEED = 75.0
JITTER_CHANCE_PER_SECOND = 0.5
JITTER_MAX_ANGLE_DEG = 15
FLEE_FORCE = 1.5
FLEE_DISTANCE = 50.0
CHASE_FORCE = 6
CHASE_DISTANCE = 75.0
LIFE_MIN_SEC = 15.0
LIFE_MAX_SEC = 30.0
BACKGROUND_COLOR = (20, 20, 30)

# Visual settings
CIRCLE_ALPHA = 80
INDICATOR_COLOR = (255, 255, 255)    # white for both circle and vector
VECTOR_FIXED_LENGTH = -40             # pixels, independent of square size
BUTTON_WIDTH = 180
BUTTON_HEIGHT = 30
BUTTON_MARGIN = 10

FPS = 60
MAX_DT = 0.1

# ========== Global Toggle States ==========
show_perception_circle = True
show_velocity_vector = True

# Button rectangles
button_circle = None
button_vector = None

# ========== Helper Functions (original, except create_square replaced) ==========

def create_square_with_fixed_size(size: int) -> Dict[str, Any]:
    """Create a square with a predefined size (other attributes random)."""
    max_speed = GLOBAL_MAX_SPEED * (MIN_SIZE / size)
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
    """Exercise 1: 5 squares of size 25, 10 of size 10, 30 of size 4."""
    squares = []
    for _ in range(5):
        squares.append(create_square_with_fixed_size(25))
    for _ in range(10):
        squares.append(create_square_with_fixed_size(10))
    for _ in range(30):
        squares.append(create_square_with_fixed_size(4))
    return squares

# ---------- update_square (unchanged, time‑based) ----------
def update_square(square: Dict[str, Any], dt: float, all_squares: List[Dict[str, Any]]) -> None:
    """Update square: age, jitter, flee, chase, position, wall bounce."""
    square["age"] += dt
    if square["age"] >= square["lifespan"]:
        square["dead"] = True
        return

    flee_x, flee_y = 0.0, 0.0
    chase_x, chase_y = 0.0, 0.0
    my_size = square["size"]

    for other in all_squares:
        if other is square:
            continue
        dx = square["x"] - other["x"]
        dy = square["y"] - other["y"]
        dist = math.hypot(dx, dy)
        if other["size"] > my_size and dist < FLEE_DISTANCE and dist > 0:
            strength = FLEE_FORCE * (1 - dist / FLEE_DISTANCE)
            flee_x += (dx / dist) * strength
            flee_y += (dy / dist) * strength
        if other["size"] < my_size and dist < CHASE_DISTANCE and dist > 0:
            strength = CHASE_FORCE * (1 - dist / CHASE_DISTANCE)
            chase_x += (-dx / dist) * strength
            chase_y += (-dy / dist) * strength

    if random.random() < JITTER_CHANCE_PER_SECOND * dt:
        angle = math.atan2(square["vy"], square["vx"])
        jitter_ang = math.radians(random.uniform(-JITTER_MAX_ANGLE_DEG, JITTER_MAX_ANGLE_DEG))
        new_angle = angle + jitter_ang
        speed = math.hypot(square["vx"], square["vy"])
        square["vx"] = math.cos(new_angle) * speed
        square["vy"] = math.sin(new_angle) * speed

    square["vx"] += (flee_x + chase_x) * dt
    square["vy"] += (flee_y + chase_y) * dt

    speed = math.hypot(square["vx"], square["vy"])
    max_sp = square["max_speed"]
    if speed > max_sp and speed > 0:
        square["vx"] = square["vx"] / speed * max_sp
        square["vy"] = square["vy"] / speed * max_sp

    new_x = square["x"] + square["vx"] * dt
    new_y = square["y"] + square["vy"] * dt

    size = square["size"]
    if new_x <= 0 or new_x + size >= SCREEN_WIDTH:
        square["vx"] *= -1
        new_x = max(0, min(new_x, SCREEN_WIDTH - size))
    if new_y <= 0 or new_y + size >= SCREEN_HEIGHT:
        square["vy"] *= -1
        new_y = max(0, min(new_y, SCREEN_HEIGHT - size))

    square["x"] = new_x
    square["y"] = new_y

# ---------- draw_square (modified: vector starts from circle edge, fixed length) ----------
def draw_square(screen: pygame.Surface, square: Dict[str, Any]) -> None:
    """Draw the square and optional indicators (circle + vector)."""
    rect = pygame.Rect(square["x"], square["y"], square["size"], square["size"])
    pygame.draw.rect(screen, square["color"], rect)

    center_x = square["x"] + square["size"] / 2
    center_y = square["y"] + square["size"] / 2
    perception_radius = int(max(FLEE_DISTANCE, CHASE_DISTANCE))

    # Perception circle (toggleable)
    if show_perception_circle:
        surf = pygame.Surface((perception_radius*2, perception_radius*2), pygame.SRCALPHA)
        color_with_alpha = (*INDICATOR_COLOR, CIRCLE_ALPHA)
        pygame.draw.circle(surf, color_with_alpha, (perception_radius, perception_radius), perception_radius, 1)
        screen.blit(surf, (center_x - perception_radius, center_y - perception_radius))

    # Velocity vector (toggleable) – starts from circle edge, fixed length, same colour
    if show_velocity_vector:
        vx, vy = square["vx"], square["vy"]
        speed = math.hypot(vx, vy)
        if speed > 0.01:
            dir_x = vx / speed
            dir_y = vy / speed
            start_x = center_x + dir_x * perception_radius
            start_y = center_y + dir_y * perception_radius
            end_x = start_x + dir_x * VECTOR_FIXED_LENGTH
            end_y = start_y + dir_y * VECTOR_FIXED_LENGTH
            pygame.draw.line(screen, INDICATOR_COLOR, (start_x, start_y), (end_x, end_y), 2)

# ---------- UI helpers (unchanted except added HUD) ----------
def draw_fps(screen: pygame.Surface, clock: pygame.time.Clock) -> None:
    font = pygame.font.SysFont(None, 24)
    fps_text = font.render(f"FPS: {clock.get_fps():.1f}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))

def init_buttons() -> None:
    global button_circle, button_vector
    x = SCREEN_WIDTH - BUTTON_WIDTH - BUTTON_MARGIN
    y = BUTTON_MARGIN
    button_circle = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)
    button_vector = pygame.Rect(x, y + BUTTON_HEIGHT + 5, BUTTON_WIDTH, BUTTON_HEIGHT)

def draw_buttons(screen: pygame.Surface) -> None:
    font = pygame.font.SysFont(None, 24)
    # Circle button
    color = (100, 200, 100) if show_perception_circle else (150, 150, 150)
    pygame.draw.rect(screen, color, button_circle)
    pygame.draw.rect(screen, (255,255,255), button_circle, 2)
    text = font.render(f"Circle: {'ON' if show_perception_circle else 'OFF'}", True, (0,0,0))
    screen.blit(text, (button_circle.x + 10, button_circle.y + 5))
    # Vector button
    color = (100, 200, 100) if show_velocity_vector else (150, 150, 150)
    pygame.draw.rect(screen, color, button_vector)
    pygame.draw.rect(screen, (255,255,255), button_vector, 2)
    text = font.render(f"Vector: {'ON' if show_velocity_vector else 'OFF'}", True, (0,0,0))
    screen.blit(text, (button_vector.x + 10, button_vector.y + 5))

# ---------- rebirth_dead_squares (adjusted for mixed sizes) ----------
def rebirth_dead_squares(squares: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Replace dead squares with new ones, preserving mixed size distribution."""
    new_squares = []
    for sq in squares:
        if sq["dead"]:
            # Approximate original distribution: 5/45=11% size25, 10/45=22% size10, 30/45=67% size4
            r = random.random()
            if r < 5/45:
                size_choice = 25
            elif r < (5+10)/45:
                size_choice = 10
            else:
                size_choice = 4
            new_squares.append(create_square_with_fixed_size(size_choice))
        else:
            new_squares.append(sq)
    return new_squares

# ========== Main Game Loop ==========
def main() -> None:
    global show_perception_circle, show_velocity_vector
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Moving Squares – Click buttons to toggle indicators")
    clock = pygame.time.Clock()
    init_buttons()

    squares = create_mixed_squares()      # Exercise 1
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        if dt > MAX_DT:
            dt = MAX_DT

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if button_circle.collidepoint(mouse_pos):
                    show_perception_circle = not show_perception_circle
                elif button_vector.collidepoint(mouse_pos):
                    show_velocity_vector = not show_velocity_vector

        # Update all squares (unchanged)
        for sq in squares:
            update_square(sq, dt, squares)

        # Rebirth dead squares (with mixed distribution)
        squares = rebirth_dead_squares(squares)

        # Draw
        screen.fill(BACKGROUND_COLOR)
        for sq in squares:
            draw_square(screen, sq)
        draw_fps(screen, clock)
        draw_buttons(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()