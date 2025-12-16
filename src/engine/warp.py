import pygame
import math
import time

class WarpTrailParticle:
    def __init__(self, pos):
        # pos is a pygame.Vector2
        self.pos = pos
        self.life = 15  # frames

    def update(self):
        self.life -= 1

    def draw(self, screen):
        # Simple cyan circle for trail
        pygame.draw.circle(screen, (0, 255, 255), (int(self.pos.x), int(self.pos.y)), max(1, self.life // 2))


class Warp:
    def __init__(self, ship):
        self.ship = ship
        self.warping = False
        self.warp_start_time = 0
        self.last_warp_time = -2  # initial cooldown done
        self.WARP_SPEED = 200
        self.WARP_DURATION = 5
        self.WARP_COOLDOWN = 2
        self.trail_particles = []

    def start(self):
        current_time = time.time()
        if current_time - self.last_warp_time >= self.WARP_COOLDOWN:
            self.warping = True
            self.warp_start_time = current_time
            self.last_warp_time = current_time

            # Compute velocity from ship's angle (no .direction)
            rad = math.radians(self.ship.angle)
            self.ship.vel_x = math.cos(rad) * self.WARP_SPEED
            self.ship.vel_y = math.sin(rad) * self.WARP_SPEED

    def update(self):
        current_time = time.time()
        if self.warping and current_time - self.warp_start_time >= self.WARP_DURATION:
            self.warping = False

        # Spawn trail particles while warping
        if self.warping:
            self.trail_particles.append(WarpTrailParticle(pygame.Vector2(self.ship.x, self.ship.y)))

        # Update trail particles
        for particle in self.trail_particles[:]:
            particle.update()
            if particle.life <= 0:
                self.trail_particles.remove(particle)

    def draw(self, screen):
        for particle in self.trail_particles:
            particle.draw(screen)
