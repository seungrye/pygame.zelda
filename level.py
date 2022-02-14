import enum
import random
import pygame
from player import Player
from debug import debug

from settings import TILESIZE
from tile import Tile
from support import *

class Level:
    def __init__(self) -> None:
        self.visible_sprites = YSortCameraGroup()
        self.obstacles_sprites = pygame.sprite.Group()

        self.create_map()

    def create_map(self) -> None:
        layouts = {
            'boundary': import_csv_layout("./map/map_FloorBlocks.csv"),
            'grass': import_csv_layout("./map/map_Grass.csv"),
            'object': import_csv_layout("./map/map_Objects.csv"),
        }
        graphics = {
            'grass': import_folder('./graphics/grass/'),
            'object': import_folder('./graphics/objects/'),
        }

        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col == '-1': continue
                    x = col_index * TILESIZE
                    y = row_index * TILESIZE

                    if style == 'boundary':
                        Tile((x, y), [self.obstacles_sprites], 'invisible')
                    if style == 'grass':
                        grass = random.choice(graphics['grass'])
                        Tile((x, y), [self.visible_sprites, self.obstacles_sprites], 'grass', grass)
                    if style == 'object':
                        surf = graphics['object'][int(col)]
                        Tile((x, y), [self.visible_sprites, self.obstacles_sprites], 'object', surf)

        #         if col == "x":
        #             Tile((x, y), [self.visible_sprites, self.obstacles_sprites])
        #         if col == 'p':
        #             self.player = Player((x, y), [self.visible_sprites], self.obstacles_sprites)

        self.player = Player((1500, 1600), [self.visible_sprites], self.obstacles_sprites)

    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()  # call Player's update()
        debug(self.player.direction)

class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self) -> None:
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2(0, 0)

        # creating the floor
        self.floor_surf = pygame.image.load('./graphics/tilemap/ground.png').convert()
        self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # drawing the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, floor_offset_pos)

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_rect = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_rect)
