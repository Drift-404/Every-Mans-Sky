import pygame, random

class StarField:
    def __init__(self, width, height, num_stars=200):
        self.width = width
        self.height = height

        # Parallax layers: far, mid, near
        self.layers = {
            1: [(random.randint(0, width), random.randint(0, height)) for _ in range(num_stars)],
            2: [(random.randint(0, width), random.randint(0, height)) for _ in range(num_stars // 2)],
            3: [(random.randint(0, width), random.randint(0, height)) for _ in range(num_stars // 4)]
        }

        self.speeds = {1: 0.1, 2: 0.3, 3: 1.0}  

    def update(self, vel_x, vel_y):
        for layer, stars in self.layers.items():
            speed = self.speeds[layer]
            for i, (x, y) in enumerate(stars):
                x -= vel_x * speed
                y -= vel_y * speed

                # Wrap around edges
                if x > self.width: x = 0
                if x < 0: x = self.width
                if y > self.height: y = 0
                if y < 0: y = self.height

                stars[i] = (x, y)

    def draw(self, screen):
        for layer, stars in self.layers.items():
            size = max(1, 4 - layer)  
            shade = 255 - (layer * 50)
            color = (shade, shade, 255)  

            for x, y in stars:
                pygame.draw.circle(screen, color, (int(x), int(y)), size)
