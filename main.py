import pygame
import sys
import random
import math
from logo import draw_title_screen, create_game_logo

    # Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Pixelated scaling factor
PIXEL_SCALE = 4

# Colors (Nintendo-like palette)
SKY_BLUE = (92, 148, 252)
GROUND_GREEN = (0, 168, 68)
BRICK_RED = (168, 16, 0)
COIN_YELLOW = (252, 188, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
MARIO_RED = (228, 0, 88)
LUIGI_GREEN = (0, 168, 68)
SHOCKWAVE_COLOR = (255, 0, 0) # For Boss shockwave

# Game settings
GRAVITY = 0.8
JUMP_STRENGTH = -16
PLAYER_SPEED = 5

class Player:
    def __init__(self, x, y, color, controls):
        self.x = x
        self.y = y
        self.spawn_x = x  # Remember spawn position
        self.spawn_y = y
        self.width = 32
        self.height = 48
        self.rect = pygame.Rect(x, y, self.width, self.height) # Crucial: Initialize rect
        self.color = color
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.controls = controls
        self.score = 0
        self.facing_right = True
        self.lives = 3
        self.dead = False
        self.double_jump_available = True

    def update(self, platforms, coins, enemies):
        if self.dead:
            return

        keys = pygame.key.get_pressed()

        # Horizontal movement
        self.vel_x = 0
        if keys[self.controls['left']]:
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
        if keys[self.controls['right']]:
            self.vel_x = PLAYER_SPEED
            self.facing_right = True

        # Jumping
        if keys[self.controls['jump']]:
            if self.on_ground:
                self.vel_y = JUMP_STRENGTH
                self.on_ground = False
                self.double_jump_available = True
            elif self.double_jump_available:
                self.vel_y = JUMP_STRENGTH
                self.double_jump_available = False

        # Apply gravity
        self.vel_y += GRAVITY

        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Update self.rect *after* position changes and *before* collision checks
        self.rect.topleft = (self.x, self.y)

        # Keep player on screen horizontally
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
        self.rect.topleft = (self.x, self.y) # Re-update rect if x changed

        # Check platform collisions
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                overlap_left = self.rect.right - platform.rect.left
                overlap_right = platform.rect.right - self.rect.left
                overlap_top = self.rect.bottom - platform.rect.top
                overlap_bottom = platform.rect.bottom - self.rect.top
                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

                if min_overlap == overlap_top and self.vel_y >= 0:
                    self.y = platform.rect.top - self.height
                    self.vel_y = 0
                    self.on_ground = True
                    self.double_jump_available = True
                elif min_overlap == overlap_bottom and self.vel_y < 0:
                    self.y = platform.rect.bottom
                    self.vel_y = 0
                elif min_overlap == overlap_left and self.vel_x > 0:
                    self.x = platform.rect.left - self.width
                elif min_overlap == overlap_right and self.vel_x < 0:
                    self.x = platform.rect.right
                self.rect.topleft = (self.x, self.y) # Re-update rect after collision adjustment

        # Ground collision
        if self.y + self.height >= SCREEN_HEIGHT - 50:
            self.y = SCREEN_HEIGHT - 50 - self.height
            self.vel_y = 0
            self.on_ground = True
            self.double_jump_available = True
        self.rect.topleft = (self.x, self.y) # Re-update rect after ground collision

        # Collect coins
        for coin in coins[:]:
            if self.rect.colliderect(coin.rect):
                coins.remove(coin)
                self.score += 100

        # Enemy collision
        for enemy in enemies[:]:
            if self.rect.colliderect(enemy.rect):
                player_prev_bottom = self.rect.bottom - self.vel_y 
                stomp_zone_top = enemy.rect.top + (enemy.rect.height * 0.5) # Increased stomp zone to 50%

                if self.vel_y > 0 and player_prev_bottom <= stomp_zone_top: # Stomp
                    self.vel_y = JUMP_STRENGTH // 2
                    self.score += 200
                    enemy.hit()
                    if not enemy.alive:
                        enemies.remove(enemy)
                    self.on_ground = False 
                    self.double_jump_available = True 
                else:
                    self.respawn()

    def respawn(self):
        self.lives -= 1
        self.score = max(0, self.score - 50)
        if self.lives <= 0:
            self.dead = True
        else:
            self.x = self.spawn_x
            self.y = self.spawn_y
            self.rect.topleft = (self.x, self.y) # Update rect on respawn
            self.vel_x = 0
            self.vel_y = 0
            self.on_ground = False
            self.double_jump_available = True

    def draw(self, screen):
        if self.dead:
            return
        player_surface = pygame.Surface((self.width // PIXEL_SCALE, self.height // PIXEL_SCALE))
        player_surface.fill(self.color)
        pygame.draw.rect(player_surface, BLACK, (1, 0, 6, 2))
        if self.facing_right:
            pygame.draw.rect(player_surface, WHITE, (5, 3, 2, 2))
            pygame.draw.rect(player_surface, BLACK, (6, 3, 1, 1))
        else:
            pygame.draw.rect(player_surface, WHITE, (1, 3, 2, 2))
            pygame.draw.rect(player_surface, BLACK, (1, 3, 1, 1))
        pygame.draw.rect(player_surface, BLACK, (2, 6, 4, 1))
        pygame.draw.rect(player_surface, BLACK, (1, 8, 1, 2))
        pygame.draw.rect(player_surface, BLACK, (6, 8, 1, 2))
        scaled_surface = pygame.transform.scale(player_surface, (self.width, self.height))
        screen.blit(scaled_surface, (self.x, self.y))

class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen):
        brick_size = 16
        for i in range(0, self.rect.width, brick_size):
            for j in range(0, self.rect.height, brick_size):
                brick_rect = pygame.Rect(self.rect.x + i, self.rect.y + j, brick_size, brick_size)
                pygame.draw.rect(screen, BRICK_RED, brick_rect)
                pygame.draw.rect(screen, (140, 12, 0), brick_rect, 2)
                pygame.draw.rect(screen, (200, 20, 0), (brick_rect.x + 2, brick_rect.y + 2, brick_size - 4, brick_size - 4))

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.animation_timer = 0

    def update(self):
        self.animation_timer += 1

    def draw(self, screen):
        offset = int(math.sin(self.animation_timer * 0.2) * 2)
        coin_rect = pygame.Rect(self.rect.x, self.rect.y + offset, 20, 20)
        pygame.draw.rect(screen, COIN_YELLOW, coin_rect)
        pygame.draw.rect(screen, (200, 148, 0), coin_rect, 2)
        inner_rect = pygame.Rect(coin_rect.x + 4, coin_rect.y + 4, 12, 12)
        pygame.draw.rect(screen, (255, 220, 50), inner_rect)
        center_rect = pygame.Rect(coin_rect.x + 8, coin_rect.y + 8, 4, 4)
        pygame.draw.rect(screen, (200, 148, 0), center_rect)

class Enemy:
    def __init__(self, x, y, health=1):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 24
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.vel_x = random.choice([-2, 2])
        self.animation_timer = 0
        self.health = health
        self.max_health = health
        self.alive = True

    def update(self, platforms): # Standard enemies don't need players_list
        if not self.alive:
            return
        self.animation_timer += 1
        self.x += self.vel_x
        if self.x <= 0 or self.x + self.width >= SCREEN_WIDTH:
            self.vel_x *= -1
        self.rect.x = self.x # Update rect x before collision check

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Correctly adjust position based on original direction of movement
                if self.vel_x > 0:  # Enemy was moving right, collided with platform's left side
                    self.x = platform.rect.left - self.width
                elif self.vel_x < 0:  # Enemy was moving left, collided with platform's right side
                    self.x = platform.rect.right
                
                self.vel_x *= -1  # Reverse velocity *after* position correction
                self.rect.x = self.x # Update rect x immediately after position change
                break  # Exit loop after handling one collision
        
        # Ensure rect is fully updated after all x and y modifications for the frame
        self.rect.topleft = (self.x, self.y)

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.alive = False

    def draw(self, screen):
        if not self.alive:
            return
        enemy_surface = pygame.Surface((self.width, self.height))
        color = (139, 69, 19) if self.animation_timer % 60 < 30 else (160, 82, 45)
        if hasattr(self, 'is_boss') and self.is_boss: # Example for boss visual differentiation
             color = (100, 0, 0) # Darker red for main boss
        enemy_surface.fill(color)
        pygame.draw.rect(enemy_surface, color, (0, 0, self.width, self.height // 2))
        pygame.draw.rect(enemy_surface, (100, 50, 10), (0, 0, self.width, self.height // 2), 2)
        body_color = (222, 173, 98)
        pygame.draw.rect(enemy_surface, body_color, (4, self.height // 2, self.width - 8, self.height // 2))
        pygame.draw.rect(enemy_surface, BLACK, (4, 6, 3, 3))
        pygame.draw.rect(enemy_surface, BLACK, (17, 6, 3, 3))
        pygame.draw.rect(enemy_surface, WHITE, (5, 7, 1, 1))
        pygame.draw.rect(enemy_surface, WHITE, (18, 7, 1, 1))
        pygame.draw.rect(enemy_surface, (139, 69, 19), (2, self.height - 4, 4, 4))
        pygame.draw.rect(enemy_surface, (139, 69, 19), (18, self.height - 4, 4, 4))
        screen.blit(enemy_surface, (self.x, self.y))
        
        # Draw health bar for enemies with more than 1 max_health
        if self.max_health > 1 and self.alive:
            health_bar_width_total = self.width
            health_bar_height = 5
            health_bar_x = self.rect.x
            health_bar_y = self.rect.y - health_bar_height - 3 # Position above enemy

            current_health_percentage = self.health / self.max_health
            current_health_width = health_bar_width_total * current_health_percentage

            pygame.draw.rect(screen, (255,0,0), (health_bar_x, health_bar_y, health_bar_width_total, health_bar_height)) # Red background
            pygame.draw.rect(screen, (0,255,0), (health_bar_x, health_bar_y, current_health_width, health_bar_height)) # Green foreground

class Fireball:
    def __init__(self, x, y, vel_x, vel_y, width=12, height=12, color=(255,100,0)):
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.color = color
        self.outline_color = (max(0, color[0]-50), max(0, color[1]-50), max(0, color[2]-50))

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, self.outline_color, self.rect, 1)

class Shockwave:
    def __init__(self, center_x, center_y, max_radius=100, speed=2, ring_width=8, color=SHOCKWAVE_COLOR):
        self.center_x = center_x
        self.center_y = center_y
        self.current_radius = 0
        self.max_radius = max_radius
        self.speed = speed
        self.ring_width = ring_width
        self.color = color
        self.active = True

    def update(self):
        if self.active:
            self.current_radius += self.speed
            if self.current_radius > self.max_radius:
                self.active = False
    
    def draw(self, screen):
        if self.active and self.current_radius > self.ring_width // 2:
             # Draw a circle with thickness (ring)
            pygame.draw.circle(screen, self.color, (self.center_x, self.center_y), int(self.current_radius), self.ring_width)

    def collides_with_player(self, player_rect):
        if not self.active:
            return False
        # Check collision between player's rect and the shockwave ring
        # Approximate collision: check distance from player center to shockwave center
        player_center_x = player_rect.centerx
        player_center_y = player_rect.centery
        dist_sq = (player_center_x - self.center_x)**2 + (player_center_y - self.center_y)**2
        
        # Effective radii for collision check
        inner_radius_sq = (self.current_radius - self.ring_width / 2 - player_rect.width / 2)**2 
        outer_radius_sq = (self.current_radius + self.ring_width / 2 + player_rect.width / 2)**2
        
        # Ensure radii are not negative
        inner_radius_sq = max(0, inner_radius_sq)

        return inner_radius_sq <= dist_sq <= outer_radius_sq


class TurretEnemy(Enemy):
    def __init__(self, x, y, health=15, shoot_interval=90, projectile_speed=6, width=32, height=32): # Increased size
        super().__init__(x, y, health)
        self.width = width # Apply new width
        self.height = height # Apply new height
        self.rect = pygame.Rect(x, y, self.width, self.height) # Update rect with new size
        self.vel_x = 0 # Stays still
        self.shoot_timer = random.randint(0, shoot_interval)
        self.shoot_interval = shoot_interval
        self.fireballs = []
        self.projectile_speed = projectile_speed
        self.turret_color_base = (80, 80, 80)
        self.turret_color_cannon = (40, 40, 40)
        self.last_shot_direction = 1

    def update(self, platforms, players_list):
        self.animation_timer += 1
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_interval:
            self.shoot(players_list)
            self.shoot_timer = 0
        for fireball in self.fireballs[:]:
            fireball.update()
            if fireball.rect.right < -SCREEN_WIDTH or fireball.rect.left > SCREEN_WIDTH * 2:
                self.fireballs.remove(fireball)

    def shoot(self, players_list):
        closest_player = None
        min_dist_sq = float('inf')
        for player in players_list:
            if not player.dead:
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                dist_sq = dx*dx + dy*dy
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    closest_player = player
        if closest_player:
            direction = 1 if closest_player.rect.centerx > self.rect.centerx else -1
            self.last_shot_direction = direction
            fb_width, fb_height = 12, 12
            fireball_y = self.rect.centery - fb_height // 2
            fireball_vel_x = direction * self.projectile_speed
            fireball_vel_y = 0
            fireball_x = self.rect.right if direction == 1 else self.rect.left - fb_width
            self.fireballs.append(Fireball(fireball_x, fireball_y, fireball_vel_x, fireball_vel_y, width=fb_width, height=fb_height))

    def draw(self, screen):
        if not self.alive:
            return
        pygame.draw.rect(screen, self.turret_color_base, self.rect)
        cannon_width = self.width
        cannon_height = self.height // 2
        cannon_y = self.rect.centery - cannon_height // 2
        if self.last_shot_direction == 1:
            cannon_rect_visual = pygame.Rect(self.rect.centerx - cannon_width // 4, cannon_y, cannon_width, cannon_height)
        else:
            cannon_rect_visual = pygame.Rect(self.rect.left - cannon_width // 2, cannon_y, cannon_width, cannon_height)
        pygame.draw.ellipse(screen, self.turret_color_cannon, cannon_rect_visual)
        super().draw(screen) # To draw health bar from base Enemy class
        for fireball in self.fireballs:
            fireball.draw(screen)

class BossEnemy(Enemy): # Main boss for Level 5
    def __init__(self, x, y, health=30, shockwave_interval=240, shockwave_speed=2, shockwave_radius=120): # Shockwave every 4s
        super().__init__(x, y, health)
        self.is_boss = True # For potential visual differentiation in Enemy.draw
        self.shockwave_timer = random.randint(0, shockwave_interval)
        self.shockwave_interval = shockwave_interval
        self.shockwaves = []
        self.shockwave_speed = shockwave_speed
        self.shockwave_max_radius = shockwave_radius
        self.vel_x = random.choice([-3, 3]) # Boss specific speed

    def update(self, platforms, players_list=None): # players_list is for consistency, not used by shockwave targeting
        super().update(platforms) # Standard enemy movement (including rect updates)

        self.shockwave_timer += 1
        if self.shockwave_timer >= self.shockwave_interval:
            self.create_shockwave()
            self.shockwave_timer = 0

        for shockwave in self.shockwaves[:]:
            shockwave.update()
            if not shockwave.active:
                self.shockwaves.remove(shockwave)

    def create_shockwave(self):
        self.shockwaves.append(Shockwave(self.rect.centerx, self.rect.centery, 
                                         max_radius=self.shockwave_max_radius, 
                                         speed=self.shockwave_speed))

    def draw(self, screen):
        super().draw(screen) # Draw standard enemy appearance + health bar
        for shockwave in self.shockwaves:
            shockwave.draw(screen)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Jump Bros - Nintendo-Style Multiplayer Platformer")
        self.clock = pygame.time.Clock()
        self.game_over = False
        self.title_screen = True
        self.winner_text = ""
        self.current_level = 1
        self.max_level = 5
        self.level_complete = False
        self.players = []
        self.player1 = Player(100, SCREEN_HEIGHT - 50 - 48, MARIO_RED, {
            'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w
        })
        self.player2 = Player(300, SCREEN_HEIGHT - 50 - 48, LUIGI_GREEN, {
            'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP,
        })
        self.players = [self.player1, self.player2]
        self.setup_level(self.current_level)
        self.font = pygame.font.Font(None, 36)

    def setup_level(self, level_num):
        if level_num == 1:
            self.platforms = [
                Platform(200, 600, 200, 32), Platform(500, 500, 150, 32),
                Platform(700, 400, 200, 32), Platform(300, 350, 100, 32),
                Platform(800, 250, 150, 32), Platform(50, 200, 132, 32),
            ]
            coin_positions = [
                (250, 550), (550, 450), (750, 350), (350, 300), (850, 200), (100, 150)
            ]
            enemy_positions = [
                (250, 576), (550, 476), (750, 376)
            ]
        elif level_num == 2:
            self.platforms = [
                Platform(150, 650, 100, 32), Platform(350, 550, 100, 32),
                Platform(550, 450, 100, 32), Platform(750, 350, 100, 32),
                Platform(200, 300, 120, 32), Platform(500, 200, 120, 32),
                Platform(800, 150, 120, 32), Platform(100, 100, 100, 32),
                Platform(195, 240, 32, 120), Platform(620, 200, 80, 32),
            ]
            coin_positions = [
                (175, 600), (375, 500), (575, 400), (775, 300), (230, 250),
                (530, 150), (830, 100), (125, 50)
            ]
            enemy_positions = [
                (175, 626), (375, 526), (575, 426), (775, 326), (530, 176)
            ]
        elif level_num == 3:
            self.platforms = [
                Platform(100, 650, 80, 32), Platform(250, 600, 80, 32),
                Platform(400, 550, 80, 32), Platform(550, 500, 80, 32),
                Platform(700, 450, 80, 32), Platform(850, 400, 80, 32),
                Platform(750, 300, 100, 32), Platform(500, 250, 100, 32),
                Platform(250, 200, 100, 32), Platform(50, 150, 100, 32),
                Platform(400, 100, 200, 32),
            ]
            coin_positions = [
                (125, 600), (275, 550), (425, 500), (575, 450), (725, 400),
                (875, 350), (775, 250), (525, 200), (275, 150), (75, 100),
                (450, 50), (525, 50)
            ]
            enemy_positions = [
                (125, 626), (275, 576), (425, 526), (575, 476), (725, 426),
                (775, 276), (525, 226), (275, 176), (450, 76)
            ]
        elif level_num == 4:
            self.platforms = [
                Platform(50, 700, 100, 32), Platform(200, 600, 80, 32),
                Platform(350, 500, 120, 32), Platform(500, 650, 100, 32),
                Platform(650, 550, 80, 32), Platform(800, 450, 150, 32),
                Platform(600, 350, 32, 100), Platform(400, 300, 100, 32),
                Platform(200, 250, 80, 32), Platform(50, 150, 100, 32),
            ]
            coin_positions = [
                (75, 650), (225, 550), (375, 450), (525, 600), (675, 500),
                (875, 400), (608, 280), (425, 250), (225, 200), (75, 100),
            ]
            enemy_positions = [ # Enemy at (75,676) was removed
                (225, 576), (375, 476), (525, 626), (675, 526),
                (875, 426), (425, 276), (225, 226)
            ]
        elif level_num == 5:
            self.platforms = [
                Platform(50, 700, SCREEN_WIDTH - 100, 32), 
                Platform(200, 550, 150, 32), Platform(SCREEN_WIDTH - 200 - 150, 550, 150, 32),
                Platform(SCREEN_WIDTH // 2 - 100, 400, 200, 32), 
                Platform(100, 236, 100, 32), Platform(SCREEN_WIDTH - 200, 236, 100, 32), 
                Platform(SCREEN_WIDTH // 2 - 75, 252, 150, 32), 
            ]
            coin_positions = [
                (100, 650), (SCREEN_WIDTH - 150, 650), (250, 500), 
                (SCREEN_WIDTH - 250 - 50, 500), (SCREEN_WIDTH // 2, 350),
                (125, 186), (SCREEN_WIDTH - 125 - 50, 186), (SCREEN_WIDTH // 2, 212)
            ]
            enemy_positions = [ # Standard enemies for level 5
                (250, 526), (SCREEN_WIDTH - 250 - 24, 526),
                (442, 376), (558, 376) 
            ]
            # Boss and Turret are added separately below
            self.boss_enemy_data = (SCREEN_WIDTH // 2 - 36, 180, 72, 72) 

        self.coins = []
        for x, y in coin_positions:
            self.coins.append(Coin(x, y))
        self.enemies = []
        for x, y in enemy_positions:
            self.enemies.append(Enemy(x, y))

        if level_num == 5 and hasattr(self, 'boss_enemy_data'):
            bx, by, bw, bh = self.boss_enemy_data
            boss = BossEnemy(bx, by, health=30) 
            boss.width = bw
            boss.height = bh
            boss.rect = pygame.Rect(bx, by, bw, bh)
            boss.vel_x = random.choice([-3, 3]) 
            self.enemies.append(boss)

            turret_x = SCREEN_WIDTH // 2 - 16 # Adjust x for new width (32/2 = 16)
            turret_y = 700 - 32 # Adjust y for new height (32)
            turret = TurretEnemy(turret_x, turret_y, health=15, shoot_interval=90, projectile_speed=4)
            self.enemies.append(turret)
            self.enemies.append(TurretEnemy(150, 176))
            self.enemies.append(TurretEnemy(750, 176))

        # Reset players
        for player in self.players:
            player.x = player.spawn_x
            player.y = player.spawn_y
            player.rect.topleft = (player.x, player.y)
            player.vel_x = 0
            player.vel_y = 0
            player.on_ground = False
            player.lives = 3
            player.dead = False
            player.double_jump_available = True
        self.game_over = False
        self.level_complete = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.title_screen and event.key == pygame.K_SPACE:
                    self.title_screen = False
                elif event.key == pygame.K_r:
                    self.__init__()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if self.level_complete:
                    restart_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 60, 120, 50)
                    next_level_button_rect = pygame.Rect(SCREEN_WIDTH // 2 + 30, SCREEN_HEIGHT // 2 + 60, 120, 50)
                    if restart_button_rect.collidepoint(mouse_x, mouse_y):
                        self.setup_level(self.current_level)
                    elif next_level_button_rect.collidepoint(mouse_x, mouse_y):
                        if self.current_level < self.max_level:
                            self.current_level += 1
                            self.setup_level(self.current_level)
                        else:
                            self.__init__()
                elif self.game_over:
                    restart_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 60, 200, 50)
                    if restart_button_rect.collidepoint(mouse_x, mouse_y):
                        self.setup_level(self.current_level)
        return True

    def update(self):
        if not self.title_screen and not self.game_over and not self.level_complete:
            for player in self.players:
                player.update(self.platforms, self.coins, self.enemies)
            for coin in self.coins:
                coin.update()

            self.enemies = [enemy for enemy in self.enemies if enemy.alive]
            for enemy in self.enemies:
                if isinstance(enemy, TurretEnemy) or isinstance(enemy, BossEnemy):
                    enemy.update(self.platforms, self.players) 
                else:
                    enemy.update(self.platforms)

            # Projectile and Shockwave Collisions
            for player in self.players:
                if player.dead:
                    continue
                for enemy in self.enemies:
                    if hasattr(enemy, 'fireballs'): 
                        for fireball in enemy.fireballs[:]: 
                            if player.rect.colliderect(fireball.rect):
                                player.respawn()
                                enemy.fireballs.remove(fireball) 
                                if player.dead: break 
                    if isinstance(enemy, BossEnemy) and hasattr(enemy, 'shockwaves'):
                        for shockwave in enemy.shockwaves[:]:
                            if shockwave.active and shockwave.collides_with_player(player.rect):
                                player.respawn()
                                # Shockwave might hit multiple players or persist
                                if player.dead: break 
                if player.dead: continue # Next player if current one died

            # Check for level complete or game over conditions
            if not self.level_complete and not self.game_over:
                objectives_cleared = (len(self.coins) == 0 and len(self.enemies) == 0)

                if objectives_cleared:
                    self.level_complete = True
                    p1_alive = not self.player1.dead
                    p2_alive = not self.player2.dead

                    if p1_alive and not p2_alive:
                        self.winner_text = "Player 1 Wins Level!"
                    elif not p1_alive and p2_alive:
                        self.winner_text = "Player 2 Wins Level!"
                    elif p1_alive and p2_alive: # Both alive
                        if self.player1.score > self.player2.score:
                            self.winner_text = "Player 1 Wins Level!"
                        elif self.player2.score > self.player1.score:
                            self.winner_text = "Player 2 Wins Level!"
                        else:
                            self.winner_text = "Level Complete - Tie!"
                    else: # Both dead, but objectives cleared (should ideally be game_over if it triggers first)
                        self.winner_text = "Level Cleared!"
                
                # Game over if any player has no lives left (and not already level complete)
                # More robust: game over if ALL players are dead. Or if one player is dead in a single player context.
                # For 2 player, if one dies, the other can continue. If both die, then game over.
                if not self.level_complete:
                    num_dead_players = sum(1 for p in self.players if p.dead)
                    if num_dead_players == len(self.players): # All players dead
                        self.game_over = True
                        self.winner_text = "Both Players Lost!"
                    elif num_dead_players == 1 and len(self.players) == 2: # One player dead in 2P game
                        # Determine winner if one player is left
                        if self.player1.dead and not self.player2.dead:
                             # Potentially game over if level cannot be completed by one player
                             # For now, let the game continue until level objectives met or other player dies
                             pass
                        elif self.player2.dead and not self.player1.dead:
                             pass


    def draw(self):
        if self.title_screen:
            draw_title_screen(self.screen, self.font)
            pygame.display.flip()
            return

        self.screen.fill(SKY_BLUE)
        for i in range(0, SCREEN_WIDTH + 100, 200):
            cloud_rects = [
                pygame.Rect(i - 40, 110, 16, 16), pygame.Rect(i - 24, 110, 16, 16),
                pygame.Rect(i - 8, 110, 16, 16), pygame.Rect(i + 8, 110, 16, 16),
                pygame.Rect(i - 32, 94, 16, 16), pygame.Rect(i - 16, 94, 16, 16),
                pygame.Rect(i, 94, 16, 16), pygame.Rect(i - 24, 78, 16, 16),
                pygame.Rect(i - 8, 78, 16, 16),
            ]
            for rect in cloud_rects: pygame.draw.rect(self.screen, WHITE, rect)
        pygame.draw.rect(self.screen, GROUND_GREEN, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
        for platform in self.platforms: platform.draw(self.screen)
        for coin in self.coins: coin.draw(self.screen)
        for enemy in self.enemies: enemy.draw(self.screen)
        for player in self.players: player.draw(self.screen)

        score1_text = self.font.render(f"Player 1: {self.player1.score} | Lives: {self.player1.lives}", True, WHITE)
        score2_text = self.font.render(f"Player 2: {self.player2.score} | Lives: {self.player2.lives}", True, WHITE)
        controls_text = self.font.render("P1: WASD | P2: Arrow Keys | R: Restart", True, WHITE)
        self.screen.blit(score1_text, (10, 10))
        self.screen.blit(score2_text, (10, 50))
        self.screen.blit(controls_text, (10, SCREEN_HEIGHT - 40))
        level_info_text = self.font.render(f"Level {self.current_level}/{self.max_level}", True, WHITE)
        self.screen.blit(level_info_text, (SCREEN_WIDTH - 150, 10))
        objective_text = self.font.render(f"Coins: {len(self.coins)} | Enemies: {len(self.enemies)}", True, WHITE)
        self.screen.blit(objective_text, (SCREEN_WIDTH // 2 - 100, 10))

        if self.level_complete:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            self.screen.blit(overlay, (0,0))
            level_text_surf = self.font.render(f"Level {self.current_level} Complete!", True, COIN_YELLOW)
            level_rect_surf = level_text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
            winner_surf = self.font.render(self.winner_text, True, WHITE)
            winner_rect_surf = winner_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            border_rect_ui = level_rect_surf.union(winner_rect_surf).inflate(40,20)
            pygame.draw.rect(self.screen, WHITE, border_rect_ui)
            pygame.draw.rect(self.screen, BLACK, border_rect_ui, 4)
            self.screen.blit(level_text_surf, level_rect_surf)
            self.screen.blit(winner_surf, winner_rect_surf)
            
            restart_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 60, 120, 50)
            next_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 + 30, SCREEN_HEIGHT // 2 + 60, 120, 50)
            pygame.draw.rect(self.screen, MARIO_RED, restart_btn_rect)
            pygame.draw.rect(self.screen, WHITE, restart_btn_rect, 4)
            restart_txt_surf = self.font.render("RESTART", True, WHITE)
            self.screen.blit(restart_txt_surf, restart_txt_surf.get_rect(center=restart_btn_rect.center))
            if self.current_level < self.max_level:
                pygame.draw.rect(self.screen, LUIGI_GREEN, next_btn_rect)
                pygame.draw.rect(self.screen, WHITE, next_btn_rect, 4)
                next_txt_surf = self.font.render("NEXT", True, WHITE)
                self.screen.blit(next_txt_surf, next_txt_surf.get_rect(center=next_btn_rect.center))
            else:
                pygame.draw.rect(self.screen, COIN_YELLOW, next_btn_rect)
                pygame.draw.rect(self.screen, WHITE, next_btn_rect, 4)
                complete_txt_surf = pygame.font.Font(None, 24).render("COMPLETE!", True, BLACK)
                self.screen.blit(complete_txt_surf, complete_txt_surf.get_rect(center=next_btn_rect.center))
            instr_font = pygame.font.Font(None, 24)
            instr_surf = instr_font.render("Click buttons or press R to restart", True, WHITE)
            self.screen.blit(instr_surf, instr_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 130)))

        elif self.game_over: # Only show game over if not level complete
            # Determine winner text if not already set by a specific condition
            if not self.winner_text: # Default game over text if not set by specific player death logic
                if self.player1.dead and self.player2.dead: self.winner_text = "Both Players Lost!"
                elif self.player1.dead: self.winner_text = "Player 2 Wins!"
                elif self.player2.dead: self.winner_text = "Player 1 Wins!"
                else: self.winner_text = "Game Over!" # Fallback

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            self.screen.blit(overlay, (0,0))
            game_over_surf = self.font.render("Game Over!", True, MARIO_RED)
            game_over_rect_surf = game_over_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
            winner_surf = self.font.render(self.winner_text, True, WHITE)
            winner_rect_surf = winner_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            border_rect_ui = game_over_rect_surf.union(winner_rect_surf).inflate(40,20)
            pygame.draw.rect(self.screen, WHITE, border_rect_ui)
            pygame.draw.rect(self.screen, BLACK, border_rect_ui, 4)
            self.screen.blit(game_over_surf, game_over_rect_surf)
            self.screen.blit(winner_surf, winner_rect_surf)

            restart_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 60, 200, 50)
            pygame.draw.rect(self.screen, MARIO_RED, restart_btn_rect)
            pygame.draw.rect(self.screen, WHITE, restart_btn_rect, 4)
            restart_txt_surf = self.font.render("RESTART", True, WHITE)
            self.screen.blit(restart_txt_surf, restart_txt_surf.get_rect(center=restart_btn_rect.center))
            instr_font = pygame.font.Font(None, 24)
            instr_surf = instr_font.render("Click RESTART or press R", True, WHITE)
            self.screen.blit(instr_surf, instr_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 130)))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()