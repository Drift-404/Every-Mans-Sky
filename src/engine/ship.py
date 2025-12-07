import pygame
import math

class Ship:
    def __init__(self, image_path, start_x=0, start_y=0):
        # Position & movement
        self.x = start_x
        self.y = start_y
        self.vel_x = 0
        self.vel_y = 0

        # Rotation & physics
        self.angle = 0  # degrees
        self.rot_speed = 4
        self.accel = 0.3
        self.damping = 0.99
        self.max_speed = 12

        # Load base sprite
        self.base_image = pygame.image.load(image_path).convert_alpha()
        self.base_image = pygame.transform.scale(self.base_image, (100, 100))
        self.thrust_image = None
        self.show_thrust = False

    def enable_thrust_flame(self, flame_path):
  
        self.thrust_image = pygame.image.load(flame_path).convert_alpha()

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

        self.vel_x *= self.damping
        self.vel_y *= self.damping

        # --- MAX SPEED CAP ---
        max_speed = 15
        speed = math.hypot(self.vel_x, self.vel_y)
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.vel_x *= scale
            self.vel_y *= scale

        # --- UPDATE POSITION ---
        self.x += self.vel_x
        self.y += self.vel_y

    def draw(self, screen, screen_width, screen_height):

        rotated = pygame.transform.rotate(self.base_image, -(self.angle+90))
        rect = rotated.get_rect(center=(screen_width // 2, screen_height // 2))

        screen.blit(rotated, rect)

        # if self.show_thrust and self.thrust_image:
        #     flame = pygame.transform.rotate(self.thrust_image, self.angle)
        #     flame_rect = flame.get_rect(center=(screen_width // 2, screen_height // 2))
        #     screen.blit(flame, flame_rect)

    def get_world_position(self):
        return self.x, self.y
