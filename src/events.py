# events.py: Define events and random event triggers
import random

def trigger_random_event(model):
    events = [
        ("Power Plant Break", 20, lambda: power_plant_break(model)),
        ("Environmental Hardship", 15, lambda: environmental_hardship(model)),
        ("New Settler Arrival", 15, lambda: new_settler_arrival(model)),
        ("Food Shortage", 10, lambda: food_shortage(model)),
        ("Oxygen Leak", 10, lambda: oxygen_leak(model)),
        ("Equipment Failure", 10, lambda: equipment_failure(model)),
        ("Meteor Threat", 5, lambda: meteor_threat(model)),
        ("Corruption Scandal", 5, lambda: corruption_scandal(model)),
        ("Tech Breakthrough", 5, lambda: tech_breakthrough(model)),
        ("Disease Outbreak", 5, lambda: disease_outbreak(model)),
        ("Resource Discovery", 5, lambda: resource_discovery(model)),
        ("Sabotage Attempt", 5, lambda: sabotage_attempt(model)),
        ("New Supply from Colony", 5, lambda: new_supply_from_colony(model)),
        ("Morale Boost After Fix", 5, lambda: morale_boost_after_fix(model))
    ]
    total_weight = sum(weight for _, weight, _ in events)
    choice = random.uniform(0, total_weight)
    cumulative = 0
    for name, weight, action in events:
        cumulative += weight
        if choice <= cumulative:
            model.changes_log.append(f"Week {model.week}: Event - {name}")
            action()
            break

def power_plant_break(model):
    from src.stressors import adjust_stress
    from src.model import GovernanceModel  # Dynamic import to avoid circular issues
    adjust_stress(model, 20, "Power Plant Break - Increased visits required")
    model.resources -= 10
    model.changes_log.append(f"Week {model.week}: Power Plant Break - Increased visits required, -10 resources")

def environmental_hardship(model):
    from src.stressors import adjust_stress
    from src.model import GovernanceModel  # Dynamic import to avoid circular issues
    adjust_stress(model, 30, "Environmental Hardship for 2 weeks")
    model.resources -= 15
    model.step_count += 20  # Lasts 2 weeks (20 steps)
    model.changes_log.append(f"Week {model.week}: Environmental Hardship for 2 weeks, -15 resources")

def new_settler_arrival(model):
    from src.stressors import adjust_stress
    from src.model import GovernanceModel, SettlerAgent  # Dynamic import to avoid circular issues
    adjust_stress(model, 15, "5 New Settlers Arrived")
    for _ in range(5):  # Add 5 new settlers
        gender = random.choice(["M", "F"])
        is_bad = random.random() < 0.15  # 15% chance new settlers are bad
        settler = SettlerAgent(model, gender, is_bad)
        model.agents.add(settler)
    model.changes_log.append(f"Week {model.week}: 5 New Settlers Arrived, +15 stress")

def food_shortage(model):
    from src.stressors import adjust_stress
    from src.model import GovernanceModel  # Dynamic import to avoid circular issues
    adjust_stress(model, 25, "Food Shortage")
    model.resources -= 20
    model.changes_log.append(f"Week {model.week}: Food Shortage, -20 resources")

def oxygen_leak(model):
    from src.stressors import adjust_stress
    from src.model import GovernanceModel  # Dynamic import to avoid circular issues
    adjust_stress(model, 40, "Oxygen Leak")
    model.resources -= 30
    model.civility -= 10
    model.changes_log.append(f"Week {model.week}: Oxygen Leak, -30 resources, -10 civility")

def equipment_failure(model):
    from src.stressors import adjust_stress
    from src.hubs import HUBS  # Import HUBS dynamically for this function
    from src.model import GovernanceModel  # Dynamic import to avoid circular issues
    adjust_stress(model, 15, "Equipment Failure")
    model.resources -= 10
    hub = random.choice(list(HUBS.keys()))
    model.changes_log.append(f"Week {model.week}: Equipment Failure at {hub}, -10 resources")

def meteor_threat(model):
    from src.stressors import adjust_stress
    from src.model import GovernanceModel  # Dynamic import to avoid circular issues
    adjust_stress(model, 30, "Meteor Threat")
    model.civility -= 5
    model.changes_log.append(f"Week {model.week}: Meteor Threat, -5 civility")

def corruption_scandal(model):
    from src.stressors import adjust_stress
    from src.model import GovernanceModel, LEAgent  # Dynamic import to avoid circular issues
    adjust_stress(model, 25, "Corruption Scandal")
    model.civility -= 15
    for agent in model.agents:
        if isinstance(agent, LEAgent) and random.random() < 0.3:  # 30% chance any LEO is corrupt
            agent.is_bad = True
    model.changes_log.append(f"Week {model.week}: Corruption Scandal, -15 civility")

def tech_breakthrough(model):
    from src.stressors import adjust_stress
    from src.model import GovernanceModel  # Dynamic import to avoid circular issues
    adjust_stress(model, -10, "Tech Breakthrough")
    model.resources += 15
    model.changes_log.append(f"Week {model.week}: Tech Breakthrough, +15 resources, -10 stress")

def disease_outbreak(model):
    from src.stressors import adjust_stress
    from src.model import GovernanceModel  # Dynamic import to avoid circular issues
    adjust_stress(model, 20, "Disease Outbreak")
    model.resources -= 20
    model.civility -= 5
    model.changes_log.append(f"Week {model.week}: Disease Outbreak, -20 resources, -5 civility")

def resource_discovery(model):
    from src.stressors import adjust_stress
    from src.model import GovernanceModel  # Dynamic import to avoid circular issues
    adjust_stress(model, -15, "Resource Discovery")
    model.resources += 25
    model.changes_log.append(f"Week {model.week}: Resource Discovery, +25 resources, -15 stress")

def sabotage_attempt(model):
    from src.stressors import adjust_stress
    from src.model import GovernanceModel, SettlerAgent  # Dynamic import to avoid circular issues
    adjust_stress(model, 35, "Sabotage Attempt")
    model.civility -= 10
    for agent in model.agents:
        if isinstance(agent, SettlerAgent) and agent.is_bad and random.random() < 0.2:
            agent.revealed = True  # Reveal bad actors involved in sabotage
    model.changes_log.append(f"Week {model.week}: Sabotage Attempt, -10 civility")

def new_supply_from_colony(model):
    from src.stressors import adjust_stress
    from src.model import GovernanceModel  # Dynamic import to avoid circular issues
    adjust_stress(model, -20, "New Supply from Colony")
    model.resources += 30
    model.changes_log.append(f"Week {model.week}: New Supply from Colony, +30 resources, -20 stress")

def morale_boost_after_fix(model):
    from src.stressors import adjust_stress
    from src.model import GovernanceModel  # Dynamic import to avoid circular issues
    adjust_stress(model, -15, "Morale Boost After Fix")
    model.civility += 5
    model.changes_log.append(f"Week {model.week}: Morale Boost After Fix, +5 civility, -15 stress")