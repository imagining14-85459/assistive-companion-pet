""" This file will focus on the movements and commands to control pet movement. """

import pygame
import random

SPRITE_PATH = "assets/pet/cat_sprites.png"
HATS = {"Top Hat":"assets/hats/tophat_cat_sprites.png", "Monocle":"assets/hats/monocle_cat_sprites.png",
        "Crown":"assets/hats/crown_cat_sprites.png", "Sunglasses":"assets/hats/sunglasses_cat_sprites.png"}
FACEWEAR = ["Monocle", "Sunglasses"]

class Pet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, hat:str=None):
        super().__init__()
        self.x = x
        self.y = y
        self.state = "stay" #stay, wonder, follow, attack, carried
        self.shown = True
        self.size = 280

        self.speed = speed # pixels / frame
        self.held_down = False # bool on if the mouse is holding the pet
        self.frame = 0
        self.animation_id = 3

        self.hat = None
        self.curr_path = SPRITE_PATH
        self.update_hat(hat)

        self.sprite_sheet = pygame.image.load(self.curr_path).convert_alpha()
        self.image = self._get_image()
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

    def update_hat(self, hat:str):
        self.hat = hat
        if not hat: self.curr_path = SPRITE_PATH
        else: self.curr_path = HATS[hat]
        self.sprite_sheet = pygame.image.load(self.curr_path).convert_alpha()

    def collide(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos[0], pos[1])

    def take_step(self, x, y):
        direction = pygame.math.Vector2(x-self.x, y-self.y).normalize()
        self.x += direction.x * self.speed
        self.y += direction.y * self.speed
        self.update_rect()

    def change_state(self, state):
        self.state = state
        self.frame = 0
        match self.state:
            case "stay":
                self.animation_id = random.choice([0,1,2,3,6])
            case "follow" | "wander":
                self.animation_id = random.choice([4,5])
            case "attack":
                self.animation_id = random.choice([7,8])
            case "carried":
                self.animation_id = 9

    def update_rect(self):
        self.rect.center = (self.x, self.y)

    def animation_tick(self): #idle (0-2, 5: 4); walk (3,4: 8); harrass (6:6) harassed (7,8: 7,8)
        self.frame += 1
        match self.state:
            case "stay":
                self.frame %= 4
            case "follow" | "wander":
                self.frame %= 8
            case "attack":
                self.frame %= 6
            case "carried":
                self.frame %= 7
        self.image = self._get_image()

    def _get_image(self):
        image = pygame.Surface((32, 32)).convert_alpha()
        image.blit(self.sprite_sheet, (0, 0), ((self.frame * 32), (self.animation_id*32), 32, 32))
        image = pygame.transform.scale(image, (self.size, self.size))
        image.set_colorkey((0, 0, 0)) # Remove background color if needed
        return image
