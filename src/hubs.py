# hubs.py: Define hub properties and logic
HUBS = {
    "Housing District": {"pos": (400, 350), "risk": 0.1, "purpose": "living"},  # Center, moved down 50
    "Gym/Recreation": {"pos": (400, 300), "risk": 0.4, "purpose": "morale"},    # Center, moved down 50
    "Medical Bay": {"pos": (400, 400), "risk": 0.2, "purpose": "health"},        # Center, moved down 50
    "Command Center": {"pos": (150, 200), "risk": 0.1, "purpose": "governance"},  # Spoke NW, moved left 50
    "Factory": {"pos": (650, 200), "risk": 0.5, "purpose": "production"},        # Spoke NE, moved right 50
    "Farming Module": {"pos": (150, 450), "risk": 0.2, "purpose": "survival"},   # Spoke SW, moved left 50
    "Entertainment District": {"pos": (650, 450), "risk": 0.8, "purpose": "social"},  # Spoke SE, moved right 50
    "Power Plant": {"pos": (250, 150), "risk": 0.7, "purpose": "infrastructure"},    # Spoke N, moved left 50
    "Water Treatment": {"pos": (550, 150), "risk": 0.4, "purpose": "survival"},      # Spoke N, moved right 50
    "Research Lab": {"pos": (250, 500), "risk": 0.5, "purpose": "innovation"},       # Spoke S, moved left 50
    "Mining Outpost": {"pos": (550, 500), "risk": 0.7, "purpose": "resources"},      # Spoke S, moved right 50
    "Prison Hub": {"pos": (400, 200), "risk": 0.9, "purpose": "security"},           # Spoke top, moved up 50
    "Morgue": {"pos": (750, 350), "risk": 0.1, "purpose": "absorbing"}              # Far right, near center, moved right 50
}

def get_hub_position(hub_name):
    return HUBS[hub_name]["pos"]

def get_hub_risk(hub_name):
    return HUBS[hub_name]["risk"]

def get_hub_purpose(hub_name):
    return HUBS[hub_name]["purpose"]