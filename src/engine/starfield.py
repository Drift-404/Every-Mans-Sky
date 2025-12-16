import pygame
import random
import math


class Star:
    def __init__(self, width, height, depth):
        self.depth = depth  # 0 = near, 1 = far
        self.reset(width, height)

        # Size & brightness by depth
        self.size = max(1, int(3 * (1.2 - depth)))
        base = random.randint(180, 255)
        tint = random.randint(-10, 10)
        self.color = (
            min(255, base),
            min(255, base + tint),
            min(255, base + tint),
        )
        tint = random.randint(-20, 20)
        brightness = int(200 + 55 * (1 - depth))
        self.color = (
            min(255, brightness + tint),
            min(255, brightness + tint),
            min(255, brightness + tint),
)

    def reset(self, width, height):
        # Large spawn area prevents banding
        self.x = random.uniform(-width * 6, width * 6)
        self.y = random.uniform(-height * 6, height * 6)


class StarLayer:
    def __init__(self, width, height, count, depth, speed_scale):
        self.width = width
        self.height = height
        self.depth = depth
        self.speed_scale = speed_scale
        self.stars = [Star(width, height, depth) for _ in range(count)]

    def draw(self, screen, cam_x, cam_y, vel_x, vel_y):
        for star in self.stars:
            sx = star.x - cam_x * self.depth - vel_x * self.speed_scale
            sy = star.y - cam_y * self.depth - vel_y * self.speed_scale

            # wrap
            if sx < -50:
                star.x += self.width * 2
            elif sx > self.width + 50:
                star.x -= self.width * 2

            if sy < -50:
                star.y += self.height * 2
            elif sy > self.height + 50:
                star.y -= self.height * 2

            pygame.draw.circle(screen, star.color, (int(sx), int(sy)), star.size)



class StarField:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.layers = [
            StarLayer(width, height, count=1500, depth=0.95, speed_scale=0.15),
            StarLayer(width, height, count=1000, depth=0.7,  speed_scale=0.3),
            StarLayer(width, height, count=600,  depth=0.5,  speed_scale=0.5),
            StarLayer(width, height, count=350,  depth=0.3,  speed_scale=0.75),
            StarLayer(width, height, count=200,  depth=0.15, speed_scale=1.0),
        ]


    def draw(self, screen, cam_x, cam_y, vel_x=0, vel_y=0):
        for layer in self.layers:
            layer.draw(screen, cam_x, cam_y, vel_x, vel_y)


