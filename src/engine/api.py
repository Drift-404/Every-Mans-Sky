import requests
import random

import os, json
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_FILE = os.path.join(BASE_DIR, "..", "data", "planets.json")
API_KEY = "d21b9f5f-c857-4916-b744-1fc12f614372"  # from the API signup

API_URL = "https://api.le-systeme-solaire.net/rest/bodies/"

TYPE_MAPPING = {
    "Mercury": "Rocky",
    "Venus": "Volcanic",
    "Earth": "Terran",
    "Mars": "Rocky",
    "Jupiter": "Gas",
    "Saturn": "Gas",
    "Uranus": "Gas",
    "Neptune": "Gas",
    "Pluto": "Ice"
}

def fetch_bodies():
    headers = { "Authorization":f"Bearer {API_KEY}"}
   
    """Fetch all bodies from the API, with caching."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
   
    resp = requests.get(API_URL, headers = headers,timeout=10)
    resp.raise_for_status()
    data = resp.json()["bodies"]
   
    # Save cache
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)
   
    return data

def get_random_planet():
    """Return a random planet from the API."""
    bodies = fetch_bodies()
    planets = [b for b in bodies if b.get("isPlanet")]
    return random.choice(planets)

def map_type(api_planet):
    """Map the real planet name to your game's planet type."""
    name = api_planet.get("englishName", api_planet.get("id", "Unknown"))
    return TYPE_MAPPING.get(name, "Terran")

def get_planet_info(api_planet):
    """Return a dict of planet info to display in game."""
    return {
        "name": api_planet.get("englishName", api_planet.get("id", "Unknown")),
        "radius": api_planet.get("meanRadius"),
        "gravity": api_planet.get("gravity"),
        "orbital_period": api_planet.get("sideralOrbit"),
        "day_length": api_planet.get("sideralRotation"),
        "type": map_type(api_planet),
        "atmosphere": api_planet.get("atmosphereComposition", "N/A")
    }

# Example usage for testing
if __name__ == "__main__":
    planet = get_random_planet()
    info = get_planet_info(planet)
    for k, v in info.items():
        print(f"{k}: {v}")


