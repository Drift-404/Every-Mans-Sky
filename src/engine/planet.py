import pygame
import os
from src.engine.planet_generator import PlanetGenerator

# Resolve project root safely (works on any machine)
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

class Planet:
    def __init__(self, x, y, radius, planet_type, name):
        self.x = x
        self.y = y
        self.radius = radius
        self.name = name
        self.planet_type = planet_type

        # Planet asset folder (portable)
        folder = os.path.join(BASE_DIR, "assets", "planets", planet_type)

        # ---------------------------------------------------
        # 1. ORBIT SPRITE (space view)
        # ---------------------------------------------------
        orbit_path = self._find_file(folder, ["orbit", "albedo", "texture"])
        if orbit_path:
            img = pygame.image.load(orbit_path).convert_alpha()
            img.set_colorkey((0, 0, 0))  # safe: removes black bg if present
            self.surface = pygame.transform.smoothscale(
                img, (radius * 2, radius * 2)
            )
        else:
            # Procedural fallback
            self.surface = PlanetGenerator(radius, planet_type).get_surface()

        # ---------------------------------------------------
        # 2. INFO PANEL IMAGE
        # ---------------------------------------------------
        info_path = self._find_file(folder, ["info", "preview"])
        self.info_image = (
            pygame.image.load(info_path).convert_alpha()
            if info_path else None
        )

        # ---------------------------------------------------
        # 3. PANORAMA SKY (surface mode)
        # ---------------------------------------------------
        self.panorama_path = self._find_file(folder, ["panorama", "pano", "sky"])
        if not self.panorama_path:
            print(f"[WARNING] No panorama found for {planet_type}")

        # ---------------------------------------------------
        # 4. CUBEMAP / TERRAIN SOURCE
        # ---------------------------------------------------
        self.cubemap_path = self._find_file(
            folder, ["cube", "cubemap", "ground", "terrain"]
        )
        if not self.cubemap_path:
            print(f"[WARNING] No cubemap found for {planet_type}")

    def _find_file(self, folder, keywords):
        """Return full path of first file containing any keyword."""
        if not os.path.isdir(folder):
            print("[ERROR] Folder missing:", folder)
            return None

        files = os.listdir(folder)

        for f in files:
            lower = f.lower()
            for key in keywords:
                if key in lower:
                    return os.path.join(folder, f)

        return None

    def draw(self, screen, cam_x, cam_y):
        """Draw planet centered at world position."""
        screen.blit(
            self.surface,
            (self.x - cam_x - self.radius, self.y - cam_y - self.radius)
        )

    def is_hovered(self, mouse_pos, camera_x, camera_y):
        """Circular hover detection."""
        mx, my = mouse_pos
        dx = (self.x - camera_x) - mx
        dy = (self.y - camera_y) - my
        return (dx * dx + dy * dy) < (self.radius + 5) ** 2
