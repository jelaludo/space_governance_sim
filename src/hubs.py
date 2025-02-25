# hubs.py: Define hub properties and logic
HUBS = {
    "Housing District": {"pos": (400, 300), "risk": 0.1, "purpose": "living"},  # Center
    "Gym/Recreation": {"pos": (400, 250), "risk": 0.4, "purpose": "morale"},    # Center
    "Medical Bay": {"pos": (400, 350), "risk": 0.2, "purpose": "health"},        # Center
    "Command Center": {"pos": (200, 200), "risk": 0.1, "purpose": "governance"},  # Spoke NW
    "Factory": {"pos": (600, 200), "risk": 0.5, "purpose": "production"},        # Spoke NE
    "Farming Module": {"pos": (200, 400), "risk": 0.2, "purpose": "survival"},   # Spoke SW
    "Entertainment District": {"pos": (600, 400), "risk": 0.8, "purpose": "social"},  # Spoke SE
    "Power Plant": {"pos": (300, 150), "risk": 0.7, "purpose": "infrastructure"},    # Spoke N
    "Water Treatment": {"pos": (500, 150), "risk": 0.4, "purpose": "survival"},      # Spoke N
    "Research Lab": {"pos": (300, 450), "risk": 0.5, "purpose": "innovation"},       # Spoke S
    "Mining Outpost": {"pos": (500, 450), "risk": 0.7, "purpose": "resources"},      # Spoke S
    "Prison Hub": {"pos": (400, 150), "risk": 0.9, "purpose": "security"},           # Spoke top
    "Morgue": {"pos": (700, 300), "risk": 0.1, "purpose": "absorbing"}              # Far right, near center for visibility
}

def get_hub_position(hub_name):
    return HUBS[hub_name]["pos"]

def get_hub_risk(hub_name):
    return HUBS[hub_name]["risk"]

def get_hub_purpose(hub_name):
    return HUBS[hub_name]["purpose"]