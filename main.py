import pygame
import sys
import os
import random
from src.engine.starfield import StarField
from src.engine.planet import Planet
from src.engine.ship import Ship


pygame.init()

# Screen Setup
WIDTH, HEIGHT = 1024, 1024
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Everyman's Sky - Pre-Alpha")

clock = pygame.time.Clock()

# -----------------------
# NEBULA BACKGROUND
# -----------------------
nebula_image = pygame.image.load(
    "/home/drift/workspace/everymanssky/assets/starfield/space/Blue_Nebula_05-1024x1024.png"
).convert()
nebula_image = pygame.transform.scale(nebula_image, (WIDTH, HEIGHT))
nebula_surface = nebula_image  
bg_width, bg_height = WIDTH, HEIGHT

dark_overlay = pygame.Surface((WIDTH, HEIGHT))
dark_overlay.set_alpha(60)   
dark_overlay.fill((0, 0, 20))

# Load Ship Sprite
ship = Ship("/home/drift/workspace/everymanssky/assets/ship/ship.png", 0, 0)

starfield = StarField(WIDTH, HEIGHT, num_stars=350)

# Create planets
planets = []
planet_types = [
    folder for folder in os.listdir("/home/drift/workspace/everymanssky/assets/planets/")
    if os.path.isdir(os.path.join("/home/drift/workspace/everymanssky/assets/planets/", folder))
]

prefixes = ["Astra", "Neo", "Vega", "Zar", "Cryo", "Lume", "Orion", "Sol", "Nexa"]
suffixes = ["-X", " Prime", " 7", "os", "ion", "ara", "is", "oth"]


def generate_name():
    return random.choice(prefixes) + random.choice(suffixes)


GALAXY_SIZE = 20000
NUM_PLANETS = 100

for i in range(NUM_PLANETS):
    px = random.randint(-GALAXY_SIZE, GALAXY_SIZE)
    py = random.randint(-GALAXY_SIZE, GALAXY_SIZE)
    size = random.randint(30, 140)
    planet_type = random.choice(planet_types)
    name = generate_name()
    planets.append(Planet(px, py, size, planet_type, name))

camera_x = camera_y = 0

# UI: Planet Info Panel
font = pygame.font.SysFont("consolas", 20)
panel_width, panel_height = 350, 250
panel_rect = pygame.Rect(20, 20, panel_width, panel_height)
close_button_rect = pygame.Rect(panel_rect.right - 35, panel_rect.y + 5, 30, 30)
panel_open = False
panel_planet = None

panel_alpha = 0
panel_fade_speed = 15
panel_surface = pygame.Surface((panel_width, panel_height))
panel_surface.fill((50, 50, 50))

# RADAR
RADAR_SIZE = 200
RADAR_X = WIDTH - RADAR_SIZE - 20
RADAR_Y = HEIGHT - RADAR_SIZE - 20
RADAR_BG_COLOR = (30, 30, 30)
RADAR_BORDER_COLOR = (200, 200, 200)
RADAR_SHIP_COLOR = (0, 255, 0)
RADAR_PLANET_COLOR = (255, 0, 0)
RADAR_RANGE = 5000

# GAME STATE
running = True
game_state = "space"          
current_planet = None

# Landing anim params
landing_start_time = 0
LANDING_DURATION = 2000  

# Surface mode assets
surface_panorama = None
surface_scroll = 0.0
surface_panorama = None
surface_panorama_width = 0
surface_scroll_x = 0  
surface_target_scroll_x = 0       
surface_scroll_x = 0              
camera_bob_phase = 0              





def init_surface_for_planet(planet):
    global surface_panorama, surface_panorama_width
    global surface_scroll_x, surface_target_scroll_x
    global parallax_mid, parallax_fg

    print("\n=== INIT SURFACE FOR PLANET ===")
    pano = pygame.image.load(planet.panorama_path).convert()
    print("Loaded size:", pano.get_size())


    pw, ph = pano.get_size()
    scale_factor = HEIGHT / ph
    pano = pygame.transform.smoothscale(pano, (int(pw * scale_factor), HEIGHT))

    surface_panorama = pano
    surface_panorama_width = pano.get_width()

    # Start centered
    surface_scroll_x = surface_panorama_width // 2 - WIDTH // 2
    surface_target_scroll_x = surface_scroll_x

    print("Scaled panorama:", surface_panorama.get_size())
    print(">>> SURFACE INIT DONE\n")


    parallax_mid = pygame.transform.smoothscale(pano, (surface_panorama_width // 2, HEIGHT))
    parallax_mid = pygame.transform.smoothscale(parallax_mid, (int(surface_panorama_width * 1.2), HEIGHT))

    parallax_fg = pygame.transform.smoothscale(pano, (int(surface_panorama_width * 1.4), HEIGHT))







import math

def draw_surface_scene(dt_ms):
    global surface_scroll_x, surface_target_scroll_x, camera_bob_phase

    if surface_panorama is None:
        return

    # -------------------------------
    # PLAYER CAMERA INPUT (target)
    # -------------------------------
    keys = pygame.key.get_pressed()

    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        surface_target_scroll_x -= 6
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        surface_target_scroll_x += 6

    # Clamp target scroll
    max_scroll = surface_panorama_width - WIDTH
    surface_target_scroll_x = max(0, min(surface_target_scroll_x, max_scroll))

    # -------------------------------
    # SMOOTH CAMERA MOVEMENT
    # -------------------------------
    surface_scroll_x += (surface_target_scroll_x - surface_scroll_x) * 0.1  

    # -------------------------------
    # CAMERA BOBBING 
    # -------------------------------
    camera_bob_phase += dt_ms * 0.003
    bob_offset = int(math.sin(camera_bob_phase) * 3)

    # -------------------------------
    # PARALLAX OFFSETS
    # -------------------------------
    bg_x  = int(surface_scroll_x * 0.5)   
    mid_x = int(surface_scroll_x * 0.8)   
    fg_x  = int(surface_scroll_x * 1.1)   

    # -------------------------------
    # DRAW LAYERS
    # -------------------------------
    # BACKGROUND SKY
    screen.blit(surface_panorama, (0, bob_offset), (surface_scroll_x, 0, WIDTH, HEIGHT))

    # MID LAYER
    screen.blit(parallax_mid, (0, bob_offset + 20), (mid_x, 0, WIDTH, HEIGHT))

    # FOREGROUND LAYER
    screen.blit(parallax_fg, (0, bob_offset + 40), (fg_x, 0, WIDTH, HEIGHT))

    # -------------------------------
    # ATMOSPHERIC FOG / GRADIENT
    # -------------------------------
    fog = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for y in range(HEIGHT):
        alpha = int(70 * (y / HEIGHT))  # fade stronger near bottom
        pygame.draw.line(fog, (0, 0, 0, alpha), (0, y), (WIDTH, y))

    screen.blit(fog, (0, 0))




while running:
    dt_ms = clock.tick(60)

    # -------------------------------
    # PROCESS EVENTS
    # -------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


        if game_state == "surface":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_state = "space"
                surface_panorama = None
                surface_layers = None
                current_planet = None
                continue


        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

        
            if panel_open and panel_planet:
                land_button_rect = pygame.Rect(
                    panel_rect.x + 15, panel_rect.y + 260, 120, 30
                )
                if land_button_rect.collidepoint(event.pos):
                    # Start landing animation
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
                    if dx * dx + dy * dy <= p.radius * p.radius:
                        panel_planet = p
                        panel_open = True
                        panel_alpha = 0
                        break

    # =========================================================
    # LANDING ANIMATION STATE
    # =========================================================
    if game_state == "landing_anim":

        parallax_x = 0
        parallax_y = 0
        for x in range(-1, 2):
            for y in range(-1, 2):
                screen.blit(
                    nebula_surface,
                    (int(parallax_x + x * WIDTH), int(parallax_y + y * HEIGHT)),
                )
        screen.blit(dark_overlay, (0, 0))


        now = pygame.time.get_ticks()
        t = (now - landing_start_time) / LANDING_DURATION
        if t > 1.0:
            # Init surface scene and move to surface state
            if current_planet is not None:
                init_surface_for_planet(current_planet)
            game_state = "surface"
            continue

        # Ease-in-out curve
        t_clamped = max(0.0, min(1.0, t))
        ease = t_clamped * t_clamped * (3 - 2 * t_clamped)  

        # Zoom planet sprite toward camera (center)
        if current_planet is not None:
            base_surface = current_planet.surface
            base_size = current_planet.radius * 2
            target_size = int(base_size * 6)  
            current_size = int(base_size + (target_size - base_size) * ease)

            zoom_surf = pygame.transform.smoothscale(
                base_surface, (current_size, current_size)
            )
            px = WIDTH // 2 - current_size // 2
            py = HEIGHT // 2 - current_size // 2
            screen.blit(zoom_surf, (px, py))

        # White flash near the end
        if t_clamped > 0.6:
            flash_strength = (t_clamped - 0.6) / 0.4  
            flash_strength = max(0.0, min(1.0, flash_strength))
            flash_alpha = int(flash_strength * 255)
            flash_surf = pygame.Surface((WIDTH, HEIGHT))
            flash_surf.fill((255, 255, 255))
            flash_surf.set_alpha(flash_alpha)
            screen.blit(flash_surf, (0, 0))

        pygame.display.flip()
        continue  

    # =========================================================
    # SURFACE MODE
    # =========================================================
    if game_state == "surface":

        draw_surface_scene(dt_ms)   

        pygame.display.flip()
        continue



    # =========================================================
    # SPACE MODE (DEFAULT)
    # =========================================================
    if game_state == "space":
    # MOVEMENT + CAMERA
        keys = pygame.key.get_pressed()
        ship.update(keys)

        ship_x, ship_y = ship.get_world_position()
        camera_x = ship_x - WIDTH // 2
        camera_y = ship_y - HEIGHT // 2


        # BACKGROUND PARALLAX (nebula)
        parallax_x = (-camera_x * 0.05) % WIDTH
        parallax_y = (-camera_y * 0.05) % HEIGHT

        for x in range(-1, 2):
            for y in range(-1, 2):
                screen.blit(
                    nebula_surface,
                    (int(parallax_x + x * WIDTH), int(parallax_y + y * HEIGHT)),
                )

        screen.blit(dark_overlay, (0, 0))

        # STARFIELD + PLANETS
        starfield.update(ship.vel_x, ship.vel_y)
        starfield.draw(screen)

        mouse_pos = pygame.mouse.get_pos()

        for p in planets:
            if p.is_hovered(mouse_pos, camera_x, camera_y):
                pygame.draw.circle(
                    screen,
                    (255, 255, 0),
                    (int(p.x - camera_x), int(p.y - camera_y)),
                    p.radius + 6,
                    2,
                )
            p.draw(screen, camera_x, camera_y)

        # PLAYER SHIP
        ship.draw(screen, WIDTH, HEIGHT)


        # UI PANEL
        if panel_open and panel_planet:
            if panel_alpha < 255:
                panel_alpha += panel_fade_speed
            panel_surface.set_alpha(panel_alpha)

            screen.blit(panel_surface, panel_rect)
            pygame.draw.rect(screen, (200, 200, 200), panel_rect, 2)

            # close button
            hover = close_button_rect.collidepoint(mouse_pos)
            color = (255, 80, 80) if hover else (200, 50, 50)
            pygame.draw.rect(screen, color, close_button_rect)
            screen.blit(
                font.render("X", True, (255, 255, 255)),
                (close_button_rect.x + 8, close_button_rect.y + 3),
            )

            # land button
            land_button_rect = pygame.Rect(panel_rect.x + 15, panel_rect.y + 260, 120, 30)
            pygame.draw.rect(screen, (80, 120, 255), land_button_rect)
            screen.blit(
                font.render("LAND", True, (255, 255, 255)),
                (land_button_rect.x + 20, land_button_rect.y + 5),
            )

            # text
            screen.blit(
                font.render(f"Name: {panel_planet.name}", True, (255, 255, 255)),
                (panel_rect.x + 15, panel_rect.y + 50),
            )

            screen.blit(
                font.render(f"Size: {panel_planet.radius * 2} km", True, (255, 255, 255)),
                (panel_rect.x + 15, panel_rect.y + 80),
            )

            screen.blit(
                font.render("System: Procedural Zone 1", True, (200, 200, 255)),
                (panel_rect.x + 15, panel_rect.y + 110),
            )

            # preview image from planet.info_image
            if panel_planet.info_image:
                preview = pygame.transform.scale(panel_planet.info_image, (320, 100))
                screen.blit(preview, (panel_rect.x + 15, panel_rect.y + 140))
        else:
            panel_alpha = 0

        # RADAR
        radar_rect = pygame.Rect(RADAR_X, RADAR_Y, RADAR_SIZE, RADAR_SIZE)
        pygame.draw.rect(screen, RADAR_BG_COLOR, radar_rect)
        pygame.draw.rect(screen, RADAR_BORDER_COLOR, radar_rect, 2)

        radar_center_x = RADAR_X + RADAR_SIZE // 2
        radar_center_y = RADAR_Y + RADAR_SIZE // 2

        for p in planets:
            dx = p.x - ship_x
            dy = p.y - ship_y

            if abs(dx) <= RADAR_RANGE and abs(dy) <= RADAR_RANGE:
                radar_dx = int((dx / RADAR_RANGE) * (RADAR_SIZE // 2))
                radar_dy = int((dy / RADAR_RANGE) * (RADAR_SIZE // 2))
                pygame.draw.circle(
                    screen,
                    RADAR_PLANET_COLOR,
                    (radar_center_x + radar_dx, radar_center_y + radar_dy),
                    3,
                )

        pygame.draw.circle(
            screen, RADAR_SHIP_COLOR, (radar_center_x, radar_center_y), 5
        )

        pygame.display.flip()
        continue
    clock.tick(60)