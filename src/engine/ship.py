import pygame
import math
from src.engine.warp import Warp


class Ship:
    def __init__(self, image_path, start_x=0, start_y=0, warp_image_path=None):
        # -----------------------
        # Position & movement
        # -----------------------
        self.x = float(start_x)
        self.y = float(start_y)
        self.vel_x = 0.0
        self.vel_y = 0.0

        # -----------------------
        # Rotation & physics
        # -----------------------
        self.angle = 0.0  # degrees (0 = facing right)
        self.rot_speed = 4
        self.accel = 0.3
        self.damping = 0.99
        self.max_speed = 12

        # -----------------------
        # Load ship sprite
        # -----------------------
        self.base_image = pygame.image.load(image_path).convert_alpha()
        self.base_image = pygame.transform.smoothscale(self.base_image, (48, 48))

        # Optional thrust flame
        self.thrust_image = None
        self.show_thrust = False

        # -----------------------
        # Warp system
        # -----------------------
        self.warp = Warp(self)

        self.warp_image = None
        if warp_image_path:
            self.warp_image = pygame.image.load(warp_image_path).convert_alpha()
            self.warp_image = pygame.transform.smoothscale(self.warp_image, (80, 80))

    # -------------------------------------------------
    def enable_thrust_flame(self, flame_path):
        self.thrust_image = pygame.image.load(flame_path).convert_alpha()

    # -------------------------------------------------
    def update(self, keys):
        # --- ROTATION ---
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle -= self.rot_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle += self.rot_speed

        # --- FORWARD THRUST ---
        thrusting = keys[pygame.K_UP] or keys[pygame.K_w]
        if thrusting:
            rad = math.radians(self.angle)
            self.vel_x += math.cos(rad) * self.accel
            self.vel_y += math.sin(rad) * self.accel
            self.show_thrust = True
        else:
            self.show_thrust = False

        # --- UPDATE WARP ---
        self.warp.update()

        # --- DAMPING ---
        self.vel_x *= self.damping
        self.vel_y *= self.damping

        # --- SPEED CAP (ignore while warping) ---
        speed = math.hypot(self.vel_x, self.vel_y)
        if not self.warp.warping and speed > self.max_speed:
            scale = self.max_speed / speed
            self.vel_x *= scale
            self.vel_y *= scale

        # --- UPDATE POSITION ---
        self.x += self.vel_x
        self.y += self.vel_y

    # -------------------------------------------------
    def start_warp(self):
        """Call this from main on KEYDOWN."""
        self.warp.start()

    # -------------------------------------------------
    def draw(self, screen, screen_width, screen_height):
        image = self.warp_image if (self.warp.warping and self.warp_image) else self.base_image

        rotated = pygame.transform.rotate(image, -(self.angle + 90))
        rect = rotated.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(rotated, rect)

        # Warp trail
        self.warp.draw(screen)

        # Thrust flame
        if self.show_thrust and self.thrust_image:
            flame = pygame.transform.rotate(self.thrust_image, -(self.angle + 90))
            flame_rect = flame.get_rect(center=rect.center)
            screen.blit(flame, flame_rect)

    # -------------------------------------------------
    def get_world_position(self):
        return self.x, self.y
