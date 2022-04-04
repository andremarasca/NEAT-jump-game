import pygame, csv, os

class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y, spritesheet):
        self.id = f"{x}_{y}"
        pygame.sprite.Sprite.__init__(self)
        self.image = spritesheet.get_sprite(image)
        # Manual load in: self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.show = True

    def draw(self, surface, camera):
        surface.blit(self.image, (self.rect.x - camera.offset.x, self.rect.y - camera.offset.y))

class TileMap():
    def __init__(self, filename, spritesheet):
        self.tile_size = spritesheet.w
        self.start_x, self.start_y = 0, 0
        self.max_x, self.max_y = 0, 0
        self.spritesheet = spritesheet
        self.tiles, self.coins = self.load_tiles(filename)

    def draw_map(self, surface, camera):
        for tile in self.tiles:
            tile.draw(surface, camera)
        # for coin in self.coins:
        #     if coin.show:
        #         coin.draw(surface, camera)
    
    def read_csv(self, filename):
        map = []
        with open(os.path.join(filename)) as data:
            data = csv.reader(data, delimiter=',')
            for row in data:
                map.append(list(row))
        return map

    def load_tiles(self, filename):
        tiles = []
        coins = []
        map = self.read_csv(filename)
        x, y = 0, 0
        for row in map:
            x = 0
            for tile in row:
                x_tile = x * self.tile_size
                y_tile = y * self.tile_size
                self.max_y = max(self.max_y, y_tile)
                self.max_x = max(self.max_x, x_tile)
                if tile == '0':
                    self.start_x, self.start_y = x_tile, y_tile
                elif tile == '1':
                    tiles.append(Tile('brick', x_tile, y_tile, self.spritesheet))
                elif tile == '2':
                    tiles.append(Tile('brick_yellow', x_tile, y_tile, self.spritesheet))
                elif tile == '3':
                    coins.append(Tile('coin', x_tile, y_tile, self.spritesheet))
                    # Move to next tile in current row
                x += 1

            # Move to next row
            y += 1
            # Store the size of the tile map
        self.map_w, self.map_h = x * self.tile_size, y * self.tile_size
        return tiles, coins

    def check_collidepoint(self, x: float, y: float):
        for tile in self.tiles:
            rect: pygame.rect.Rect = tile.rect
            if rect.collidepoint(x, y):
                return tile
        return None

    def reset_tile_map(self):
        for tile in self.coins:
            tile.show = True