from xmlrpc.server import DocCGIXMLRPCRequestHandler
from pygame import MOUSEBUTTONDOWN
from tiles import *
from spritesheet import Spritesheet
from player import Player
from camera import *
import neat
import random
import numpy as np

import gzip
import pickle  # pylint: disable=import-error

################################# LOAD UP A BASIC WINDOW AND CLOCK #################################
pygame.init()
DISPLAY_W, DISPLAY_H = 1920, 1080
canvas = pygame.Surface((DISPLAY_W,DISPLAY_H))
window = pygame.display.set_mode(((DISPLAY_W,DISPLAY_H)))
clock = pygame.time.Clock()
TARGET_FPS = 60
################################# LOAD SPRITESHEET AND LEVEL ########## ##########
spritesheet = Spritesheet('assets/spritesheet.png', 32, 32)
tile_map = TileMap('data/jump_level.csv', spritesheet)
################################# LOAD PLAYER ###################################
player = Player(tile_map.start_x, tile_map.start_y, spritesheet)
camera = Camera(player, DISPLAY_W, DISPLAY_H)
follow = Follow(camera,player)
camera.setmethod(follow)
################################# GAME LOOP ##########################
best_fitness = 0
generation = 0
def eval_genomes(genome, config):
    global best_fitness, TARGET_FPS, canvas, window, clock, TARGET_FPS, tile_map, player, camera, follow, generation
    output_message = ""
    generation += 1
    genome_id = generation
    while True:
        ge = genome
        # net = neat.nn.FeedForwardNetwork.create(genome, config)
        net = neat.nn.RecurrentNetwork.create(genome, config)
        activation_times = 0
        player.is_dead = False
        imprimir = True
        while not player.is_dead:
            dt = clock.tick(60) * .001 * TARGET_FPS
            dt = 1.16
            ################################# CHECK PLAYER INPUT #################################
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        player.LEFT_KEY = True
                    elif event.key == pygame.K_RIGHT:
                        player.RIGHT_KEY = True
                    elif event.key == pygame.K_SPACE:
                        if player.on_ground:
                            player.jump_propulsion(1, 0)
                        else:
                            player.air_propulsion(0.7, 0)
                    elif event.key == pygame.K_a:
                        if player.on_ground:
                            player.jump_propulsion(1, -0.5)
                        else:
                            player.air_propulsion(0.7, -0.6)
                    elif event.key == pygame.K_d:
                        if player.on_ground:
                            player.jump_propulsion(1, 0.5)
                        else:
                            player.air_propulsion(0.7, 0.6)
                    elif event.key == pygame.K_KP_ENTER:
                        player.is_dead = False

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        player.LEFT_KEY = False
                    elif event.key == pygame.K_RIGHT:
                        player.RIGHT_KEY = False
                    elif event.key == pygame.K_SPACE:
                        if player.is_jumping:
                            player.is_jumping = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # 1 - left click
                    # 2 - middle click
                    # 3 - right click
                    # 4 - scroll up
                    # 5 - scroll down
                    p = player
                    player_x = p.position.x + p.rect.w / 2 - camera.offset.x
                    player_y = p.position.y - p.rect.h / 2 - camera.offset.y
                    if event.button == 1:
                        x, y = pygame.mouse.get_pos()
                        dx = min(1, max(-1, (x - player_x)/300))
                        dy = min(1, max(0, (player_y - y)/300))
                        print(dy, dx)
                        if player.on_ground:
                            player.jump_propulsion(dy, dx)
                        else:
                            player.air_propulsion(dy, dx)

            if not player.is_dead and (player.is_enabled_air_propulsion() or player.is_enabled_jump_propulsion()):
                activation_times += 1
                feature_vector = player.get_feature_vector(tile_map)

                # output = net.activate(feature_vector+[player.position.x/tile_map.map_w, player.position.y/tile_map.map_h])
                output = net.activate(feature_vector)
                a = (output[0]+1)/2
                b = output[1]
                player.jump_propulsion(a, b)
                player.air_propulsion(a, b)
                output_message = f"{round(a, 3)}, {round(b, 3)}"                

            ################################# UPDATE/ Animate SPRITE #################################
            player.update(dt, tile_map.tiles)
            camera.scroll()
            ################################# UPDATE WINDOW AND DISPLAY #################################
            canvas.fill((0, 180, 240)) # Fills the entire screen with light blue
            if imprimir: tile_map.draw_map(canvas, camera)
            if imprimir: player.draw(canvas, camera, imprimir)
            message = f"G {generation} P {genome_id}: {round(player.get_fitness(), 2)} | {activation_times} |"
            player.print(canvas, camera, message, 40, imprimir)
            player.print(canvas, camera, output_message, 60, imprimir)
            if imprimir: window.blit(canvas, (0,0))
            if imprimir: pygame.display.flip()

            if player.is_dead:
                ge.fitness = player.get_fitness()
                print(message, ge.fitness)
                player.reset_player()
                tile_map.reset_tile_map()


# Setup the NEAT Neural Network
def run(config_path, file_name):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    with gzip.open(f'bests/{file_name}') as f:
        genome_best = pickle.load(f)
    eval_genomes(genome_best, config)

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path, 'best_loop')
    