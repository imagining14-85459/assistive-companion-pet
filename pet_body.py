""" This file will focus on the movements and commands to control pet movement. """

import pygame

SPRITE_PATH = "test_rock.jpg"
class Pet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.x = x
        self.y = y
        self.size = 100
        self.speed = speed # pixels / frame
        self.image = pygame.transform.scale(pygame.image.load(SPRITE_PATH).convert_alpha(), (self.size, self.size))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

    def take_step(self, x, y):
        direction = pygame.math.Vector2(x-self.x, y-self.y).normalize()
        self.x += direction.x * self.speed
        self.y += direction.y * self.speed
        self.rect.center = (self.x,self.y)
