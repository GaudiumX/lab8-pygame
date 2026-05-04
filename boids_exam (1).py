import pygame
import random
import math
from typing import List, Tuple


class Config:
    WIDTH: int = 800
    HEIGHT: int = 600

    NUM_BOIDS: int = 200
    BOID_SIZE: int = 5
    BOID_SPEED_MIN: int = 200  # Pixels per second
    BOID_SPEED_MAX: int = 300  # Pixels per second

    # TODO: Use the following parameters to implement the three main boid behaviors: separation, alignment, and cohesion
    # Use the *_DISTANCE parameters in the _separation, _alignment, and _cohesion methods to determine which nearby boids to consider for each behavior.
    # Use the *_STEER_STRENGTH parameters when applying the steering forces in the update() method.
    # You may have to adjust these parameters to get good results, but they should be a good starting point for tuning the behaviors.

    # Separation is the behavior where boids steer away from nearby boids to avoid crowding
    SEPARATION_ON: bool = False  # Toggle separation behavior on/off
    SEPARATION_DISTANCE: int = BOID_SIZE * 15  # Minimum distance to maintain from other boids
    SEPARATION_STEER_STRENGTH: float = 5 # How strongly boids steer away from neighbors (vector-based)

    # Alignment is the behavior where boids steer toward the average direction of nearby boids
    ALIGNEMENT_ON: bool = False  # Toggle alignment behavior on/off
    ALIGNMENT_DISTANCE: int = BOID_SIZE * 100  # Distance within which to consider neighbors for alignment
    ALIGNEMENT_STEER_STRENGTH: float = .8  # How strongly boids steer toward average direction of neighbors (vector-based)

    # Cohesion is the behavior where boids steer toward the average position of nearby boids
    COHESION_ON: bool = False  # Toggle cohesion behavior on/off
    COHESION_DISTANCE: int = BOID_SIZE * 50  # Distance within which to consider neighbors for cohesion
    COHESION_STEER_STRENGTH: float = 5  # How strongly boids steer toward center of mass of neighbors (vector-based)

    # Wall warp or bounce
    WALL_BEHAVIOR: str = "bounce"  # "wrap" or "bounce"



config = Config()

# Main Boid class representing each boid in the simulation
class Boid:
    def __init__(self) -> None:
        self.x: float = random.randint(0, config.WIDTH)
        self.y: float = random.randint(0, config.HEIGHT)
        self.speed: float = random.uniform(config.BOID_SPEED_MIN, config.BOID_SPEED_MAX)
        angle: float = random.uniform(0, 2 * math.pi)
        self.vx: float = self.speed * math.cos(angle)
        self.vy: float = self.speed * math.sin(angle)


    # TODO: Implement speed clamping to ensure boids don't exceed max speed
    def _clampSpeed(self) -> None:
        pass

    # TODO: Implement Screen Wrapping
    # Screen wrapping: if a boid goes off one edge of the screen, 
    # it should reappear on the opposite edge
    def _screen_wrap(self) -> None:
        pass
    
    # Default wall behavior is bounce: if a boid hits the edge of the screen, 
    # it should bounce back in the opposite direction
    def _screen_bounce(self) -> None:
        if self.x < config.BOID_SIZE or self.x > config.WIDTH - config.BOID_SIZE:
            self.vx = -self.vx
            self.x = max(config.BOID_SIZE, min(self.x, config.WIDTH - config.BOID_SIZE))
        if self.y < config.BOID_SIZE or self.y > config.HEIGHT - config.BOID_SIZE:
            self.vy = -self.vy
            self.y = max(config.BOID_SIZE, min(self.y, config.HEIGHT - config.BOID_SIZE))

    # TODO: Implement Random Steering of the velocity vector to create more natural movement
    def _random_steer(self, spread: float = 0.2) -> None:
        # # Randomly steer a bit to create more natural movement
        pass


    # TODO: Implement the three main boid behaviors: separation, alignment, and cohesion

    # Separation: steer away from nearby boids to avoid crowding: 
    # _separation returns a vector pointing away from nearby boids
    # Explanation: For each nearby boid, calculate a vector pointing away from it, 
    # inversely proportional to the distance. 
    # Then sum these vectors to get the overall separation steering force.
    def _separation(self, boids: List['Boid']) -> pygame.Vector2:
        steer : pygame.Vector2 = pygame.Vector2(0, 0)
        return steer

    # Alignment: steer toward the average direction of nearby boids: 
    # _alignment returns a vector pointing in the average direction of nearby boids
    # Explanation: For each nearby boid, get its velocity vector and sum them up. 
    # Then divide by the number of nearby boids to get the average velocity, 
    # and subtract the current boid's velocity to get the alignment steering force.
    def _alignment(self, boids: List['Boid']) -> pygame.Vector2:
        steer : pygame.Vector2 = pygame.Vector2(0, 0)
        return steer
    
    # Cohesion: steer toward the average position of nearby boids: 
    # _cohesion returns a vector pointing toward the average position of nearby boids
    # Explanation: For each nearby boid, get its position and sum them up. 
    # Then divide by the number of nearby boids to get the average position, 
    # and subtract the current boid's position to get the cohesion steering force.
    def _cohesion(self, boids: List['Boid']) -> pygame.Vector2:
        steer : pygame.Vector2 = pygame.Vector2(0, 0)
        return steer
        

    # TODO: Use _random_steer, _separation, _alignment and _cohesion in update()
    def update(self, boids: List['Boid'], dt: int) -> None:
        # dt is in milliseconds, convert to seconds for physics calculations, when applying steering forces
        # and the speed which are in pixels per second
        dt_seconds: float = dt / 1000.0

        # TODO: Use _random_steer, _separation, _alignment and _cohesion in update()
        # Explanation: 
        # Use the _separation, _alignment, and _cohesion methods to calculate the steering forces based on nearby boids.
        # Use the flags in the Config class to determine which behaviors are active 
        # and apply the corresponding steering forces to the boid's velocity 
        # using the defined strengths (*_STEER_STRENGTH) for each behavior.

        self._random_steer()

        # Update the boid's position based on its velocity.
        self.x += self.vx * dt_seconds
        self.y += self.vy * dt_seconds

        # Last, handle wall behavior (bounce or wrap)
        if config.WALL_BEHAVIOR == "bounce":
            self._screen_bounce()
        else:   
            self._screen_wrap()


    # Draw boid as a triangle pointing in the direction of velocity
    def draw(self, screen: pygame.Surface) -> None:
        arrow_spread_angle: float = 2.5  # Radians between the two back points of the triangle
        angle: float = math.atan2(self.vy, self.vx)
        points: List[Tuple[float, float]] = [
            (self.x + math.cos(angle) * config.BOID_SIZE, self.y + math.sin(angle) * config.BOID_SIZE),
            (self.x + math.cos(angle + arrow_spread_angle) * config.BOID_SIZE, self.y + math.sin(angle + arrow_spread_angle) * config.BOID_SIZE),
            (self.x + math.cos(angle - arrow_spread_angle) * config.BOID_SIZE, self.y + math.sin(angle - arrow_spread_angle) * config.BOID_SIZE),
        ]
        pygame.draw.polygon(screen, (255, 255, 255), points)

# Draw HUD (Heads Up Display) with FPS and behavior statuses
def draw_hud(screen: pygame.Surface, font: pygame.font.Font, config: Config, fps: float) -> None:
    # Draw separation status and alignment and FPS on the screen
    text: str = f"FPS: {fps:.2f}   (Press 'ESC' or 'Q' to quit)"
    img: pygame.Surface = font.render(text, True, (255, 255, 255))
    screen.blit(img, (10, 10))
    text: str = f"Separation: {'ON' if config.SEPARATION_ON else 'OFF'} - Press 'S' to toggle"
    img = font.render(text, True, (255, 255, 255))
    screen.blit(img, (10, 25))
    text: str = f"Alignment: {'ON' if config.ALIGNEMENT_ON else 'OFF'} - Press 'A' to toggle"
    img = font.render(text, True, (255, 255, 255))
    screen.blit(img, (10, 40))
    text: str = f"Cohesion: {'ON' if config.COHESION_ON else 'OFF'} - Press 'C' to toggle"
    img = font.render(text, True, (255, 255, 255))
    screen.blit(img, (10, 55))
    text: str = f"Wall Behavior: {config.WALL_BEHAVIOR.capitalize()} - Press 'W' to toggle"
    img = font.render(text, True, (255, 255, 255))
    screen.blit(img, (10, 70))


# Main function to run the simulation
def run_simulation() -> None:

    # Initialize Pygame and create screen, clock, and font
    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
    clock: pygame.time.Clock = pygame.time.Clock()
    font: pygame.font.Font = pygame.font.SysFont(None, 18)

    # Create boids
    boids: List[Boid] = [Boid() for _ in range(Config.NUM_BOIDS)]
    
    # Main loop
    running: bool = True
    while running:
        dt: int = clock.tick(60)  # Elapsed time in milliseconds since last frame
        fps: float = clock.get_fps() # Current frames per second

        # Screen clearing
        screen.fill((0, 0, 0))

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False
                if event.key == pygame.K_s:
                    config.SEPARATION_ON = not config.SEPARATION_ON
                if event.key == pygame.K_a:
                    config.ALIGNEMENT_ON = not config.ALIGNEMENT_ON
                if event.key == pygame.K_c:
                    config.COHESION_ON = not config.COHESION_ON
                if event.key == pygame.K_w:
                    config.WALL_BEHAVIOR = "bounce" if config.WALL_BEHAVIOR == "wrap" else "wrap"

        # Update and draw boids in one loop
        for boid in boids:
            boid.update(boids, dt)
            boid.draw(screen)

        # Draw HUD (Heads Up Display) with FPS and behavior statuses
        draw_hud(screen, font, config, fps)
        pygame.display.flip()

    pygame.quit()

# Main entry point to run the simulation
if __name__ == "__main__":
    run_simulation()