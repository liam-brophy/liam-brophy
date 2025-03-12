#!/usr/bin/env python3
import os
import re
import random
import json
from datetime import datetime, timedelta
from pathlib import Path

# Fish ASCII art
FISH_TYPES = [
    "<><",
    "><((°>",
    "<°)))><"
]

# Configure the aquarium dimensions
TANK_WIDTH = 70
TANK_HEIGHT = 6
MAX_FISH = 8

# Check if this update is triggered by a feed event
IS_FEEDING = os.environ.get('IS_FEEDING', 'false').lower() == 'true'

# Get the last feeding time from a state file
def get_feeding_state():
    try:
        if Path('.github/aquarium_state.json').exists():
            with open('.github/aquarium_state.json', 'r') as f:
                return json.load(f)
    except Exception:
        pass
    
    return {"last_fed": None, "fast_mode_until": None}

# Update the feeding state
def update_feeding_state(state):
    os.makedirs('.github', exist_ok=True)
    with open('.github/aquarium_state.json', 'w') as f:
        json.dump(state, f)

# Generate a random fish with position
def generate_fish():
    fish_type = random.choice(FISH_TYPES)
    x = random.randint(0, TANK_WIDTH - len(fish_type))
    y = random.randint(0, TANK_HEIGHT - 1)
    return {
        "type": fish_type,
        "x": x,
        "y": y
    }

# Generate the ASCII aquarium
def generate_aquarium(fish_count, fast_mode=False):
    # Create an empty tank
    tank = [[' ' for _ in range(TANK_WIDTH)] for _ in range(TANK_HEIGHT)]
    
    # Generate fish and place them in the tank
    fish = [generate_fish() for _ in range(fish_count)]
    
    # Place fish in the tank
    for f in fish:
        x, y = f["x"], f["y"]
        fish_chars = list(f["type"])
        for i, char in enumerate(fish_chars):
            if 0 <= x + i < TANK_WIDTH:
                tank[y][x + i] = char
    
    # Convert the tank to string
    tank_lines = [''.join(line) for line in tank]
    
    # Add extra speed indicator if in fast mode
    if fast_mode:
        tank_lines.append('')
        tank_lines.append('The fish are swimming faster after being fed! 🌊')
    
    return '\n'.join(['```'] + tank_lines + ['```'])

# Read the current README
with open('README.md', 'r') as f:
    readme = f.read()

# Get feeding state
state = get_feeding_state()

# If this is a feed event, update the state
if IS_FEEDING:
    now = datetime.now().isoformat()
    state["last_fed"] = now
    state["fast_mode_until"] = (datetime.now() + timedelta(hours=24)).isoformat()
    update_feeding_state(state)

# Check if we're in fast mode
fast_mode = False
if state.get("fast_mode_until"):
    try:
        fast_until = datetime.fromisoformat(state["fast_mode_until"])
        if datetime.now() < fast_until:
            fast_mode = True
    except ValueError:
        pass

# Generate new aquarium
fish_count = random.randint(5, MAX_FISH)
new_aquarium = generate_aquarium(fish_count, fast_mode)

# Replace the aquarium section in the README
new_readme = re.sub(
    r'(<!-- Fish will be updated via GitHub Actions -->)\n```.*?```',
    r'\1\n' + new_aquarium,
    readme,
    flags=re.DOTALL
)

# Write the updated README
with open('README.md', 'w') as f:
    f.write(new_readme)

print(f"Updated aquarium with {fish_count} fish. Fast mode: {fast_mode}")
