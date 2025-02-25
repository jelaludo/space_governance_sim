from mesa import Agent, Model
import random

# Hub definitions in hub-and-spoke pattern (housing, gym, medical in center at (400, 300))
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
    "Prison Hub": {"pos": (400, 150), "risk": 0.9, "purpose": "security"}            # Spoke top
}

class SettlerAgent(Agent):
    def __init__(self, model, gender, is_bad=False):
        super().__init__(model)
        self.gender = gender  # "M" for men (squares), "F" for women (circles)
        self.is_bad = is_bad  # Bad actor flag
        self.revealed = False if is_bad else True  # Hidden bad actors
        self.pos = (random.randint(0, 700), random.randint(0, 550))  # Larger area for 800x600
        self.target_hub = random.choice(list(HUBS.keys()))  # Start with random hub

    def step(self):
        hub_pos = HUBS[self.target_hub]["pos"]
        target_x, target_y = hub_pos
        # Move toward target hub, but clamp to stay on-screen
        new_x = self.pos[0] + (target_x - self.pos[0]) // 10
        new_y = self.pos[1] + (target_y - self.pos[1]) // 10
        self.pos = (max(5, min(795, new_x)), max(5, min(595, new_y)))
        # Randomly change hub based on purpose and stress
        if random.random() < 0.2:  # Increased chance for more movement
            if self.is_bad and self.revealed:
                self.target_hub = random.choice(["Entertainment District", "Power Plant", "Mining Outpost", "Prison Hub"])
            else:
                purposes = [h for h in HUBS if HUBS[h]["purpose"] in ["living", "morale", "health", "survival"]]
                self.target_hub = random.choice(purposes)

class PrisonAgent(Agent):
    def __init__(self, model):
        super().__init__(model)
        self.pos = HUBS["Prison Hub"]["pos"]  # Use prison hub position
        self.is_prisoner = True

class LEAgent(Agent):
    def __init__(self, model, is_bad=False):
        super().__init__(model)
        self.is_bad = is_bad  # Corrupt LEO chance (e.g., 5%)
        self.pos = (random.randint(0, 700), random.randint(0, 550))  # Larger area for 800x600
        self.patrol_index = 0  # Track current patrol hub

    def step(self):
        # Patrol all hubs in sequence or randomly
        hubs = list(HUBS.keys())
        if random.random() < 0.7:  # 70% chance to patrol systematically, 30% random
            self.patrol_index = (self.patrol_index + 1) % len(hubs)
            self.target_hub = hubs[self.patrol_index]
        else:
            self.target_hub = random.choice(hubs)
        
        hub_pos = HUBS[self.target_hub]["pos"]
        target_x, target_y = hub_pos
        # Move toward target hub, but clamp to stay on-screen
        new_x = self.pos[0] + (target_x - self.pos[0]) // 10
        new_y = self.pos[1] + (target_y - self.pos[1]) // 10
        self.pos = (max(5, min(795, new_x)), max(5, min(595, new_y)))

class GovernanceModel(Model):
    def __init__(self):
        super().__init__()
        self.civility = 50
        self.resources = 100  # Initial resources
        self.week = 0
        self.steps_per_week = 10  # 10 steps = 1 week
        self.step_count = 0
        self.conflict_rate = 0
        self.changes_log = []  # Log of key changes
        self.stress = 0  # New stress metric (0-100)

        # Create agents with unique IDs assigned by Mesa
        for i in range(20):  # Settlers
            gender = "M" if i < 10 else "F"  # Half men, half women
            is_bad = random.random() < 0.1  # 10% bad actors
            agent = SettlerAgent(self, gender, is_bad)
            self.agents.add(agent)
        for i in range(2):  # 2 LEOs
            is_bad = random.random() < 0.05  # 5% chance of corrupt LEO
            le_agent = LEAgent(self, is_bad)
            self.agents.add(le_agent)

    def step(self):
        self.step_count += 1
        if self.step_count % self.steps_per_week == 0:
            self.week += 1
            self.trigger_random_event()  # Trigger a random event each week
            self.changes_log.append(f"Week {self.week}: Civility {self.civility}, Resources {self.resources}, Stress {self.stress}")

        self.agents.shuffle_do("step")  # Randomly activate agents
        # Handle bad actors, incidents, and stress effects
        for agent in self.agents:
            if isinstance(agent, SettlerAgent):
                # Check for stress-induced bad behavior
                if not agent.is_bad and random.random() < (self.stress / 1000):  # 0.1% per stress point
                    agent.is_bad = True
                    agent.revealed = False  # Starts as hidden (orange)
                    self.changes_log.append(f"Week {self.week}: Good actor turned bad due to stress")
                # Check for incidents with weaker, isolated settlers
                if agent.is_bad and agent.revealed:
                    nearby_agents = [other for other in self.agents if isinstance(other, SettlerAgent) and other != agent and 
                                    abs(other.pos[0] - agent.pos[0]) < 50 and abs(other.pos[1] - agent.pos[1]) < 50]
                    if len(nearby_agents) < 2 and random.random() < 0.1:  # 10% chance of incident if isolated
                        self.civility -= 3  # Incident reduces civility
                        self.stress += 10  # Increase stress from incident
                        self.changes_log.append(f"Week {self.week}: Incident - Bad actor attacked isolated settler")
                        # Trigger LEO response
                        nearby_leos = [leo for leo in self.agents if isinstance(leo, LEAgent) and 
                                      abs(leo.pos[0] - agent.pos[0]) < 50 and abs(leo.pos[1] - agent.pos[1]) < 50]
                        if nearby_leos and random.random() < 0.7:  # 70% chance LEOs respond
                            self.agents.remove(agent)
                            prisoner = PrisonAgent(self)
                            self.agents.add(prisoner)
                            self.resources -= 5  # Resource cost for prison
                            self.civility = max(0, self.civility - 2)  # Slight civility drop
                            self.stress += 5  # Additional stress from imprisonment
                            self.changes_log.append(f"Week {self.week}: Bad actor imprisoned, -5 resources")

        # Decay stress slightly each step
        self.stress = max(0, self.stress - 0.1)
        # Update metrics
        self.update_metrics()

    def trigger_random_event(self):
        events = [
            ("Power Plant Break", 20, lambda: self.power_plant_break()),
            ("Environmental Hardship", 15, lambda: self.environmental_hardship()),
            ("New Settler Arrival", 15, lambda: self.new_settler_arrival()),
            ("Food Shortage", 10, lambda: self.food_shortage()),
            ("Oxygen Leak", 10, lambda: self.oxygen_leak()),
            ("Equipment Failure", 10, lambda: self.equipment_failure()),
            ("Meteor Threat", 5, lambda: self.meteor_threat()),
            ("Corruption Scandal", 5, lambda: self.corruption_scandal()),
            ("Tech Breakthrough", 5, lambda: self.tech_breakthrough()),
            ("Disease Outbreak", 5, lambda: self.disease_outbreak()),
            ("Resource Discovery", 5, lambda: self.resource_discovery()),
            ("Sabotage Attempt", 5, lambda: self.sabotage_attempt())
        ]
        total_weight = sum(weight for _, weight, _ in events)
        choice = random.uniform(0, total_weight)
        cumulative = 0
        for name, weight, action in events:
            cumulative += weight
            if choice <= cumulative:
                self.changes_log.append(f"Week {self.week}: Event - {name}")
                action()
                break

    def power_plant_break(self):
        self.stress += 20
        self.resources -= 10
        self.changes_log.append(f"Week {self.week}: Power Plant Break - Increased visits required, -10 resources")

    def environmental_hardship(self):
        self.stress += 30
        self.resources -= 15
        self.step_count += 20  # Lasts 2 weeks (20 steps)
        self.changes_log.append(f"Week {self.week}: Environmental Hardship for 2 weeks, -15 resources")

    def new_settler_arrival(self):
        self.stress += 15
        for _ in range(5):  # Add 5 new settlers
            gender = random.choice(["M", "F"])
            is_bad = random.random() < 0.15  # 15% chance new settlers are bad
            agent = SettlerAgent(self, gender, is_bad)
            self.agents.add(agent)
        self.changes_log.append(f"Week {self.week}: 5 New Settlers Arrived, +15 stress")

    def food_shortage(self):
        self.stress += 25
        self.resources -= 20
        self.changes_log.append(f"Week {self.week}: Food Shortage, -20 resources")

    def oxygen_leak(self):
        self.stress += 40
        self.resources -= 30
        self.civility -= 10
        self.changes_log.append(f"Week {self.week}: Oxygen Leak, -30 resources, -10 civility")

    def equipment_failure(self):
        self.stress += 15
        self.resources -= 10
        hub = random.choice(list(HUBS.keys()))
        self.changes_log.append(f"Week {self.week}: Equipment Failure at {hub}, -10 resources")

    def meteor_threat(self):
        self.stress += 30
        self.civility -= 5
        self.changes_log.append(f"Week {self.week}: Meteor Threat, -5 civility")

    def corruption_scandal(self):
        self.stress += 25
        self.civility -= 15
        for agent in self.agents:
            if isinstance(agent, LEAgent) and random.random() < 0.3:  # 30% chance any LEO is corrupt
                agent.is_bad = True
        self.changes_log.append(f"Week {self.week}: Corruption Scandal, -15 civility")

    def tech_breakthrough(self):
        self.stress -= 10
        self.resources += 15
        self.changes_log.append(f"Week {self.week}: Tech Breakthrough, +15 resources, -10 stress")

    def disease_outbreak(self):
        self.stress += 20
        self.resources -= 20
        self.civility -= 5
        self.changes_log.append(f"Week {self.week}: Disease Outbreak, -20 resources, -5 civility")

    def resource_discovery(self):
        self.stress -= 15
        self.resources += 25
        self.changes_log.append(f"Week {self.week}: Resource Discovery, +25 resources, -15 stress")

    def sabotage_attempt(self):
        self.stress += 35
        self.civility -= 10
        for agent in self.agents:
            if isinstance(agent, SettlerAgent) and agent.is_bad and random.random() < 0.2:
                agent.revealed = True  # Reveal bad actors involved in sabotage
        self.changes_log.append(f"Week {self.week}: Sabotage Attempt, -10 civility")

    def update_metrics(self):
        bad_actors = sum(1 for a in self.agents if isinstance(a, SettlerAgent) and a.is_bad and a.revealed)
        total_settlers = sum(1 for a in self.agents if isinstance(a, SettlerAgent))
        self.conflict_rate = bad_actors / total_settlers if total_settlers > 0 else 0