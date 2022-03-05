import pygame
from entity import Entity

from support import import_folder
from settings import weapon_data
from settings import magic_data

class Player(Entity):
    def __init__(self, pos, groups, obstacle_sprites, 
            create_attack, destroy_attack,
            create_magic, destroy_magic, damage_player) -> None:
        super().__init__(groups)
        self.image = pygame.image.load("./graphics/player.png").convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)

        self.import_player_assets()
        self.status = 'down'
        # self.frame_index = 0
        # self.animation_speed = 0.15
       
        # self.direction = pygame.math.Vector2()
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None

        self.obstacles_sprites = obstacle_sprites

        # weapon
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]

        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200

        # magic
        self.create_magic = create_magic
        self.destroy_magic = destroy_magic
        self.magic_index = 0
        self.magic = list(magic_data.keys())[self.magic_index]

        self.can_switch_magic = True
        self.magic_switch_time = None


        # stats
        self.stats = { 'health': 100, 'energy':60, 'attack': 10, 'magic':4, 'speed':6}
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.exp = 0 # 경험치
        self.speed = self.stats['speed']


        self.damage_player = damage_player

        # invincibility timer
        self.vulernable = True
        self.hurt_time = None
        self.invincibility_duration = 300


    def get_full_weapon_damage(self):
        base_damage = self.stats['attack']
        weapon_damage = weapon_data[self.weapon]['damage']
        return base_damage + weapon_damage

    def import_player_assets(self):
        self.animations = {
            "down":[],
            "down_attack":[],
            "down_idle": [],
            "left": [],
            "left_attack": [],
            "left_idle": [],
            "right": [],
            "right_attack": [],
            "right_idle": [],
            "up": [],
            "up_attack": [],
            "up_idle": []
        }

        for animation in self.animations.keys():
            self.animations[animation] = import_folder(f"./graphics/player/{animation}")

    def input(self) -> None:
        if self.attacking: return None
        
        keys = pygame.key.get_pressed()

        # movement
        if keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.status = "left"
        elif keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.status = "right"
        else:
            self.direction.x = 0

        if keys[pygame.K_UP]:
            self.direction.y = -1
            self.status = "up"
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
            self.status = "down"
        else:
            self.direction.y = 0

        # attack
        if keys[pygame.K_z]:
            self.attacking = True
            self.attack_time = pygame.time.get_ticks()
            self.create_attack()

        # magic
        if keys[pygame.K_x]:
            self.attacking = True
            self.attack_time = pygame.time.get_ticks()
            style = magic_data[self.magic]['graphic']
            strength = magic_data[self.magic]['strength']
            cost = magic_data[self.magic]['cost']
            self.create_magic(style, strength, cost)

        # swap weapon
        if keys[pygame.K_TAB] and self.can_switch_weapon:
            self.can_switch_weapon = False
            self.weapon_switch_time = pygame.time.get_ticks()
            self.weapon_index += 1
            if self.weapon_index >= len(weapon_data):
                self.weapon_index = 0
            self.weapon = list(weapon_data.keys())[self.weapon_index]

        # swap magic
        if keys[pygame.K_q] and self.can_switch_magic:
            self.can_switch_magic = False
            self.magic_switch_time = pygame.time.get_ticks()
            self.magic_index += 1
            if self.magic_index >= len(magic_data):
                self.magic_index = 0
            self.magic = list(magic_data.keys())[self.magic_index]


    def get_status(self):
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status:
                self.status = f"{self.status}_idle"

        if self.attacking:
            self.direction.x = 0
            self.direction.y = 0
            if not 'attack' in self.status:
                if 'idle' in self.status:
                    self.status = self.status.replace('idle', 'attack')
                else:
                    self.status = f"{self.status}_attack"
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('attack', 'idle')

    # def collision(self, direction):
    #     if direction == "horizontal":
    #         for sprite in self.obstacles_sprites:
    #             if sprite.hitbox.colliderect(self.hitbox):
    #                 if self.direction.x > 0:  # moving right
    #                     self.hitbox.right = sprite.hitbox.left
    #                 elif self.direction.x < 0:  # moving left
    #                     self.hitbox.left = sprite.hitbox.right
    #     elif direction == "vertical":
    #         for sprite in self.obstacles_sprites:
    #             if sprite.hitbox.colliderect(self.hitbox):
    #                 if self.direction.y > 0:  # moving down
    #                     self.hitbox.bottom = sprite.hitbox.top
    #                 elif self.direction.y < 0:  # moving up
    #                     self.hitbox.top = sprite.hitbox.bottom

    # def move(self, speed):
    #     # make same speed in x and y direction
    #     if self.direction.magnitude() != 0:
    #         self.direction = self.direction.normalize()

    #     self.hitbox.x += self.direction.x * speed
    #     self.collision("horizontal")
    #     self.hitbox.y += self.direction.y * speed
    #     self.collision("vertical")

    #     self.rect.center = self.hitbox.center

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if self.attacking:
            if current_time - self.attack_time > self.attack_cooldown + weapon_data[self.weapon]['cooldown']:
                self.attacking = False
                self.destroy_attack()
                
        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time > self.switch_duration_cooldown:
                self.can_switch_weapon = True

        if not self.can_switch_magic:
            if current_time - self.magic_switch_time > self.switch_duration_cooldown:
                self.can_switch_magic = True

        if not self.vulernable:
            if current_time - self.hurt_time > self.invincibility_duration:
                self.vulernable = True

    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        if not self.vulernable:
            # flicker
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)


    def update(self) -> None:
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)
