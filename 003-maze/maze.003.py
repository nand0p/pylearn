import pygame
import sys

WIDTH = 640
HEIGHT = 480
SPRITE_WIDTH = 640
SPRITE_HEIGHT = 480

class GameObject:

    def __init__(self, image, height, speed):
        self.speed = speed
        self.image = image
        self.pos = image.get_rect().move(0, height)

    def move(self):
        self.pos = self.pos.move(self.speed, 0)
        if self.pos.right > 600:
            self.pos.left = 0

    def move(self, up=False, down=False, left=False, right=False):
      if right:
          self.pos.right += self.speed
      if left:
          self.pos.right -= self.speed
      if down:
          self.pos.top += self.speed
      if up:
          self.pos.top -= self.speed
      if self.pos.right > WIDTH:
          self.pos.left = 0
      if self.pos.top > HEIGHT-SPRITE_HEIGHT:
          self.pos.top = 0
      if self.pos.right < SPRITE_WIDTH:
          self.pos.right = WIDTH
      if self.pos.top < 0:
          self.pos.top = HEIGHT-SPRITE_HEIGHT


screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
player = pygame.image.load('images/hell.png').convert()
entity = pygame.image.load('images/player.png').convert()
background = pygame.image.load('images/block.png').convert()
screen.blit(background, (0, 0))

objects = []

p = GameObject(player, 10, 3)

for x in range(10):
    o = GameObject(entity, x*40, x)
    objects.append(o)

while True:

    screen.blit(background, p.pos, p.pos)

    for o in objects:
        screen.blit(background, o.pos, o.pos)

    keys = pygame.key.get_pressed()

    if keys[pygame.K_UP]:
        p.move(up=True)

    if keys[pygame.K_DOWN]:
        p.move(down=True)

    if keys[pygame.K_LEFT]:
        p.move(left=True)

    if keys[pygame.K_RIGHT]:
        p.move(right=True)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.blit(p.image, p.pos)

    for o in objects:
        o.move()
        screen.blit(o.image, o.pos)

    pygame.display.update()
    clock.tick(60)
