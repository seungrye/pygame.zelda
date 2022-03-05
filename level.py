import enum
import random
import pygame
from enemy import Enemy
from player import Player
from debug import debug

from settings import TILESIZE
from tile import Tile
from support import *
from ui import UI
from weapon import Weapon

class Level:
    def __init__(self) -> None:
        self.display_surface = pygame.display.get_surface()
        self.visible_sprites = YSortCameraGroup()
        self.obstacles_sprites = pygame.sprite.Group()
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        self.current_attck = None

        self.create_map()

        self.ui = UI()

    def create_map(self) -> None:
        layouts = {
            'boundary': import_csv_layout("./map/map_FloorBlocks.csv"),
            'grass': import_csv_layout("./map/map_Grass.csv"),
            'object': import_csv_layout("./map/map_Objects.csv"),
            'entities': import_csv_layout("./map/map_Entities.csv"),
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
                        Tile((x, y), [self.visible_sprites, self.obstacles_sprites, self.attackable_sprites], 'grass', grass)
                    if style == 'object':
                        surf = graphics['object'][int(col)]
                        Tile((x, y), [self.visible_sprites, self.obstacles_sprites], 'object', surf)
                    if style == 'entities':
                        if col == '394':
                            self.player = Player((x, y), 
                                [self.visible_sprites], self.obstacles_sprites, 
                                self.create_attack, self.destroy_attack,
                                self.create_magic, self.destroy_magic,
                                self.damage_player)
                        else:
                            if col == '390': monster_name = 'bamboo'
                            if col == '391': monster_name = 'spirit'
                            if col == '392': monster_name = 'raccoon'
                            if col == '393': monster_name = 'squid'
                            Enemy(monster_name, (x, y), [self.visible_sprites, self.attackable_sprites], self.obstacles_sprites)

        #         if col == "x":
        #             Tile((x, y), [self.visible_sprites, self.obstacles_sprites])
        #         if col == 'p':
        #             self.player = Player((x, y), [self.visible_sprites], self.obstacles_sprites)


    def create_attack(self):
        self.current_attck = Weapon(self.player, [self.visible_sprites, self.attack_sprites])

    def damage_player(self, amount, attack_type):
        if self.player.vulernable:
            self.player.health -= amount
            self.player.vulernable = False
            self.player.hurt_time = pygame.time.get_ticks()


    def destroy_attack(self):
        if self.current_attck:
            self.current_attck.kill()
            self.current_attck = None

    def create_magic(self, style, strength, cost):
        # self.current_attck = Weapon(self.player, [self.visible_sprites])
        print(style)
        print(strength)
        print(cost)

    def destroy_magic(self):
        pass
        # if self.current_attck:
        #     self.current_attck.kill()
        #     self.current_attck = None

    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
                if collision_sprites:
                    for collision_sprite in collision_sprites:
                        if collision_sprite.sprite_type == 'grass':
                            collision_sprite.kill()
                        elif collision_sprite.sprite_type == 'enemy':
                            collision_sprite.get_damage(self.player, attack_sprite.sprite_type)


    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()  # call Player's update()
        self.visible_sprites.enemy_update(self.player)
        self.player_attack_logic()
        self.ui.display(self.player)

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

    def enemy_update(self, player: Player):
        enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy']
        for sprite in enemy_sprites:
            sprite.enemy_update(player)
