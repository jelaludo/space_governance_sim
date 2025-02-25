from mesa import Agent, Model
import random

# Hub definitions
HUBS = {
    "Command Center": {"pos": (50, 50), "risk": 0.1, "purpose": "governance"},
    "Factory": {"pos": (150, 100), "risk": 0.5, "purpose": "production"},
    "Farming Module": {"pos": (250, 150), "risk": 0.2, "purpose": "survival"},
    "Housing District": {"pos": (350, 200), "risk": 0.1, "purpose": "living"},
    "Entertainment District": {"pos": (450, 250), "risk": 0.8, "purpose": "social"},
    "Gym/Recreation": {"pos": (550, 300), "risk": 0.4, "purpose": "morale"},
    "Power Plant": {"pos": (650, 350), "risk": 0.7, "purpose": "infrastructure"},
    "Water Treatment": {"pos": (100, 400), "risk": 0.4, "purpose": "survival"},
    "Medical Bay": {"pos": (200, 450), "risk": 0.2, "purpose": "health"},
    "Research Lab": {"pos": (300, 500), "risk": 0.5, "purpose": "innovation"},
    "Mining Outpost": {"pos": (400, 550), "risk": 0.7, "purpose": "resources"},
    "Prison Hub": {"pos": (500, 600), "risk": 0.9, "purpose": "security"}
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
        # Randomly change hub (more frequent for variety)
        if random.random() < 0.2:  # Increased chance for more movement
            if self.is_bad and self.revealed:
                self.target_hub = random.choice(["Entertainment District", "Power Plant", "Mining Outpost"])
            else:
                self.target_hub = random.choice(["Housing District", "Farming Module", "Gym/Recreation"])

class PrisonAgent(Agent):
    def __init__(self, model):
        super().__init__(model)
        self.pos = (500, 600)  # Prison hub position
        self.is_prisoner = True

class LEAgent(Agent):
    def __init__(self, model, is_bad=False):
        super().__init__(model)
        self.is_bad = is_bad  # Corrupt LEO chance (e.g., 5%)
        self.pos = (random.randint(0, 700), random.randint(0, 550))  # Larger area for 800x600
        self.patrol_index = 0  # Track current patrol hub

    def step(self):
        # Patrol hubs in sequence or randomly
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
            self.changes_log.append(f"Week {self.week}: Civility {self.civility}, Resources {self.resources}")

        self.agents.shuffle_do("step")  # Randomly activate agents
        # Handle bad actors and incidents
        for agent in self.agents:
            if isinstance(agent, SettlerAgent) and agent.is_bad and agent.revealed:
                # Check for weaker, isolated settlers (e.g., far from other agents)
                nearby_agents = [other for other in self.agents if isinstance(other, SettlerAgent) and other != agent and 
                                abs(other.pos[0] - agent.pos[0]) < 50 and abs(other.pos[1] - agent.pos[1]) < 50]
                if len(nearby_agents) < 2 and random.random() < 0.1:  # 10% chance of incident if isolated
                    self.civility -= 3  # Incident reduces civility
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
                        self.changes_log.append(f"Week {self.week}: Bad actor imprisoned, -5 resources")

        # Update metrics (e.g., conflict rate)
        self.update_metrics()

    def update_metrics(self):
        bad_actors = sum(1 for a in self.agents if isinstance(a, SettlerAgent) and a.is_bad and a.revealed)
        self.conflict_rate = bad_actors / 20  # Normalize by total settlers