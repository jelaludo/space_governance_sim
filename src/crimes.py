# crimes.py: Define crime types, probabilities, and impacts for the simulation

CRIMES = {
    "Larceny/Theft": {
        "probability": 0.65,  # 65% of property crimes, ~52% of all crimes
        "stress_impact": 5,   # Low stress increase
        "conflict_impact": 0.05,  # Small conflict rate increase
        "description": "A bad actor steals property from a weaker settler."
    },
    "Motor Vehicle Theft": {
        "probability": 0.075,  # 7.5% of property crimes, ~6% of all crimes
        "stress_impact": 10,   # Moderate stress increase
        "conflict_impact": 0.10,  # Moderate conflict rate increase
        "description": "A bad actor steals a vehicle or equipment from a weaker settler."
    },
    "Burglary": {
        "probability": 0.125,  # 12.5% of property crimes, ~10% of all crimes
        "stress_impact": 15,   # Moderate stress increase
        "conflict_impact": 0.15,  # Moderate conflict rate increase
        "description": "A bad actor breaks into a weaker settler’s residence or hub."
    },
    "Simple Assault": {
        "probability": 0.10,  # 10% of violent crimes, ~2% of all crimes
        "stress_impact": 20,   # Moderate stress increase
        "conflict_impact": 0.20,  # Moderate conflict rate increase
        "description": "A bad actor physically attacks a weaker settler without severe injury."
    },
    "Aggravated Assault": {
        "probability": 0.065,  # 6.5% of violent crimes, ~1.3% of all crimes
        "stress_impact": 30,   # High stress increase
        "conflict_impact": 0.25,  # High conflict rate increase
        "description": "A bad actor severely injures a weaker settler."
    },
    "Robbery": {
        "probability": 0.02,  # 2% of violent crimes, ~0.4% of all crimes
        "stress_impact": 40,   # High stress increase
        "conflict_impact": 0.30,  # High conflict rate increase
        "description": "A bad actor robs a weaker settler using force or threat."
    },
    "Rape": {
        "probability": 0.0075,  # 0.75% of violent crimes, ~0.15% of all crimes
        "stress_impact": 50,   # Very high stress increase
        "conflict_impact": 0.35,  # Very high conflict rate increase
        "description": "A bad actor commits a sexual assault against a weaker settler."
    },
    "Murder/Nonnegligent Manslaughter": {
        "probability": 0.0015,  # 0.15% of violent crimes, ~0.03% of all crimes
        "stress_impact": 100,  # Extreme stress increase
        "conflict_impact": 0.50,  # Extreme conflict rate increase
        "description": "A bad actor kills a weaker settler."
    },
    "Property Destruction/Vandalism": {
        "probability": 0.075,  # 7.5% of other crimes, ~7.5% of all crimes
        "stress_impact": 15,   # Moderate stress increase
        "conflict_impact": 0.15,  # Moderate conflict rate increase
        "description": "A bad actor damages property or infrastructure."
    }
}

# Total probability should sum to ~100% (adjust as needed for simulation balance)
TOTAL_PROBABILITY = sum(crime["probability"] for crime in CRIMES.values())
for crime in CRIMES.values():
    crime["normalized_probability"] = crime["probability"] / TOTAL_PROBABILITY

def select_crime():
    """Select a random crime based on normalized probabilities."""
    rand = random.random()
    cumulative = 0
    for crime_name, crime_data in CRIMES.items():
        cumulative += crime_data["normalized_probability"]
        if rand <= cumulative:
            return crime_name, crime_data
    return list(CRIMES.keys())[0], CRIMES[list(CRIMES.keys())[0]]  # Fallback

def apply_crime_impact(model, crime_name, crime_data):
    """Apply stress and conflict impacts from a crime to the model."""
    model.stress = max(0, min(100, model.stress + crime_data["stress_impact"]))
    model.conflict_rate = max(0, min(1.0, model.conflict_rate + crime_data["conflict_impact"]))
    model.changes_log.append(f"Day {model.week}: {crime_data['description']} - Stress now {model.stress}, Conflict now {model.conflict_rate:.2f}")