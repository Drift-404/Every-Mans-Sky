import pygame, random, noise
class PlanetGenerator:
    def __init__(self, radius, planet_type):
        self.radius = radius
        self.planet_type = planet_type
        self.surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        self.seed = random.randint(0, 999999)

        self._generate_texture()

    def get_surface(self):
        return self.surface

    def _generate_texture(self):
        biome_palettes = {
            "Terran": {  
                "ocean": (30, 70, 180),
                "shore": (240, 220, 140),
                "grass": (40, 160, 40),
                "desert": (210, 180, 80),
                "rock": (110, 110, 110),
                "ice": (240, 250, 255)
            },
            "Desert": {
                "ocean": (160, 130, 60),
                "shore": (240, 200, 80),
                "grass": (200, 140, 40),
                "desert": (230, 200, 70),
                "rock": (170, 150, 100),
                "ice": (240, 240, 240)
            },
            "Ice": {
                "ocean": (160, 200, 255),
                "shore": (220, 230, 250),
                "grass": (200, 200, 255),
                "desert": (210, 220, 250),
                "rock": (210, 220, 240),
                "ice": (255, 255, 255)
            },
            "Volcanic": {
                "ocean": (30, 0, 0),
                "shore": (70, 10, 10),
                "grass": (140, 20, 20),
                "desert": (200, 40, 0),
                "rock": (60, 60, 60),
                "ice": (255, 240, 100)
            },
            "Alien": {
                "ocean": (140, 0, 200),
                "shore": (255, 100, 255),
                "grass": (0, 255, 200),
                "desert": (180, 0, 255),
                "rock": (100, 200, 255),
                "ice": (255, 255, 0)
            },
            "Gas": {       
                "ocean": (150, 200, 255),
                "shore": (200, 220, 255),
                "grass": (180, 180, 255),
                "desert": (160, 160, 255),
                "rock": (120, 120, 255),
                "ice": (255, 255, 255)
            }
        }

        palette = biome_palettes.get(self.planet_type, biome_palettes["Terran"])
        radius = self.radius

        import noise, math
        for y in range(-radius, radius):
            for x in range(-radius, radius):
                dist = math.sqrt(x*x + y*y)
                if dist > radius:
                    continue

                nx = (x / radius) * 2
                ny = (y / radius) * 2

                elevation = noise.pnoise2(
                    nx, ny,
                    octaves=5,
                    persistence=0.5,
                    lacunarity=2.0,
                    base=self.seed
                )

                if elevation < -0.05:
                    color = palette["ocean"]
                elif elevation < 0.02:
                    color = palette["shore"]
                elif elevation < 0.25:
                    color = palette["grass"]
                elif elevation < 0.45:
                    color = palette["desert"]
                elif elevation < 0.7:
                    color = palette["rock"]
                else:
                    color = palette["ice"]

                shade = (x + y) * 0.08
                shaded = (
                    max(0, min(color[0] - shade, 255)),
                    max(0, min(color[1] - shade, 255)),
                    max(0, min(color[2] - shade, 255))
                )
                self.surface.set_at((x + radius, y + radius), shaded)
