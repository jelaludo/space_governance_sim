import pygame
from src.model import GovernanceModel

pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Space Governance Sim V1")
clock = pygame.time.Clock()

def draw(model):
    screen.fill((0, 0, 0))  # Black background
    # Draw hubs
    hub_positions = [(100, 100), (300, 200), (500, 300)]
    for hub in hub_positions:
        pygame.draw.circle(screen, (255, 255, 255), hub, 20, 1)

    # Draw agents (updated to use model.agents)
    for agent in model.agents:  # Changed from model.schedule.agents
        color = (255, 0, 0) if agent.is_bad and agent.revealed else (255, 165, 0) if agent.is_bad else (128, 128, 128)
        if agent.gender == "M":
            pygame.draw.rect(screen, color, (agent.pos[0] - 5, agent.pos[1] - 5, 10, 10))
        else:
            pygame.draw.circle(screen, color, agent.pos, 5)
    
    # Civility gauge
    pygame.draw.rect(screen, (0, 255, 0) if model.civility > 50 else (255, 0, 0), (10, 10, model.civility, 10))
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