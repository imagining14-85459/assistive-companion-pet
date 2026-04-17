""" This file will focus on the movements and commands to control pet movement. """

import pygame

SPRITE_PATH = "test_rock.jpg"
HATS = {"top_hat":"top_hat.jpg"}
class Hat(pygame.sprite.Sprite):
    def __init__(self, x, y, hat):
        super().__init__()
        self.x = x
        self.size = 50
        self.y = y + self.size
        self.image = pygame.transform.scale(pygame.image.load(HATS[hat]).convert_alpha(), (self.size, self.size))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

    def update_rect(self):
        self.rect.center = (self.x, self.y)

class Pet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, hat:str=None):
        super().__init__()
        self.x = x
        self.y = y
        self.size = 100
        self.speed = speed # pixels / frame
        if hat: self.hat = Hat(x, y, hat)
        self.image = pygame.transform.scale(pygame.image.load(SPRITE_PATH).convert_alpha(), (self.size, self.size))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

    def take_step(self, x, y):
        direction = pygame.math.Vector2(x-self.x, y-self.y).normalize()
        self.x += direction.x * self.speed
        self.y += direction.y * self.speed
        self.update_rect()

    def update_rect(self):
        self.rect.center = (self.x, self.y)
        if self.hat:
            self.hat.x = self.x
            self.hat.y = self.y-self.hat.size
            self.hat.update_rect()
