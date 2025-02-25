# stressors.py: Manage stress mechanics
STRESS_EVENTS = {}  # Can expand later for event-specific stress tracking

def adjust_stress(model, amount, reason):
    model.stress = max(0, min(100, model.stress + amount))  # Cap stress at 0-100
    model.changes_log.append(f"Week {model.week}: {reason}, Stress now {model.stress}")