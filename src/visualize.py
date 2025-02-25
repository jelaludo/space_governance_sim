import pygame
from src.model import GovernanceModel, SettlerAgent, PrisonAgent, LEAgent, DeadAgent

pygame.init()
screen = pygame.display.set_mode((800, 600))  # Bigger for dashboard and glossary
pygame.display.set_caption("Space Governance Sim V3.0")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)  # Regular font for dashboard
small_font = pygame.font.Font(None, 16)  # Smaller font for hub labels and counters
tiny_font = pygame.font.Font(None, 14)  # Tiny font for change log

# Hub definitions (import from hubs.py, but include here for completeness)
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

def draw(model):
    screen.fill((0, 0, 0))
    # Draw glossary on the left with icons
    glossary = [
        ("Neutral Settler (M)", (128, 128, 128), pygame.Rect(10, 10, 10, 10)),  # Grey square (male)
        ("Neutral Settler (F)", (128, 128, 128), (30, 15, 10, 0)),  # Grey dot (female, circle)
        ("Hidden Bad Actor (M)", (255, 165, 0), pygame.Rect(10, 30, 10, 10)),  # Orange square (male)
        ("Hidden Bad Actor (F)", (255, 165, 0), (30, 35, 10, 0)),  # Orange dot (female, circle)
        ("Revealed Bad Actor (M)", (255, 0, 0), pygame.Rect(10, 50, 10, 10)),  # Red square (male)
        ("Revealed Bad Actor (F)", (255, 0, 0), (30, 55, 10, 0)),  # Red dot (female, circle)
        ("Good Law Enforcement (M)", (0, 0, 255), pygame.Rect(10, 70, 10, 10)),  # Blue square (male LEO)
        ("Good Law Enforcement (F)", (0, 0, 255), (30, 75, 10, 0)),  # Blue dot (female LEO)
        ("Corrupt Law Enforcement", (255, 0, 128), (30, 95, 10, 0)),  # Purple dot (corrupt LEO, circle)
        ("Dead Agent", (100, 100, 100), (30, 115, 10, 0))  # Dark grey dot (dead, circle)
    ]
    pygame.draw.rect(screen, (50, 50, 50), (0, 0, 200, 600))  # Grey background for glossary
    for i, (text, color, shape) in enumerate(glossary):
        if isinstance(shape, pygame.Rect):  # Square for male agents
            pygame.draw.rect(screen, color, (shape.x, shape.y, 10, 10))
        else:  # Circle for female agents and others
            pygame.draw.circle(screen, color, (shape[0], shape[1]), 5)
        rendered = small_font.render(text, True, (255, 255, 255))
        screen.blit(rendered, (50, 10 + i * 20))  # Text next to icon

    # Draw hubs with colors based on risk and counters
    for hub_name, hub in HUBS.items():
        risk = hub["risk"]
        color = (0, 255, 0) if risk < 0.3 else (255, 255, 0) if risk < 0.6 else (255, 0, 0)
        pygame.draw.circle(screen, color, hub["pos"], 20, 1)
        # Label hubs above with smaller font
        rendered = small_font.render(hub_name, True, (255, 255, 255))
        screen.blit(rendered, (hub["pos"][0] - rendered.get_width() // 2, hub["pos"][1] - 25))
        # Display counters inside Prison Hub and Morgue
        if hub_name == "Prison Hub":
            counter_text = f"Prison: {model.prison_count}"
            counter_rendered = small_font.render(counter_text, True, (255, 255, 255))
            screen.blit(counter_rendered, (hub["pos"][0] - counter_rendered.get_width() // 2, hub["pos"][1] - 5))
        elif hub_name == "Morgue":
            counter_text = f"Morgue: {model.morgue_count}"
            counter_rendered = small_font.render(counter_text, True, (255, 255, 255))
            screen.blit(counter_rendered, (hub["pos"][0] - counter_rendered.get_width() // 2, hub["pos"][1] - 5))

    # Draw agents
    for agent in model.agents:
        if isinstance(agent, SettlerAgent):
            color = (255, 0, 0) if agent.is_bad and agent.revealed else (255, 165, 0) if agent.is_bad else (128, 128, 128)
            # Clamp position to stay within 800x600, adjust for glossary
            x, y = max(205, min(795, agent.pos[0])), max(5, min(595, agent.pos[1]))  # Shift right to avoid glossary
            if agent.gender == "M":
                pygame.draw.rect(screen, color, (x - 5, y - 5, 10, 10))  # Square for male
            else:
                pygame.draw.circle(screen, color, (x, y), 5)  # Dot for female
        elif isinstance(agent, LEAgent):
            color = (255, 0, 128) if agent.is_bad else (0, 0, 255)  # Purple for corrupt, blue for good
            x, y = max(205, min(795, agent.pos[0])), max(5, min(595, agent.pos[1]))  # Shift right to avoid glossary
            if agent.gender == "M":
                pygame.draw.rect(screen, color, (x - 5, y - 5, 10, 10))  # Square for male LEO
            else:
                pygame.draw.circle(screen, color, (x, y), 5)  # Dot for female LEO
        elif isinstance(agent, PrisonAgent):
            x, y = max(205, min(795, agent.pos[0])), max(5, min(595, agent.pos[1]))  # Shift right to avoid glossary
            color = (255, 0, 0) if agent.is_bad else (128, 128, 128)  # Red for bad, grey for others
            if agent.original_gender == "M":
                pygame.draw.rect(screen, color, (x - 5, y - 5, 10, 10), 2)  # Outline square for male prisoners
            else:
                pygame.draw.circle(screen, color, (x, y), 5, 2)  # Outline dot for female prisoners
        elif isinstance(agent, DeadAgent):
            x, y = max(205, min(795, agent.pos[0])), max(5, min(595, agent.pos[1]))  # Shift right to avoid glossary
            pygame.draw.circle(screen, (100, 100, 100), (x, y), 5, 2)  # Dark grey outline dot for dead

    # Dashboard (top area, remove Morgue and Prison counters)
    pygame.draw.rect(screen, (50, 50, 50), (0, 0, 800, 100))  # Grey dashboard background
    metrics = [
        f"Week: {model.week}",
        f"Civility: {model.civility}",
        f"Resources: {model.resources}",
        f"Conflict Rate: {model.conflict_rate:.2f}",
        f"Stress: {model.stress:.0f}",
        f"Population: {len(model.living_agents)}"
    ]
    for i, text in enumerate(metrics):
        rendered = font.render(text, True, (255, 255, 255))
        screen.blit(rendered, (210, 10 + i * 20))  # Shift right to avoid glossary

    # Change log (scrolling text, smaller font)
    changes = model.changes_log[-5:]  # Show last 5 changes
    for i, text in enumerate(changes):
        rendered = tiny_font.render(text, True, (255, 255, 255))
        screen.blit(rendered, (400, 10 + i * 15))  # Tighter spacing for smaller text

    # Civility gauge (bottom)
    pygame.draw.rect(screen, (0, 255, 0) if model.civility > 50 else (255, 0, 0), (210, 550, model.civility * 4, 10))  # Shift right to avoid glossary
    pygame.display.flip()

def run():
    model = GovernanceModel()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        model.step()
        draw(model)
        clock.tick(30)  # 30 FPS
    pygame.quit()

if __name__ == "__main__":
    run()