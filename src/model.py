from mesa import Agent, Model
import random
from src.hubs import HUBS
from src.events import trigger_random_event
from src.stressors import adjust_stress, STRESS_EVENTS

class SettlerAgent(Agent):
    def __init__(self, model, gender, is_bad=False):
        super().__init__(model)
        self.gender = gender  # "M" for men (squares), "F" for women (circles/dots)
        self.is_bad = is_bad  # Bad actor flag
        self.revealed = False if is_bad else True  # Hidden bad actors
        self.pos = (random.randint(0, 700), random.randint(0, 550))  # Larger area for 800x600
        self.target_hub = random.choice(list(HUBS.keys()))  # Start with random hub

    def step(self):
        hub_pos = HUBS[self.target_hub]["pos"]
        target_x, target_y = hub_pos
        # Move toward target hub very slowly and smoothly, clamp to stay on-screen
        new_x = self.pos[0] + (target_x - self.pos[0]) // 30  # Slower, smoother movement
        new_y = self.pos[1] + (target_y - self.pos[1]) // 30  # Slower, smoother movement
        jitter_x = random.randint(-3, 3)  # Reduced jitter for smoother motion
        jitter_y = random.randint(-3, 3)  # Reduced jitter for smoother motion
        self.pos = (max(5, min(795, new_x + jitter_x)), max(5, min(595, new_y + jitter_y)))
        # Check if agent "touches" the target hub (within 20 pixels) to trigger stat changes
        if abs(self.pos[0] - target_x) <= 20 and abs(self.pos[1] - target_y) <= 20:
            if self.target_hub in ["Farming Module", "Factory", "Water Treatment", "Command Center"]:
                self.model.resources = min(200, self.model.resources + random.randint(1, 3))  # Cap resources at 200, increase by 1-3
            elif self.target_hub in ["Gym/Recreation", "Entertainment District"]:
                self.reduce_stress()
        # Randomly change hub based on purpose and stress, increase remote hub visits
        if random.random() < 0.3:  # Increased chance for more movement (30%)
            if self.is_bad and self.revealed:
                self.target_hub = random.choice(["Entertainment District", "Power Plant", "Mining Outpost", "Prison Hub"])
            else:
                if random.random() < 0.2:  # 20% chance each for remote hubs
                    self.target_hub = random.choice(["Factory", "Water Treatment", "Command Center", "Farming Module"])
                else:
                    purposes = [h for h in HUBS if HUBS[h]["purpose"] in ["living", "morale", "health", "survival"]]
                    remote_hubs = ["Power Plant", "Mining Outpost", "Research Lab"]
                    if random.random() < 0.1:  # 10% chance to visit a remote hub
                        self.target_hub = random.choice(remote_hubs)
                    else:
                        self.target_hub = random.choice(purposes)

    def reduce_stress(self):
        # Reduce stress when visiting morale-boosting hubs
        if self.target_hub in ["Gym/Recreation", "Entertainment District"] and random.random() < 0.1:
            adjust_stress(self.model, -5, "Agent visited morale hub")

class PrisonAgent(Agent):
    def __init__(self, model, original_agent):
        super().__init__(model)
        self.pos = HUBS["Prison Hub"]["pos"]  # Prison hub position
        self.is_prisoner = True
        self.original_gender = original_agent.gender  # Store original gender for visualization
        self.is_bad = original_agent.is_bad  # Retain bad actor status

    def step(self):
        # Prisoners stay in prison (absorbing state)
        self.pos = HUBS["Prison Hub"]["pos"]

class DeadAgent(Agent):
    def __init__(self, model, original_agent):
        super().__init__(model)
        self.pos = HUBS["Morgue"]["pos"]  # Morgue hub position (moved further away)
        self.is_dead = True
        self.original_gender = original_agent.gender  # Store original gender for visualization

    def step(self):
        # Dead agents stay in morgue (absorbing state)
        self.pos = HUBS["Morgue"]["pos"]

class LEAgent(Agent):
    def __init__(self, model, is_bad=False):
        super().__init__(model)
        self.is_bad = is_bad  # Corrupt LEO chance (e.g., 5%)
        self.gender = "M" if random.random() < 0.9 else "F"  # 90% male, 10% female for LEOs
        self.pos = (random.randint(0, 700), random.randint(0, 550))  # Larger area for 800x600
        self.patrol_index = 0  # Track current patrol hub
        self.chasing = None  # Track if chasing a bad actor

    def step(self):
        if self.chasing:
            # Chase the bad actor directly
            bad_actor_pos = self.chasing.pos
            target_x, target_y = bad_actor_pos
            new_x = self.pos[0] + (target_x - self.pos[0]) // 10  # Faster chase
            new_y = self.pos[1] + (target_y - self.pos[1]) // 10  # Faster chase
            self.pos = (max(5, min(795, new_x)), max(5, min(595, new_y)))
            # Check if close enough to escort to prison
            if abs(self.pos[0] - bad_actor_pos[0]) < 10 and abs(self.pos[1] - bad_actor_pos[1]) < 10:
                self.model.agents.remove(self.chasing)
                prisoner = PrisonAgent(self.model, self.chasing)
                self.model.agents.add(prisoner)
                self.model.resources -= 5  # Resource cost for prison
                self.model.civility = max(0, self.model.civility - 2)  # Slight civility drop
                adjust_stress(self.model, -10, "Bad actor imprisoned, reducing stress for good actors")  # Stress reduction
                self.model.prison_count += 1  # Increment prison counter
                self.model.changes_log.append(f"Week {self.model.week}: Bad actor imprisoned by LEO, -5 resources, -10 stress, Prison now {self.model.prison_count}")
                self.chasing = None  # Stop chasing
        else:
            # Systematic patrol of all hubs in fixed order, no randomness, extra slow movement
            hubs = list(HUBS.keys())
            self.patrol_index = (self.patrol_index + 1) % len(hubs)  # Always systematic, no randomness
            self.target_hub = hubs[self.patrol_index]
            hub_pos = HUBS[self.target_hub]["pos"]
            target_x, target_y = hub_pos
            # Move toward target hub extra slowly, clamp to stay on-screen, add slight jitter
            new_x = self.pos[0] + (target_x - self.pos[0]) // 40  # Extra slow movement for LEOs
            new_y = self.pos[1] + (target_y - self.pos[1]) // 40  # Extra slow movement for LEOs
            jitter_x = random.randint(-3, 3)  # Reduced jitter for smoother motion
            jitter_y = random.randint(-3, 3)  # Reduced jitter for smoother motion
            self.pos = (max(5, min(795, new_x + jitter_x)), max(5, min(595, new_y + jitter_y)))
            # Check for bad actors acting violently to initiate chase
            for agent in self.model.agents:
                if isinstance(agent, SettlerAgent) and agent.is_bad and agent.revealed:
                    nearby_agents = [other for other in self.model.agents if isinstance(other, SettlerAgent) and other != agent and 
                                    abs(other.pos[0] - agent.pos[0]) < 50 and abs(other.pos[1] - agent.pos[1]) < 50]
                    if len(nearby_agents) < 2 and random.random() < 0.05:  # Reduced to 5% for slower population drop
                        self.chasing = agent  # Start chasing this bad actor
                        break

class GovernanceModel(Model):
    def __init__(self):
        super().__init__()
        self.civility = 50
        self.resources = 100  # Initial resources, cap at 200
        self.week = 0
        self.steps_per_week = 100  # 100 steps = 1 week for slower observation
        self.step_count = 0
        self.conflict_rate = 0
        self.changes_log = []  # Log of key changes
        self.stress = 0  # New stress metric (0-100)
        self.morgue_count = 0  # Counter for dead agents in Morgue
        self.prison_count = 0  # Counter for imprisoned agents in Prison

        # Update HUBS to include Morgue (moved further away)
        HUBS["Morgue"] = {"pos": (700, 300), "risk": 0.1, "purpose": "absorbing"}  # Far right, near center for visibility

        # Create agents with unique IDs assigned by Mesa, double initial population
        self.living_agents = []  # Track all living agents (settlers + LEOs)
        for i in range(40):  # Double settlers to 40
            gender = "M" if i < 20 else "F"  # Half men, half women
            is_bad = random.random() < 0.1  # 10% bad actors
            agent = SettlerAgent(self, gender, is_bad)
            self.living_agents.append(agent)
            self.agents.add(agent)
        for i in range(4):  # Double LEOs to 4
            is_bad = random.random() < 0.05  # 5% chance of corrupt LEO
            le_agent = LEAgent(self, is_bad)
            self.living_agents.append(le_agent)
            self.agents.add(le_agent)

    def step(self):
        self.step_count += 1
        if self.step_count % self.steps_per_week == 0:
            self.week += 1
            self.trigger_random_event()  # Trigger a random event every other week for slower pace
            self.reduce_stress_over_time()  # Reduce stress based on conditions
            self.changes_log.append(f"Week {self.week}: Civility {self.civility}, Resources {self.resources}, Stress {self.stress}, Population {len(self.living_agents)}, Morgue {self.morgue_count}, Prison {self.prison_count}")

        self.agents.shuffle_do("step")  # Randomly activate agents
        # Handle bad actors, incidents, deaths, and stress effects
        for agent in list(self.agents):  # Use list to modify agents during iteration
            if isinstance(agent, SettlerAgent):
                # Check for stress-induced bad behavior (slower transition)
                if not agent.is_bad and random.random() < (self.stress / 2000):  # Reduced to 0.05% per stress point
                    agent.is_bad = True
                    agent.revealed = False  # Starts as hidden (orange)
                    adjust_stress(self, 5, "Good actor turned bad due to stress")
                # Check for stress reduction from visiting hubs (triggered by touching hub)
                if agent.target_hub in ["Gym/Recreation", "Entertainment District"]:
                    hub_pos = HUBS[agent.target_hub]["pos"]
                    if abs(agent.pos[0] - hub_pos[0]) <= 20 and abs(agent.pos[1] - hub_pos[1]) <= 20 and random.random() < 0.1:
                        adjust_stress(self, -5, "Agent visited morale hub")
                # Check for incidents with weaker, isolated settlers
                if agent.is_bad and agent.revealed:
                    nearby_agents = [other for other in self.agents if isinstance(other, SettlerAgent) and other != agent and 
                                    abs(other.pos[0] - agent.pos[0]) < 50 and abs(other.pos[1] - agent.pos[1]) < 50]
                    if len(nearby_agents) < 2 and random.random() < 0.05:  # Reduced to 5% for slower population drop
                        self.civility -= 3  # Incident reduces civility
                        adjust_stress(self, 10, "Incident - Bad actor attacked isolated settler")
                        # Check for death from violent assault (reduced to 3%)
                        if random.random() < 0.03:
                            self.handle_death(agent, "Violent assault by bad actor")
                        # Trigger LEO chase (handled in LEAgent.step())

                # Check for death at Medical Bay (reduced to 0.3%)
                if agent.target_hub == "Medical Bay":
                    hub_pos = HUBS["Medical Bay"]["pos"]
                    if abs(agent.pos[0] - hub_pos[0]) <= 20 and abs(agent.pos[1] - hub_pos[1]) <= 20 and random.random() < 0.003:
                        self.handle_death(agent, "Medical complications")
                
                # Check for death at damaged hubs after adverse events (reduced to 1%)
                if self.step_count % self.steps_per_week < 5 and agent.target_hub in ["Power Plant", "Factory", "Mining Outpost"]:
                    hub_pos = HUBS[agent.target_hub]["pos"]
                    if abs(agent.pos[0] - hub_pos[0]) <= 20 and abs(agent.pos[1] - hub_pos[1]) <= 20 and random.random() < 0.01:
                        self.handle_death(agent, "Risky repair at damaged hub")

        # Apply prison upkeep cost and stress reduction
        prisoners = [a for a in self.agents if isinstance(a, PrisonAgent)]
        if prisoners:
            self.resources -= len(prisoners) * 2  # 2 resources per prisoner per step
            self.changes_log.append(f"Week {self.week}: Prison upkeep, -{len(prisoners) * 2} resources")

        # Decay stress slightly each step
        adjust_stress(self, -0.1, "Natural stress decay")
        # Update metrics
        self.update_metrics()

    def handle_death(self, agent, reason):
        if agent in self.living_agents:
            self.living_agents.remove(agent)
            self.agents.remove(agent)
            dead_agent = DeadAgent(self, agent)
            self.agents.add(dead_agent)
            self.morgue_count += 1  # Increment morgue counter
            adjust_stress(self, 15, f"Death due to {reason}")
            self.changes_log.append(f"Week {self.week}: Death - {reason}, Population now {len(self.living_agents)}, Morgue now {self.morgue_count}")

    def trigger_random_event(self):
        from src.events import trigger_random_event  # Import here to avoid circular imports
        if self.week % 2 == 0:  # Trigger events every other week for slower pace
            trigger_random_event(self)

    def reduce_stress_over_time(self):
        # Reduce stress if civility is high or no incidents recently
        if self.civility >= 70 and random.random() < 0.2:
            adjust_stress(self, -5, "High civility reduces stress")
        if len([log for log in self.changes_log[-10:] if "Incident" in log]) == 0 and self.week > 5 and random.random() < 0.1:
            adjust_stress(self, -10, "Long time without incidents reduces stress")

    def update_metrics(self):
        bad_actors = sum(1 for a in self.living_agents if isinstance(a, SettlerAgent) and a.is_bad and a.revealed)
        total_agents = len(self.living_agents)  # Include LEOs in population
        self.conflict_rate = bad_actors / total_agents if total_agents > 0 else 0