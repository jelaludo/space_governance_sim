import pygame
from src.model import GovernanceModel, SettlerAgent, PrisonAgent, LEAgent, DeadAgent

pygame.init()
screen = pygame.display.set_mode((800, 600))  # Bigger for dashboard and glossary
pygame.display.set_caption("Space Governance Sim V3.7")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 20)  # Slightly smaller font for dashboard to fit better
small_font = pygame.font.Font(None, 14)  # Smaller font for hub labels, counters, and glossary
tiny_font = pygame.font.Font(None, 12)  # Even smaller font for change log

# Hub definitions (import from hubs.py, but keep increased spacing)
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

def draw(model):
    screen.fill((0, 0, 0))
    # Draw glossary on the left with icons (corrected colors)
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
        screen.blit(rendered, (50, 10 + i * 18))  # Tighter spacing for smaller font

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

    # Draw agents with animation (fixed position unpacking)
    for agent in model.agents:
        if isinstance(agent, SettlerAgent):
            color = (255, 0, 0) if agent.is_bad and agent.revealed else (255, 165, 0) if agent.is_bad else (128, 128, 128)
            # Clamp position to stay within 800x600, adjust for glossary and spacing
            x = max(225, min(775, agent.pos[0]))  # X coordinate
            y = max(25, min(575, agent.pos[1]))   # Y coordinate
            if agent.gender == "M":
                pygame.draw.rect(screen, color, (x - 5, y - 5, 10, 10))  # Square for male
            else:
                pygame.draw.circle(screen, color, (x, y), 5)  # Dot for female
        elif isinstance(agent, LEAgent):
            color = (255, 0, 128) if agent.is_bad else (0, 0, 255)  # Purple for corrupt, blue for good
            x = max(225, min(775, agent.pos[0]))  # X coordinate
            y = max(25, min(575, agent.pos[1]))   # Y coordinate
            if agent.gender == "M":
                pygame.draw.rect(screen, color, (x - 5, y - 5, 10, 10))  # Square for male LEO
            else:
                pygame.draw.circle(screen, color, (x, y), 5)  # Dot for female LEO
        elif isinstance(agent, PrisonAgent):
            x = max(225, min(775, agent.pos[0]))  # X coordinate
            y = max(25, min(575, agent.pos[1]))   # Y coordinate
            color = (255, 0, 0) if agent.is_bad else (128, 128, 128)  # Red for bad, grey for others
            if agent.original_gender == "M":
                pygame.draw.rect(screen, color, (x - 5, y - 5, 10, 10), 2)  # Outline square for male prisoners
            else:
                pygame.draw.circle(screen, color, (x, y), 5, 2)  # Outline dot for female prisoners
        elif isinstance(agent, DeadAgent):
            x = max(225, min(775, agent.pos[0]))  # X coordinate
            y = max(25, min(575, agent.pos[1]))   # Y coordinate
            pygame.draw.circle(screen, (100, 100, 100), (x, y), 5, 2)  # Dark grey outline dot for dead

    # Dashboard (top area, remove Morgue and Prison counters, smaller font)
    pygame.draw.rect(screen, (50, 50, 50), (0, 0, 800, 80))  # Slightly smaller dashboard for better fit
    metrics = [
        f"Day: {model.week}",
        f"Civility: {model.civility}",
        f"Resources: {model.resources}",
        f"Conflict: {model.conflict_rate:.2f}",
        f"Stress: {model.stress:.0f}",
        f"Pop: {len(model.living_agents)}"
    ]
    for i, text in enumerate(metrics):
        rendered = font.render(text, True, (255, 255, 255))
        screen.blit(rendered, (210, 10 + i * 16))  # Tighter spacing for smaller font, shift right to avoid glossary

    # Change log (scrolling text, even smaller font, repositioned)
    changes = model.changes_log[-5:]  # Show last 5 changes
    pygame.draw.rect(screen, (50, 50, 50), (400, 80, 400, 100))  # Adjusted change log area
    for i, text in enumerate(changes):
        rendered = tiny_font.render(text, True, (255, 255, 255))
        screen.blit(rendered, (410, 90 + i * 12))  # Tighter, smaller spacing

    # Civility gauge (bottom, repositioned)
    pygame.draw.rect(screen, (0, 255, 0) if model.civility > 50 else (255, 0, 0), (210, 570, model.civility * 4, 10))  # Shifted down, right

    # Draw manual and auto buttons (improved visibility, dynamic colors)
    manual_color = (0, 255, 0) if model.is_manual else (150, 150, 150)  # Green if active, grey if inactive
    auto_color = (150, 150, 150) if model.is_manual else (0, 255, 0)  # Grey if manual active, green if auto active
    pygame.draw.rect(screen, manual_color, (700, 10, 80, 30))  # "Manual" button
    rendered = font.render("Manual", True, (0, 0, 0))  # Black text for contrast
    screen.blit(rendered, (720, 15))  # Center text in manual button

    pygame.draw.rect(screen, auto_color, (700, 50, 80, 30))  # "Auto" button
    rendered = font.render("Auto", True, (0, 0, 0))  # Black text for contrast
    screen.blit(rendered, (720, 55))  # Center text in auto button

    pygame.display.flip()

def run():
    model = GovernanceModel()
    running = True
    auto_timer = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                if 700 <= event.pos[0] <= 780 and 10 <= event.pos[1] <= 40:  # Click on manual button
                    model.is_manual = True  # Switch to manual mode, stopping auto
                    if not model.is_animating:
                        model.step()  # Trigger next turn in manual mode
                elif 700 <= event.pos[0] <= 780 and 50 <= event.pos[1] <= 80:  # Click on auto button
                    model.is_manual = False  # Switch to auto mode

        if not model.is_manual and not model.is_animating:  # Auto mode simulates manual clicks at 1 click/second
            auto_timer += clock.get_rawtime() / 1000  # Convert milliseconds to seconds
            if auto_timer >= 0.01:  # Advance one day every second in auto mode (simulating a manual click)
                model.step()
                auto_timer = 0

        # Handle animation if in progress
        if model.is_animating:
            model.animate_step()

        draw(model)
        clock.tick(30)  # 30 FPS
    pygame.quit()

if __name__ == "__main__":
    run()