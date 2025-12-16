import pygame
import sys
import os
import random
import math
from src.engine.starfield import StarField
from src.engine.planet import Planet
from src.engine.ship import Ship
from src.engine.api import get_random_planet, get_planet_info

# -----------------------------
# PLANET TYPE MAPPING
# -----------------------------
PLANET_TYPE_MAP = {
    "Rocky": "Rocky01",
    "Gas": "Gas01",
    "Terran": "Terran01",
    "Volcanic": "Volcanic01",
    "Ice": "Ice01"
}

# -----------------------------
# FETCH PLANET FROM API
# -----------------------------
api_planet = get_random_planet()
planet_info = get_planet_info(api_planet)
planet_type_folder = PLANET_TYPE_MAP.get(planet_info["type"], "Rocky01")
name = planet_info["name"]

# -----------------------------
# GAME SETUP
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pygame.init()
WIDTH, HEIGHT = 1024, 1024
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Everyman's Sky - Initial Release")
clock = pygame.time.Clock()

# -----------------------------
# NEBULA BACKGROUND
# -----------------------------
nebula_image = pygame.image.load(
    os.path.join(BASE_DIR, "assets", "starfield", "space", "Blue_Nebula_05-1024x1024.png")
).convert()
nebula_image = pygame.transform.scale(nebula_image, (WIDTH, HEIGHT))
nebula_surface = nebula_image

dark_overlay = pygame.Surface((WIDTH, HEIGHT))
dark_overlay.set_alpha(60)
dark_overlay.fill((0, 0, 20))

# -----------------------------
# SHIP
# -----------------------------
ship = Ship(
    os.path.join(BASE_DIR, "assets", "ship", "ship.png"),
    0, 0
)
starfield = StarField(WIDTH, HEIGHT)

# -----------------------------
# PLANETS
# -----------------------------
PLANETS_DIR = os.path.join(BASE_DIR, "assets", "planets")
planets = []
planet_types = [
    folder for folder in os.listdir(PLANETS_DIR)
    if os.path.isdir(os.path.join(PLANETS_DIR, folder))
]

prefixes = ["Astra", "Neo", "Vega", "Zar", "Cryo", "Lume", "Orion", "Sol", "Nexa"]
suffixes = ["-X", " Prime", " 7", "os", "ion", "ara", "is", "oth"]

def generate_name():
    return random.choice(prefixes) + random.choice(suffixes)

# --- Add API planet ---
display_radius = random.randint(30, 140)  # purely visual
api_planet_obj = Planet(0, 0, display_radius, planet_type_folder, name)
api_planet_obj.api_info = planet_info  # real API info
planets.append(api_planet_obj)

# --- Generate procedural planets ---
GALAXY_SIZE = 20000
NUM_PLANETS = 100
for i in range(NUM_PLANETS):
    px = random.randint(-GALAXY_SIZE, GALAXY_SIZE)
    py = random.randint(-GALAXY_SIZE, GALAXY_SIZE)
    size = random.randint(30, 140)
    planet_type = random.choice(planet_types)
    name = generate_name()
   
    planet = Planet(px, py, size, planet_type, name)
   
    # Add random stats for info panel
    planet.api_info = {
        "name": name,
        "radius": random.randint(1000, 15000),          # km
        "gravity": round(random.uniform(0.3, 3.0), 2), # g
        "orbital_period": random.randint(50, 1000),    # days
        "day_length": round(random.uniform(5, 50), 1)  # hours
    }
   
    planets.append(planet)

camera_x = camera_y = 0

# -----------------------------
# UI PANEL
# -----------------------------
font = pygame.font.SysFont("consolas", 20)
panel_width, panel_height = 350, 340
panel_rect = pygame.Rect(20, 20, panel_width, panel_height)
close_button_rect = pygame.Rect(panel_rect.right - 35, panel_rect.y + 5, 30, 30)
panel_open = False
panel_planet = None
panel_alpha = 0
panel_fade_speed = 15
panel_surface = pygame.Surface((panel_width, panel_height))
panel_surface.fill((50, 50, 50))
PREVIEW_HEIGHT = 90
PREVIEW_GAP = 12
BUTTON_GAP = 14
PREVIEW_MARGIN_TOP = 150
BUTTON_MARGIN_TOP = PREVIEW_MARGIN_TOP + PREVIEW_HEIGHT + 15



# -----------------------------
# RADAR
# -----------------------------
RADAR_SIZE = 200
RADAR_X = WIDTH - RADAR_SIZE - 20
RADAR_Y = HEIGHT - RADAR_SIZE - 20
RADAR_BG_COLOR = (30, 30, 30)
RADAR_BORDER_COLOR = (200, 200, 200)
RADAR_SHIP_COLOR = (0, 255, 0)
RADAR_PLANET_COLOR = (255, 0, 0)
RADAR_RANGE = 5000

# -----------------------------
# GAME STATE
# -----------------------------
running = True
game_state = "space"
current_planet = None
landing_start_time = 0
LANDING_DURATION = 2000
surface_panorama = None
surface_panorama_width = 0
surface_scroll_x = 0
surface_target_scroll_x = 0
camera_bob_phase = 0
parallax_mid = None
parallax_fg = None

# -----------------------------
# HELPERS
# -----------------------------
def init_surface_for_planet(planet):
    global surface_panorama, surface_panorama_width, surface_scroll_x, surface_target_scroll_x
    global parallax_mid, parallax_fg

    pano = pygame.image.load(planet.panorama_path).convert()
    pw, ph = pano.get_size()
    scale_factor = HEIGHT / ph
    pano = pygame.transform.smoothscale(pano, (int(pw * scale_factor), HEIGHT))

    surface_panorama = pano
    surface_panorama_width = pano.get_width()
    surface_scroll_x = surface_panorama_width // 2 - WIDTH // 2
    surface_target_scroll_x = surface_scroll_x

    parallax_mid = pygame.transform.smoothscale(pano, (surface_panorama_width // 2, HEIGHT))
    parallax_mid = pygame.transform.smoothscale(parallax_mid, (int(surface_panorama_width * 1.2), HEIGHT))
    parallax_fg = pygame.transform.smoothscale(pano, (int(surface_panorama_width * 1.4), HEIGHT))

def draw_surface_scene(dt_ms):
    global surface_scroll_x, surface_target_scroll_x, camera_bob_phase

    if surface_panorama is None:
        return

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        surface_target_scroll_x -= 6
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        surface_target_scroll_x += 6

    max_scroll = surface_panorama_width - WIDTH
    surface_target_scroll_x = max(0, min(surface_target_scroll_x, max_scroll))
    surface_scroll_x += (surface_target_scroll_x - surface_scroll_x) * 0.1

    camera_bob_phase += dt_ms * 0.003
    bob_offset = int(math.sin(camera_bob_phase) * 3)

    bg_x  = int(surface_scroll_x * 0.5)
    mid_x = int(surface_scroll_x * 0.8)
    fg_x  = int(surface_scroll_x * 1.1)

    screen.blit(surface_panorama, (0, bob_offset), (surface_scroll_x, 0, WIDTH, HEIGHT))
    screen.blit(parallax_mid, (0, bob_offset + 20), (mid_x, 0, WIDTH, HEIGHT))
    screen.blit(parallax_fg, (0, bob_offset + 40), (fg_x, 0, WIDTH, HEIGHT))

    fog = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for y in range(HEIGHT):
        alpha = int(70 * (y / HEIGHT))
        pygame.draw.line(fog, (0, 0, 0, alpha), (0, y), (WIDTH, y))
    screen.blit(fog, (0, 0))

def draw_panel():
    global panel_alpha

    if panel_open and panel_planet:
        if panel_alpha < 255:
            panel_alpha += panel_fade_speed
        panel_surface.set_alpha(panel_alpha)

        # Panel background
        screen.blit(panel_surface, panel_rect)
        pygame.draw.rect(screen, (200, 200, 200), panel_rect, 2)

        # ---------------- CLOSE BUTTON ----------------
        hover = close_button_rect.collidepoint(pygame.mouse.get_pos())
        color = (255, 80, 80) if hover else (200, 50, 50)
        pygame.draw.rect(screen, color, close_button_rect)
        screen.blit(
            font.render("X", True, (255, 255, 255)),
            (close_button_rect.x + 8, close_button_rect.y + 3)
        )

        # ---------------- PLANET INFO (API) ----------------
        info = getattr(panel_planet, "api_info", None)
        y_offset = panel_rect.y + 50
        line_gap = 28

        def draw_line(text):
            nonlocal y_offset
            screen.blit(
                font.render(text, True, (255, 255, 255)),
                (panel_rect.x + 15, y_offset)
            )
            y_offset += line_gap

        if info:
            draw_line(f"Name: {info.get('name','N/A')}")
            draw_line(f"Radius: {info.get('radius','N/A')} km")
            draw_line(f"Gravity: {info.get('gravity','N/A')}")
            draw_line(f"Orbital: {info.get('orbital_period','N/A')} days")
            draw_line(f"Day Length: {info.get('day_length','N/A')} hours")
        else:
            draw_line(f"Name: {panel_planet.name}")

        # ---------------- PREVIEW IMAGE ----------------
        if panel_planet.info_image:
            preview = pygame.transform.smoothscale(
                panel_planet.info_image,
                (panel_width - 30, PREVIEW_HEIGHT)
            )

            preview_x = panel_rect.x + 15
            preview_y = y_offset + PREVIEW_GAP

            # frame
            pygame.draw.rect(
                screen,
                (120, 120, 120),
                (preview_x - 2, preview_y - 2,
                 preview.get_width() + 4,
                 preview.get_height() + 4),
                2
            )

            screen.blit(preview, (preview_x, preview_y))

            y_offset = preview_y + PREVIEW_HEIGHT

        # ---------------- LAND BUTTON ----------------
        land_button_rect = pygame.Rect(
            panel_rect.x + 15,
            y_offset + BUTTON_GAP,
            120,
            30
        )

        pygame.draw.rect(screen, (80, 120, 255), land_button_rect)
        screen.blit(
            font.render("LAND", True, (255, 255, 255)),
            (land_button_rect.x + 30, land_button_rect.y + 5)
        )




# -----------------------------
# MAIN GAME LOOP
# -----------------------------
while running:
    dt_ms = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_state == "surface" and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            game_state = "space"
            surface_panorama = None
            current_planet = None
            continue

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if panel_open and panel_planet:
                land_button_rect = pygame.Rect(panel_rect.x + 15, panel_rect.y + panel_height - 40, 120, 30)
                if land_button_rect.collidepoint(event.pos):
                    current_planet = panel_planet
                    landing_start_time = pygame.time.get_ticks()
                    game_state = "landing_anim"
                    panel_open = False
                    continue
                if close_button_rect.collidepoint(event.pos):
                    panel_open = False
                    panel_planet = None
                    continue

            if game_state == "space":
                mouse_x, mouse_y = event.pos
                world_x = mouse_x + camera_x
                world_y = mouse_y + camera_y
                for p in planets:
                    dx = world_x - p.x
                    dy = world_y - p.y
                    if dx*dx + dy*dy <= p.radius*p.radius:
                        panel_planet = p
                        panel_open = True
                        panel_alpha = 0
                        break

    # -----------------------------
    # LANDING ANIMATION
    # -----------------------------
    if game_state == "landing_anim":
        for x in range(-1, 2):
            for y in range(-1, 2):
                screen.blit(nebula_surface, (x*WIDTH, y*HEIGHT))
        screen.blit(dark_overlay, (0, 0))

        now = pygame.time.get_ticks()
        t = (now - landing_start_time)/LANDING_DURATION
        if t > 1.0:
            if current_planet:
                init_surface_for_planet(current_planet)
            game_state = "surface"
            continue

        t_clamped = max(0.0, min(1.0, t))
        ease = t_clamped*t_clamped*(3-2*t_clamped)

        if current_planet:
            base_surface = current_planet.surface
            base_size = current_planet.radius*2
            target_size = int(base_size*6)
            current_size = int(base_size + (target_size-base_size)*ease)
            zoom_surf = pygame.transform.smoothscale(base_surface, (current_size, current_size))
            px = WIDTH//2 - current_size//2
            py = HEIGHT//2 - current_size//2
            screen.blit(zoom_surf, (px, py))

        if t_clamped > 0.6:
            flash_alpha = int(max(0.0, min(1.0, (t_clamped-0.6)/0.4))*255)
            flash_surf = pygame.Surface((WIDTH, HEIGHT))
            flash_surf.fill((255,255,255))
            flash_surf.set_alpha(flash_alpha)
            screen.blit(flash_surf, (0,0))

        pygame.display.flip()
        continue

    # -----------------------------
    # SURFACE MODE
    # -----------------------------
    if game_state == "surface":
        draw_surface_scene(dt_ms)
        pygame.display.flip()
        continue

    # -----------------------------
    # SPACE MODE
    # -----------------------------
    if game_state == "space":
        keys = pygame.key.get_pressed()
        ship.update(keys)
        if keys[pygame.K_LSHIFT]:
            ship.start_warp()

        ship_x, ship_y = ship.get_world_position()
        camera_x = ship_x - WIDTH//2
        camera_y = ship_y - HEIGHT//2

        parallax_x = (-camera_x*0.05) % WIDTH
        parallax_y = (-camera_y*0.05) % HEIGHT
        for x in range(-1, 2):
            for y in range(-1, 2):
                screen.blit(nebula_surface, (parallax_x+x*WIDTH, parallax_y+y*HEIGHT))
        screen.blit(dark_overlay, (0,0))


        starfield.draw(screen, camera_x, camera_y, ship.vel_x, ship.vel_y)



        mouse_pos = pygame.mouse.get_pos()
        for p in planets:
            if p.is_hovered(mouse_pos, camera_x, camera_y):
                pygame.draw.circle(screen, (255,255,0), (int(p.x-camera_x), int(p.y-camera_y)), p.radius+6, 2)
            p.draw(screen, camera_x, camera_y)

        ship.draw(screen, WIDTH, HEIGHT)
        draw_panel()

        # RADAR
        radar_rect = pygame.Rect(RADAR_X, RADAR_Y, RADAR_SIZE, RADAR_SIZE)
        pygame.draw.rect(screen, RADAR_BG_COLOR, radar_rect)
        pygame.draw.rect(screen, RADAR_BORDER_COLOR, radar_rect, 2)
        radar_center_x = RADAR_X + RADAR_SIZE//2
        radar_center_y = RADAR_Y + RADAR_SIZE//2
        for p in planets:
            dx = p.x - ship_x
            dy = p.y - ship_y
            if abs(dx) <= RADAR_RANGE and abs(dy) <= RADAR_RANGE:
                radar_dx = int((dx/RADAR_RANGE)*(RADAR_SIZE//2))
                radar_dy = int((dy/RADAR_RANGE)*(RADAR_SIZE//2))
                pygame.draw.circle(screen, RADAR_PLANET_COLOR, (radar_center_x+radar_dx, radar_center_y+radar_dy), 3)
        pygame.draw.circle(screen, RADAR_SHIP_COLOR, (radar_center_x, radar_center_y), 5)

        pygame.display.flip()
        continue

    clock.tick(60)


