import pygame

from entity import Entity
from support import import_folder
from settings import monster_data
from player import Player

class Enemy(Entity):
    def __init__(self, monster_name, pos, groups, obstacles_sprites) -> None:
        super().__init__(groups)

        self.sprite_type = 'enemy'

        # graphics
        self.import_graphics(monster_name)
        self.status = 'idle'
        self.image = self.animations[self.status][int(self.frame_index)]

        # movement
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)
        self.obstacles_sprites = obstacles_sprites

        # stats
        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
    
        self.health = monster_info['health'] 
        self.exp = monster_info['exp']
        self.damage = monster_info['damage'] 
        self.attack_type = monster_info['attack_type'] 
        self.speed = monster_info['speed'] 
        self.resistance = monster_info['resistance'] 
        self.attack_radius = monster_info['attack_radius'] 
        self.notice_radius = monster_info['notice_radius'] 

        # player interaction
        self.can_attack = True
        self.attack_time = None
        self.attack_cooldown = 400

        # invincibility timer
        self.vulernable = True
        self.hit_time = None
        self.invincibility_duration = 300

    def import_graphics(self, monster_name):
        self.animations = {
            "idle":[],
            "move":[],
            "attack": [],
        }

        for animation in self.animations.keys():
            self.animations[animation] = import_folder(f"./graphics/monsters/{monster_name}/{animation}")

    def get_player_distance_direction(self, player: Player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = enemy_vec.distance_to(player_vec)
        if distance > 0:
            direction = (player_vec-enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2(0,0)

        return (distance, direction)

    def get_status(self, player):
        distance = self.get_player_distance_direction(player)[0]

        if distance < self.attack_radius and self.can_attack:
            if self.status != 'attack':
                self.frame_index = 0
            self.status = 'attack'
        elif distance < self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'

    def actions(self, player):
        if self.status == 'attack':
            self.attack_time = pygame.time.get_ticks()
            player.damage_player(self.damage, self.attack_type)
        elif self.status == 'move':
            self.direction = self.get_player_distance_direction(player)[1]
        else:
            self.direction = pygame.math.Vector2(0,0)

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if not self.can_attack:
            if current_time - self.attack_time > self.attack_cooldown:
                self.can_attack = True

        if not self.vulernable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulernable = True

    def hit_reaction(self):
        if not self.vulernable:
            self.direction *= -self.resistance

    def get_damage(self, player, attack_type):
        if self.vulernable:
            self.direction = self.get_player_distance_direction(player)[1]
            if attack_type == 'weapon':
                self.health -= player.get_full_weapon_damage()
            else:
                # magic
                pass
            self.hit_time = pygame.time.get_ticks()
            self.vulernable = False

    def check_death(self):
        if self.health <= 0:
            self.kill()

    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            if self.status == 'attack':
                self.can_attack = False
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        if not self.vulernable:
            # flicker
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)


    def update(self):
        self.hit_reaction()
        self.move(self.speed)
        self.animate()
        self.cooldowns()
        self.check_death()

    def enemy_update(self, player: Player):
        self.get_status(player)
        self.actions(player)