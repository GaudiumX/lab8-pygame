import math
import random
import sys
from collections import deque
from typing import List, Dict, Any

import pygame


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
NUM_SQUARES = 45
MIN_SIZE = 10
MAX_SIZE = 50
GLOBAL_MAX_SPEED = 100.0
JITTER_CHANCE_PER_SECOND = 0.5
JITTER_MAX_ANGLE_DEG = 15
FLEE_FORCE = 7
FLEE_DISTANCE = 50.0
CHASE_FORCE = 20
CHASE_DISTANCE = 75.0
LIFE_MIN_SEC = 15.0
LIFE_MAX_SEC = 30.0
BACKGROUND_COLOR = (20, 20, 30)


CIRCLE_ALPHA = 80
INDICATOR_COLOR = (255, 255, 255)
VECTOR_FIXED_LENGTH = -40
BUTTON_WIDTH = 180
BUTTON_HEIGHT = 30
BUTTON_MARGIN = 10

# Exercise 7: Trails
TRAILS_LENGTH = 60
TRAIL_COLOR = (200, 200, 200)

# Exercises 6 & 9: Growth
GROWTH_FACTOR = 0.5
MAX_GROWTH_SIZE = 80
GROWTH_DURATION = 0.5

FPS = 60
MAX_DT = 0.1

show_perception_circle = True
show_velocity_vector = True

button_circle = None
button_vector = None




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
        "dead": False,
        # EXERCISE 2: store birth size (never changes) ===
        "birth_size": size,
        # Exercise 7: trail
        "trail": deque(maxlen=TRAILS_LENGTH),
        # Exercise 9: animated growth attributes
        "is_growing": False,
        "original_size": size,
        "target_size": size,
        "grow_start_time": 0.0
    }


def create_mixed_squares() -> List[Dict[str, Any]]:
    # EXERCISE 1: 5 squares of size 25, 10 of size 10, 30 of size 4 ===
    squares = []
    for _ in range(5):
        squares.append(create_square_with_fixed_size(25))
    for _ in range(10):
        squares.append(create_square_with_fixed_size(10))
    for _ in range(30):
        squares.append(create_square_with_fixed_size(4))
    return squares


# EXERCISE 3: Screen wrapping 
def _screen_wrap(square: Dict[str, Any]) -> None:
    size = square["size"]
    if square["x"] + size < 0:
        square["x"] = SCREEN_WIDTH
    elif square["x"] > SCREEN_WIDTH:
        square["x"] = -size
    if square["y"] + size < 0:
        square["y"] = SCREEN_HEIGHT
    elif square["y"] > SCREEN_HEIGHT:
        square["y"] = -size


# EXERCISE 4: Collision detection
def check_collision(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    rect_a = pygame.Rect(a["x"], a["y"], a["size"], a["size"])
    rect_b = pygame.Rect(b["x"], b["y"], b["size"], b["size"])
    return rect_a.colliderect(rect_b)


def update_square(square: Dict[str, Any], dt: float, all_squares: List[Dict[str, Any]]) -> None:
    """Update square: age, jitter, flee, chase, position, wrap."""
    # Age and death
    square["age"] += dt
    if square["age"] >= square["lifespan"]:
        square["dead"] = True
        return

    # Exercise 9: Animated growth
    if square["is_growing"]:
        now = pygame.time.get_ticks() / 1000.0
        elapsed = now - square["grow_start_time"]
        if elapsed >= GROWTH_DURATION:
            square["size"] = square["target_size"]
            square["is_growing"] = False
            square["max_speed"] = GLOBAL_MAX_SPEED * (MIN_SIZE / square["size"])
        else:
            t = elapsed / GROWTH_DURATION
            new_size = int(square["original_size"] + (square["target_size"] - square["original_size"]) * t)
            square["size"] = new_size
            square["max_speed"] = GLOBAL_MAX_SPEED * (MIN_SIZE / square["size"])

    # Flee & chase
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

    # Jitter
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

    # Position
    square["x"] += square["vx"] * dt
    square["y"] += square["vy"] * dt

    # Screen wrapping (Exercise 3)
    _screen_wrap(square)

    # Trail update
    center = (square["x"] + square["size"] / 2, square["y"] + square["size"] / 2)
    square["trail"].append(center)


def draw_square(screen: pygame.Surface, square: Dict[str, Any]) -> None:
    # 1. Draw the square itself
    rect = pygame.Rect(square["x"], square["y"], square["size"], square["size"])
    pygame.draw.rect(screen, square["color"], rect)

    # 2. Draw trail on top (for all squares)
    trail = square["trail"]
    if len(trail) >= 2:
        for i in range(1, len(trail)):
            p1 = trail[i-1]
            p2 = trail[i]
            
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            dist = math.hypot(dx, dy)
            
            if dist > max(SCREEN_WIDTH, SCREEN_HEIGHT) / 2:
                continue
            pygame.draw.line(screen, TRAIL_COLOR, p1, p2, 2)

    
    center_x = square["x"] + square["size"] / 2
    center_y = square["y"] + square["size"] / 2
    perception_radius = int(max(FLEE_DISTANCE, CHASE_DISTANCE))

    if show_perception_circle:
        surf = pygame.Surface((perception_radius*2, perception_radius*2), pygame.SRCALPHA)
        color_with_alpha = (*INDICATOR_COLOR, CIRCLE_ALPHA)
        pygame.draw.circle(surf, color_with_alpha, (perception_radius, perception_radius), perception_radius, 1)
        screen.blit(surf, (center_x - perception_radius, center_y - perception_radius))

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
    
    color = (100, 200, 100) if show_perception_circle else (150, 150, 150)
    pygame.draw.rect(screen, color, button_circle)
    pygame.draw.rect(screen, (255, 255, 255), button_circle, 2)
    text = font.render(f"Circle: {'ON' if show_perception_circle else 'OFF'}", True, (0, 0, 0))
    screen.blit(text, (button_circle.x + 10, button_circle.y + 5))
    
    color = (100, 200, 100) if show_velocity_vector else (150, 150, 150)
    pygame.draw.rect(screen, color, button_vector)
    pygame.draw.rect(screen, (255, 255, 255), button_vector, 2)
    text = font.render(f"Vector: {'ON' if show_velocity_vector else 'OFF'}", True, (0, 0, 0))
    screen.blit(text, (button_vector.x + 10, button_vector.y + 5))


# EXERCISE 2: Same Size Respawn 
def rebirth_dead_squares(squares: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Replace dead squares with new ones, preserving original birth size."""
    new_squares = []
    for sq in squares:
        if sq["dead"]:
            # Respawn using the stored birth_size (never changed by eating)
            birth_size = sq["birth_size"]
            new_squares.append(create_square_with_fixed_size(birth_size))
        else:
            new_squares.append(sq)
    return new_squares


def main() -> None:
    global show_perception_circle, show_velocity_vector
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Moving Squares – Exam (All Exercises)")
    clock = pygame.time.Clock()
    init_buttons()

    squares = create_mixed_squares()
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

        # Update squares
        for sq in squares:
            update_square(sq, dt, squares)

        # EXERCISES 5 & 6 & 9: Eating, growth, animated growth
        for i, predator in enumerate(squares):
            if predator["dead"]:
                continue
            for j, prey in enumerate(squares):
                if i == j or prey["dead"]:
                    continue
                if predator["size"] > prey["size"] and check_collision(predator, prey):
                    prey["dead"] = True
                    # Exercise 6: grow proportionally
                    growth = int(prey["size"] * GROWTH_FACTOR)
                    new_target = predator["size"] + growth
                    if new_target > MAX_GROWTH_SIZE:
                        new_target = MAX_GROWTH_SIZE
                    # Exercise 9: animated growth
                    predator["is_growing"] = True
                    predator["original_size"] = predator["size"]
                    predator["target_size"] = new_target
                    predator["grow_start_time"] = pygame.time.get_ticks() / 1000.0

        # Rebirth dead squares (Exercise 2: same size respawn)
        squares = rebirth_dead_squares(squares)

        
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