import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player = pygame.image.load("player.png").convert()
    background = pygame.image.load('block.png').convert()
    screen.fill("purple")
    screen.blit(background, (0, 0)) 

    pygame.draw.circle(screen, "red", player_pos, 40)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_j]:
        player_pos.y -= 300 * dt
    if keys[pygame.K_k]:
        player_pos.y += 300 * dt
    if keys[pygame.K_h]:
        player_pos.x -= 300 * dt
    if keys[pygame.K_l]:
        player_pos.x += 300 * dt

        #display.fill((0,0,0))
        #display.blit(display,)
        #self.maze.draw(display, block)
        pygame.display.flip()


    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
