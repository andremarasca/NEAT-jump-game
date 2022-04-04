import pygame
import json

class Spritesheet:
    def __init__(self, filename, h, w):
        self.h = h
        self.w = w
        self.filename = filename
        self.sprite_sheet = pygame.image.load(filename).convert_alpha()
        self.n_sprites = int(self.sprite_sheet.get_height() / h)
        self.split_spritesheet()

    def split_spritesheet(self):
        self.sprites = []
        for i in range(self.n_sprites):
            img = self.sprite_sheet.subsurface((0, self.h*i), (self.w, self.h))
            self.sprites.append(img)

    def get_sprite(self, name):
        if name == 'brick':
            return self.sprites[1]
        if name == 'brick_yellow':
            return self.sprites[2]
        if name == 'player':
            return self.sprites[0]
        if name == 'coin':
            return self.sprites[3]
        print(f"SPRITE {name} NAO EXISTE!")
        return self.sprites[0]