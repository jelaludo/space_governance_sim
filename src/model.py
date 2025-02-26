import pygame  # Added to fix NameError
from mesa import Agent, Model
import random
from src.hubs import HUBS
from src.events import trigger_random_event
from src.stressors import adjust_stress, STRESS_EVENTS
from src.crimes import select_crime, apply_crime_impact

class SettlerAgent(Agent):
    def __init__(self, model, gender, is_bad=False):
        super().__init__(model)
        self.gender = gender  # "M" for men (squares), "F" for women (circles/dots)
        self.is_bad = is_bad  # Bad actor flag
        self.revealed = False if is_bad else True  # Hidden bad actors
        self.pos = HUBS[random.choice(list(HUBS.keys()))]["pos"]  # Start at a random hub
        self.target_hub = None  # Will be set each turn
        self.start_pos = None  # Starting position for animation
        self.animation_frames = 30  # Number of frames for animation (1 second at 30 FPS)
        self.animation_frame = 0  # Current animation frame
        self.power = sum(random.randint(1, 6) for _ in range(3))  # 3d6 roll (3-18)

    def step(self, animate=False):
        if not animate:  # Initialize movement for next turn
            if self.target_hub is None or random.random() < 0.1:  # 10% chance to stay at current hub
                # Choose new target hub with bias toward Housing District
                if self.is_bad and self.revealed:
                    hubs = ["Housing District", "Entertainment District", "Power Plant", "Mining Outpost", "Prison Hub"]
                    weights = [0.3, 0.2, 0.2, 0.2, 0.1]  # Bias toward Housing, less to Prison
                else:
                    hubs = ["Housing District", "Farming Module", "Factory", "Water Treatment", "Command Center", 
                            "Gym/Recreation", "Medical Bay", "Entertainment District", "Power Plant", "Research Lab", 
                            "Mining Outpost"]
                    weights = [0.5, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05, 0.05, 0.05]  # Strong bias toward Housing
                self.target_hub = random.choices(hubs, weights=weights, k=1)[0]
            self.start_pos = self.pos
            self.animation_frame = 0
            # Check for crime if bad actor and revealed
            if self.is_bad and self.revealed:
                nearby_agents = [other for other in self.model.agents if isinstance(other, SettlerAgent) and other != self and 
                                abs(other.pos[0] - self.pos[0]) < 50 and abs(other.pos[1] - self.pos[1]) < 50]
                nearby_leas = [other for other in self.model.agents if isinstance(other, LEAgent) and 
                              abs(other.pos[0] - self.pos[0]) < 50 and abs(other.pos[1] - self.pos[1]) < 50]
                if nearby_agents and not nearby_leas:  # Weaker people present, no LEAs nearby
                    weaker_agents = [agent for agent in nearby_agents if agent.power < self.power]
                    if weaker_agents and random.random() < 0.1:  # 10% chance to commit a crime if conditions met
                        crime_name, crime_data = select_crime()
                        apply_crime_impact(self.model, crime_name, crime_data)
                        # Optionally handle victim or other effects (e.g., death for murder)
                        if crime_name == "Murder/Nonnegligent Manslaughter":
                            victim = random.choice(weaker_agents)
                            self.model.handle_death(victim, "Murder by bad actor")
        else:  # Animate movement
            if self.animation_frame < self.animation_frames:
                start_x, start_y = self.start_pos
                hub_pos = HUBS[self.target_hub]["pos"]
                target_x, target_y = hub_pos
                progress = self.animation_frame / self.animation_frames
                new_x = start_x + (target_x - start_x) * progress
                new_y = start_y + (target_y - start_y) * progress
                # Clamp to stay on-screen, with more spacing
                self.pos = (max(25, min(775, new_x)), max(25, min(575, new_y)))  # Increased margins for spacing
                self.animation_frame += 1
            else:
                # Complete movement and trigger stat changes
                hub_pos = HUBS[self.target_hub]["pos"]
                target_x, target_y = hub_pos
                self.pos = (max(25, min(775, target_x)), max(25, min(575, target_y)))  # Ensure exact hub position
                # Check if agent "touches" the target hub (within 20 pixels) to trigger stat changes
                if abs(self.pos[0] - target_x) <= 20 and abs(self.pos[1] - target_y) <= 20:
                    if self.target_hub in ["Farming Module", "Factory", "Water Treatment", "Command Center"]:
                        self.model.resources = min(200, self.model.resources + random.randint(1, 3))  # Cap resources at 200, increase by 1-3
                    elif self.target_hub in ["Gym/Recreation", "Entertainment District"]:
                        self.reduce_stress()

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
        self.target_hub = "Prison Hub"  # Stay at prison
        self.start_pos = None  # Starting position for animation
        self.animation_frames = 30  # Number of frames for animation (1 second at 30 FPS)
        self.animation_frame = 0  # Current animation frame
        self.power = original_agent.power  # Retain original power

    def step(self, animate=False):
        if not animate:  # Initialize movement for next turn
            if random.random() < 0.1:  # 10% chance to stay, otherwise move within prison
                self.target_hub = "Prison Hub"
            self.start_pos = self.pos
            self.animation_frame = 0
        else:  # Animate movement
            if self.animation_frame < self.animation_frames:
                start_x, start_y = self.start_pos
                hub_pos = HUBS[self.target_hub]["pos"]
                target_x, target_y = hub_pos
                progress = self.animation_frame / self.animation_frames
                new_x = start_x + (target_x - start_x) * progress
                new_y = start_y + (target_y - start_y) * progress
                # Clamp to stay on-screen, with more spacing
                self.pos = (max(25, min(775, new_x)), max(25, min(575, new_y)))  # Increased margins for spacing
                self.animation_frame += 1
            else:
                # Complete movement
                hub_pos = HUBS[self.target_hub]["pos"]
                target_x, target_y = hub_pos
                self.pos = (max(25, min(775, target_x)), max(25, min(575, target_y)))  # Ensure exact hub position

class DeadAgent(Agent):
    def __init__(self, model, original_agent):
        super().__init__(model)
        self.pos = HUBS["Morgue"]["pos"]  # Morgue hub position (moved further away)
        self.is_dead = True
        self.original_gender = original_agent.gender  # Store original gender for visualization
        self.target_hub = "Morgue"  # Stay at morgue
        self.start_pos = None  # Starting position for animation
        self.animation_frames = 30  # Number of frames for animation (1 second at 30 FPS)
        self.animation_frame = 0  # Current animation frame
        self.power = original_agent.power  # Retain original power

    def step(self, animate=False):
        if not animate:  # Initialize movement for next turn
            if random.random() < 0.1:  # 10% chance to stay, otherwise move within morgue
                self.target_hub = "Morgue"
            self.start_pos = self.pos
            self.animation_frame = 0
        else:  # Animate movement
            if self.animation_frame < self.animation_frames:
                start_x, start_y = self.start_pos
                hub_pos = HUBS[self.target_hub]["pos"]
                target_x, target_y = hub_pos
                progress = self.animation_frame / self.animation_frames
                new_x = start_x + (target_x - start_x) * progress
                new_y = start_y + (target_y - start_y) * progress
                # Clamp to stay on-screen, with more spacing
                self.pos = (max(25, min(775, new_x)), max(25, min(575, new_y)))  # Increased margins for spacing
                self.animation_frame += 1
            else:
                # Complete movement
                hub_pos = HUBS[self.target_hub]["pos"]
                target_x, target_y = hub_pos
                self.pos = (max(25, min(775, target_x)), max(25, min(575, target_y)))  # Ensure exact hub position

class LEAgent(Agent):
    def __init__(self, model, is_bad=False):
        super().__init__(model)
        self.is_bad = is_bad  # Corrupt LEO chance (e.g., 5%)
        self.gender = "M" if random.random() < 0.9 else "F"  # 90% male, 10% female for LEOs
        self.pos = HUBS[random.choice(list(HUBS.keys()))]["pos"]  # Start at a random hub
        self.patrol_index = 0  # Track current patrol hub
        self.chasing = None  # Track if chasing a bad actor
        self.start_pos = None  # Starting position for animation
        self.animation_frames = 30  # Number of frames for animation (1 second at 30 FPS)
        self.animation_frame = 0  # Current animation frame
        self.power = sum(random.randint(1, 6) for _ in range(3))  # 3d6 roll (3-18)

    def step(self, animate=False):
        if not animate:  # Initialize movement for next turn
            if self.chasing:
                # Find the bad actor to chase
                for agent in self.model.agents:
                    if agent == self.chasing:
                        self.target_hub = None  # Chase directly to bad actor
                        break
            else:
                # Systematic patrol of all hubs in fixed order, no randomness
                hubs = list(HUBS.keys())
                self.patrol_index = (self.patrol_index + 1) % len(hubs)  # Always systematic, no randomness
                self.target_hub = hubs[self.patrol_index]
            self.start_pos = self.pos
            self.animation_frame = 0
        else:  # Animate movement
            if self.animation_frame < self.animation_frames:
                if self.chasing:
                    # Animate chase to bad actor
                    bad_actor_pos = self.chasing.pos
                    start_x, start_y = self.start_pos
                    target_x, target_y = bad_actor_pos
                else:
                    # Animate patrol to target hub
                    hub_pos = HUBS[self.target_hub]["pos"]
                    start_x, start_y = self.start_pos
                    target_x, target_y = hub_pos
                progress = self.animation_frame / self.animation_frames
                new_x = start_x + (target_x - start_x) * progress
                new_y = start_y + (target_y - start_y) * progress
                # Clamp to stay on-screen, with more spacing
                self.pos = (max(25, min(775, new_x)), max(25, min(575, new_y)))  # Increased margins for spacing
                self.animation_frame += 1
            else:
                # Complete movement and handle chase logic
                if self.chasing:
                    bad_actor_pos = self.chasing.pos
                    target_x, target_y = bad_actor_pos
                    self.pos = (max(25, min(775, target_x)), max(25, min(575, target_y)))  # Ensure exact bad actor position
                    # Check if close enough to escort to prison
                    if abs(self.pos[0] - bad_actor_pos[0]) < 10 and abs(self.pos[1] - bad_actor_pos[1]) < 10:
                        self.model.agents.remove(self.chasing)
                        prisoner = PrisonAgent(self.model, self.chasing)
                        self.model.agents.add(prisoner)
                        self.model.resources -= 5  # Resource cost for prison
                        self.model.civility = max(0, self.model.civility - 2)  # Slight civility drop
                        adjust_stress(self.model, -10, "Bad actor imprisoned, reducing stress for good actors")  # Stress reduction
                        self.model.prison_count += 1  # Increment prison counter
                        self.model.changes_log.append(f"Day {self.model.week}: Bad actor imprisoned by LEO, -5 resources, -10 stress, Prison now {self.model.prison_count}")
                        self.chasing = None  # Stop chasing
                else:
                    hub_pos = HUBS[self.target_hub]["pos"]
                    target_x, target_y = hub_pos
                    self.pos = (max(25, min(775, target_x)), max(25, min(575, target_y)))  # Ensure exact hub position
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
        self.week = 0  # Now represents days in turn-based system
        self.is_manual = True  # Start in manual mode
        self.is_animating = False  # Track if animation is in progress
        self.animation_frame = 0  # Current animation frame
        self.steps_per_day = 1  # One step per day
        self.step_count = 0
        self.conflict_rate = 0
        self.changes_log = []  # Log of key changes
        self.stress = 0  # New stress metric (0-100)
        self.morgue_count = 0  # Counter for dead agents in Morgue
        self.prison_count = 0  # Counter for imprisoned agents in Prison

        # Update HUBS to include Morgue (moved further away)
        HUBS["Morgue"] = {"pos": (750, 350), "risk": 0.1, "purpose": "absorbing"}  # Far right, near center, moved right 50

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
        if (self.is_manual and not self.is_animating and pygame.mouse.get_pressed()[0]) or (not self.is_manual and not self.is_animating):  # Manual click or auto mode
            self.is_animating = True
            self.animation_frame = 0
            # Initialize movement for all agents
            for agent in self.agents:
                agent.step(animate=False)

    def animate_step(self):
        if self.is_animating:
            self.animation_frame += 1
            if self.animation_frame >= 30:  # Animation complete after 30 frames (1 second at 30 FPS)
                self.is_animating = False
                self.week += 1  # Advance one day
                self.step_count += 1
                if self.week % 7 == 0:  # Trigger a random event every 7 days (weekly)
                    self.trigger_random_event()
                self.reduce_stress_over_time()  # Reduce stress based on conditions
                self.changes_log.append(f"Day {self.week}: Civility {self.civility}, Resources {self.resources}, Stress {self.stress}, Population {len(self.living_agents)}, Morgue {self.morgue_count}, Prison {self.prison_count}")

                # Complete movement and handle effects
                for agent in list(self.agents):  # Use list to modify agents during iteration
                    agent.step(animate=True)
                    if isinstance(agent, SettlerAgent):
                        # Check for stress-induced bad behavior (slower transition)
                        if not agent.is_bad and random.random() < (self.stress / 2000):  # Reduced to 0.05% per stress point
                            agent.is_bad = True
                            agent.revealed = False  # Starts as hidden (orange)
                            adjust_stress(self, 5, "Good actor turned bad due to stress")
                        # Check for death at Medical Bay (reduced to 0.3%)
                        if agent.target_hub == "Medical Bay":
                            hub_pos = HUBS["Medical Bay"]["pos"]
                            if abs(agent.pos[0] - hub_pos[0]) <= 20 and abs(agent.pos[1] - hub_pos[1]) <= 20 and random.random() < 0.003:
                                self.handle_death(agent, "Medical complications")
                        # Check for death at damaged hubs after adverse events (reduced to 1%)
                        if self.week % 7 < 1 and agent.target_hub in ["Power Plant", "Factory", "Mining Outpost"]:  # Check first day of week
                            hub_pos = HUBS[agent.target_hub]["pos"]
                            if abs(agent.pos[0] - hub_pos[0]) <= 20 and abs(agent.pos[1] - hub_pos[1]) <= 20 and random.random() < 0.01:
                                self.handle_death(agent, "Risky repair at damaged hub")
                        # Check for incidents with weaker, isolated settlers (handled in crimes.py now)

                # Apply prison upkeep cost and stress reduction
                prisoners = [a for a in self.agents if isinstance(a, PrisonAgent)]
                if prisoners:
                    self.resources -= len(prisoners) * 2  # 2 resources per prisoner per day
                    self.changes_log.append(f"Day {self.week}: Prison upkeep, -{len(prisoners) * 2} resources")

                # Decay stress slightly each day
                adjust_stress(self, -0.1, "Natural stress decay")
                # Update metrics
                self.update_metrics()
            else:
                # Animate all agents
                for agent in self.agents:
                    agent.step(animate=True)

    def handle_death(self, agent, reason):
        if agent in self.living_agents:
            self.living_agents.remove(agent)
            self.agents.remove(agent)
            dead_agent = DeadAgent(self, agent)
            self.agents.add(dead_agent)
            self.morgue_count += 1  # Increment morgue counter
            adjust_stress(self, 15, f"Death due to {reason}")
            self.changes_log.append(f"Day {self.week}: Death - {reason}, Population now {len(self.living_agents)}, Morgue now {self.morgue_count}")

    def trigger_random_event(self):
        from src.events import trigger_random_event  # Import here to avoid circular imports
        trigger_random_event(self)

    def reduce_stress_over_time(self):
        # Reduce stress if civility is high or no incidents recently
        if self.civility >= 70 and random.random() < 0.2:
            adjust_stress(self, -5, "High civility reduces stress")
        if len([log for log in self.changes_log[-7:] if "Incident" in log]) == 0 and self.week > 7 and random.random() < 0.1:  # Check last week
            adjust_stress(self, -10, "Long time without incidents reduces stress")

    def update_metrics(self):
        bad_actors = sum(1 for a in self.living_agents if isinstance(a, SettlerAgent) and a.is_bad and a.revealed)
        total_agents = len(self.living_agents)  # Include LEOs in population
        self.conflict_rate = bad_actors / total_agents if total_agents > 0 else 0