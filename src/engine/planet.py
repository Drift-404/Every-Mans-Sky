import pygame, os
from src.engine.planet_generator import PlanetGenerator


class Planet:
    def __init__(self, x, y, radius, planet_type, name):
        self.x = x
        self.y = y
        self.radius = radius
        self.name = name
        self.planet_type = planet_type

        # Planet asset folder
        folder = f"/home/drift/workspace/everymanssky/assets/planets/{planet_type}/"

        # ---------------------------------------------------
        # 1. ORBIT SPRITE 
        # ---------------------------------------------------
        orbit_path = self._find_file(folder, ["orbit", "albedo", "texture"])
        if orbit_path:
            img = pygame.image.load(orbit_path).convert_alpha()
            self.surface = pygame.transform.smoothscale(img, (radius * 2, radius * 2))
        else:
            # fallback procedural
            self.surface = PlanetGenerator(radius, planet_type).get_surface()

        # ---------------------------------------------------
        # 2. INFO PANEL IMAGE 
        # ---------------------------------------------------
        info_path = self._find_file(folder, ["info", "preview"])
        self.info_image = pygame.image.load(info_path).convert() if info_path else None

        # ---------------------------------------------------
        # 3. PANORAMA SKYBOX 
        # ---------------------------------------------------
        self.panorama_path = self._find_file(folder, ["panorama", "pano", "sky"])
        if not self.panorama_path:
            print(f"[WARNING] No panorama found for {planet_type}")

        # ---------------------------------------------------
        # 4. CUBEMAP FOR GROUND/PARALLAX
        # ---------------------------------------------------
        self.cubemap_path = self._find_file(folder, ["cube", "cubemap", "ground", "terrain"])
        if not self.cubemap_path:
            print(f"[WARNING] No cubemap found for {planet_type}")


    def _find_file(self, folder, keywords):
        """Return full path of first file containing any keyword (case-insensitive)."""
        if not os.path.isdir(folder):
            print("[ERROR] Folder missing:", folder)
            return None

        files = os.listdir(folder)
        print("[DEBUG] Files in", folder, "=", files)

        for f in files:
            lower = f.lower()
            for key in keywords:
                if key in lower:
                    print("[DEBUG] Matched", key, "->", f)
                    return os.path.join(folder, f)

        print("[WARNING] No match for", keywords, "in", folder)
        return None


    def draw(self, screen, cam_x, cam_y):
        screen.blit(
            self.surface,
            (self.x - cam_x - self.radius, self.y - cam_y - self.radius)
        )

    def is_hovered(self, mouse_pos, camera_x, camera_y):
        mx, my = mouse_pos
        dx = (self.x - camera_x) - mx
        dy = (self.y - camera_y) - my
        return (dx*dx + dy*dy) < (self.radius + 5)**2
