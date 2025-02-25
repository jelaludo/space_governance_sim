from mesa import Agent, Model
import random
from src.hubs import HUBS
from src.events import trigger_random_event
from src.stressors import adjust_stress, STRESS_EVENTS

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

    def reduce_stress(self):
        # Reduce stress when visiting morale-boosting hubs
        if self.target_hub in ["Gym/Recreation", "Entertainment District"] and random.random() < 0.1:
            adjust_stress(self.model, -5, "Agent visited morale hub")

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
            self.reduce_stress_over_time()  # Reduce stress based on conditions
            self.changes_log.append(f"Week {self.week}: Civility {self.civility}, Resources {self.resources}, Stress {self.stress}")

        self.agents.shuffle_do("step")  # Randomly activate agents
        # Handle bad actors, incidents, and stress effects
        for agent in self.agents:
            if isinstance(agent, SettlerAgent):
                # Check for stress-induced bad behavior
                if not agent.is_bad and random.random() < (self.stress / 1000):  # 0.1% per stress point
                    agent.is_bad = True
                    agent.revealed = False  # Starts as hidden (orange)
                    adjust_stress(self, 5, "Good actor turned bad due to stress")
                # Check for stress reduction from visiting hubs
                agent.reduce_stress()
                # Check for incidents with weaker, isolated settlers
                if agent.is_bad and agent.revealed:
                    nearby_agents = [other for other in self.agents if isinstance(other, SettlerAgent) and other != agent and 
                                    abs(other.pos[0] - agent.pos[0]) < 50 and abs(other.pos[1] - agent.pos[1]) < 50]
                    if len(nearby_agents) < 2 and random.random() < 0.1:  # 10% chance of incident if isolated
                        self.civility -= 3  # Incident reduces civility
                        adjust_stress(self, 10, "Incident - Bad actor attacked isolated settler")
                        # Trigger LEO response
                        nearby_leos = [leo for leo in self.agents if isinstance(leo, LEAgent) and 
                                      abs(leo.pos[0] - agent.pos[0]) < 50 and abs(leo.pos[1] - agent.pos[1]) < 50]
                        if nearby_leos and random.random() < 0.7:  # 70% chance LEOs respond
                            self.agents.remove(agent)
                            prisoner = PrisonAgent(self)
                            self.agents.add(prisoner)
                            self.resources -= 5  # Resource cost for prison
                            self.civility = max(0, self.civility - 2)  # Slight civility drop
                            adjust_stress(self, 5, "Bad actor imprisoned")

        # Decay stress slightly each step
        adjust_stress(self, -0.1, "Natural stress decay")
        # Update metrics
        self.update_metrics()

    def trigger_random_event(self):
        from src.events import trigger_random_event  # Import here to avoid circular imports
        trigger_random_event(self)

    def reduce_stress_over_time(self):
        # Reduce stress if civility is high or no incidents recently
        if self.civility >= 70 and random.random() < 0.2:
            adjust_stress(self, -5, "High civility reduces stress")
        if len([log for log in self.changes_log[-10:] if "Incident" in log]) == 0 and self.week > 5 and random.random() < 0.1:
            adjust_stress(self, -10, "Long time without incidents reduces stress")

    def update_metrics(self):
        bad_actors = sum(1 for a in self.agents if isinstance(a, SettlerAgent) and a.is_bad and a.revealed)
        total_settlers = sum(1 for a in self.agents if isinstance(a, SettlerAgent))
        self.conflict_rate = bad_actors / total_settlers if total_settlers > 0 else 0