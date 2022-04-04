import pygame
from math import sin, cos, pi, copysign, sqrt

sind = lambda x: sin(x * pi / 180)
cosd = lambda x: cos(x * pi / 180)

class Player(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, spritesheet):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.SysFont('arial', 10, True, False)
        self.LEFT_KEY, self.RIGHT_KEY, self.FACING_LEFT = False, False, False
        self.is_dead = False
        self.gravity, self.acceleration_x,  self.friction = .35, .35, -.12
        self.image = spritesheet.get_sprite('player')
        self.rect = self.image.get_rect()
        self.start_position = pygame.math.Vector2(0, 0)
        self.position = pygame.math.Vector2(0, 0)
        self.velocity = pygame.math.Vector2(0,0)
        self.acceleration = pygame.math.Vector2(0, self.gravity)
        self.reset_player(start_x, start_y)

    def reset_player(self, start_x, start_y):
        self.start_position.x, self.start_position.y = start_x, start_y
        self.position.x, self.position.y = self.start_position.x, self.start_position.y
        self.rect.x, self.rect.y = self.start_position.x, self.start_position.y
        self.velocity.x, self.velocity.y = 0, 0
        self.acceleration.x = 0
        self.min_y_on_ground = self.start_position.y
        self.min_y = self.start_position.y
        self.radius_dist = []
        self.propulsion_used = True
        self.on_ground = False
        self.improved = False
        self.n_collisions = 0
        self.penalty = 1
        self.coins = 0
        self.message = ""
        
    def get_feature_vector(self, tile_map):
        self.radius_dist = []
        player_x = self.position.x + self.rect.w / 2
        player_y = self.position.y - self.rect.h / 2
        for theta in range(0, 360, 15):
            collided_tile = None
            for r in range(10, 401, 10):
                px = r * cosd(theta) + player_x
                py = -r * sind(theta) + player_y
                collided_tile = tile_map.check_collidepoint(px, py)
                if collided_tile != None: break
            self.radius_dist.append(r/400)

        return self.radius_dist
        
    def draw(self, display, camera, imprimir=False):
        if imprimir: display.blit(self.image, (self.rect.x - camera.offset.x, self.rect.y - camera.offset.y))
    
    def print(self, display, camera, message, pos, imprimir):
        text = self.font.render(message, True, (0, 0, 0))
        if imprimir: display.blit(text, (self.rect.x - camera.offset.x, self.rect.y - camera.offset.y + pos))
    
    def update(self, dt, tiles):
        self.check_is_dead()
        if self.is_dead: return
        self.horizontal_movement(dt)
        self.checkCollisionsx(tiles)
        self.vertical_movement(dt)
        self.checkCollisionsy(tiles)
        if self.on_ground:
            new_min = min(self.min_y_on_ground, self.position.y)
            self.improved = new_min != self.min_y_on_ground
            self.min_y_on_ground = new_min
        self.min_y = min(self.min_y, self.position.y)

    def check_is_dead(self):
        if self.position.y - self.start_position.y > 100:
            self.is_dead = True
            self.penalty = -1
    
    def get_improved(self):
        improved = self.improved
        self.improved = False
        return improved

    def get_fitness(self):
        return self.penalty * (self.start_position.y - self.min_y)**2/5 + (self.start_position.y - self.min_y_on_ground)**2 - self.n_collisions
        # return (self.start_position.y - self.min_y)**2

    def horizontal_movement(self,dt):
        if self.on_ground:
            self.acceleration.x = 0
            if self.LEFT_KEY:
                self.acceleration.x -= self.acceleration_x
            elif self.RIGHT_KEY:
                self.acceleration.x += self.acceleration_x
            self.acceleration.x += self.get_friction()
            self.velocity.x += self.acceleration.x * dt
            self.limit_velocity(8)
            self.position.x += self.velocity.x * dt + (self.acceleration.x * .5) * (dt * dt)
            self.rect.x = self.position.x
        else:
            self.position.x += self.velocity.x * dt
            self.rect.x = self.position.x


    def vertical_movement(self,dt):
        self.velocity.y += self.acceleration.y * dt
        if self.velocity.y > 7: self.velocity.y = 7
        self.position.y += self.velocity.y * dt + (self.acceleration.y * .5) * (dt * dt)
        self.rect.bottom = self.position.y

    def limit_velocity(self, max_vel):
        self.velocity.x = max(-max_vel, min(self.velocity.x, max_vel))
        if abs(self.velocity.x) < .01: self.velocity.x = 0

    def get_friction(self):
        friction = self.velocity.x * self.friction
        return max(-self.acceleration_x, min(friction, self.acceleration_x))

    def is_enabled_air_propulsion(self):
        return not self.on_ground and not self.propulsion_used and self.velocity.y > 0

    def is_enabled_jump_propulsion(self):
        return self.on_ground

    def air_propulsion(self, jump_height_percentage, horizontal_percentage):
        if self.is_enabled_air_propulsion():
            self.propulsion_used = True
            self.propulsion(jump_height_percentage, horizontal_percentage)

    def jump_propulsion(self, jump_height_percentage, horizontal_percentage):
        if self.is_enabled_jump_propulsion():
            self.on_ground = False
            self.propulsion(jump_height_percentage, horizontal_percentage)

    def propulsion(self, jump_height_percentage, horizontal_percentage):
        """jump_height_percentage deve ser em percentual, o pulo maximo é definido aqui"""
        MAXIMUM_JUMP_HEIGHT = 100 # pixels
        jump_height = jump_height_percentage * MAXIMUM_JUMP_HEIGHT 
        vy = 0.6515899982950621 + 0.82897762 * jump_height**0.5
        vy = 0 if vy < 0.7 else vy
        vx = horizontal_percentage * 10
        self.velocity.x = vx
        self.velocity.y = -vy

    def jump(self, vy):
        if self.on_ground:
            self.velocity.y = vy
            self.on_ground = False

    def get_hits(self, tiles):
        hits = []
        for tile in tiles:
            if self.rect.colliderect(tile):
                hits.append(tile)
        return hits

    def checkCollisionsx(self, tiles):
        collisions = self.get_hits(tiles)
        for tile in collisions:
            self.n_collisions += 1
            if self.velocity.x > 0:  # Hit tile moving right
                self.velocity.x = 0
                self.position.x = tile.rect.left - self.rect.w
                self.rect.x = self.position.x
            elif self.velocity.x < 0:  # Hit tile moving left
                self.velocity.x = 0
                self.position.x = tile.rect.right
                self.rect.x = self.position.x

    def checkCollisionsy(self, tiles):
        self.on_ground = False
        self.rect.bottom += 1
        collisions = self.get_hits(tiles)
        for tile in collisions:
            self.n_collisions += 1
            if self.velocity.y > 0:  # Hit tile from the top
                self.propulsion_used = False
                self.on_ground = True
                self.velocity.y = 0
                self.position.y = tile.rect.top
                self.rect.bottom = self.position.y
            elif self.velocity.y < 0:  # Hit tile from the bottom
                self.velocity.y = 0
                self.position.y = tile.rect.bottom + self.rect.h
                self.rect.bottom = self.position.y






