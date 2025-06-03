
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
        self.color = color
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.controls = controls
        self.score = 0
        self.facing_right = True
        self.lives = 3
        self.dead = False
        
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
        if keys[self.controls['jump']] and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
            
        # Apply gravity
        self.vel_y += GRAVITY
        
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Keep player on screen horizontally
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
            
        # Check platform collisions
        self.on_ground = False
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        for platform in platforms:
            if player_rect.colliderect(platform.rect):
                # Calculate overlap amounts
                overlap_left = player_rect.right - platform.rect.left
                overlap_right = platform.rect.right - player_rect.left
                overlap_top = player_rect.bottom - platform.rect.top
                overlap_bottom = platform.rect.bottom - player_rect.top
                
                # Find minimum overlap to determine collision direction
                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                
                if min_overlap == overlap_top and self.vel_y >= 0:
                    # Landing on top of platform
                    self.y = platform.rect.top - self.height
                    self.vel_y = 0
                    self.on_ground = True
                elif min_overlap == overlap_bottom and self.vel_y < 0:
                    # Hitting platform from below
                    self.y = platform.rect.bottom
                    self.vel_y = 0
                elif min_overlap == overlap_left and self.vel_x > 0:
                    # Hitting platform from the left
                    self.x = platform.rect.left - self.width
                elif min_overlap == overlap_right and self.vel_x < 0:
                    # Hitting platform from the right
                    self.x = platform.rect.right
                    
        # Ground collision
        if self.y + self.height >= SCREEN_HEIGHT - 50:
            self.y = SCREEN_HEIGHT - 50 - self.height
            self.vel_y = 0
            self.on_ground = True
            
        # Collect coins
        for coin in coins[:]:
            if player_rect.colliderect(coin.rect):
                coins.remove(coin)
                self.score += 100
                
        # Enemy collision
        for enemy in enemies[:]:  # Use slice to allow modification during iteration
            if player_rect.colliderect(enemy.rect):
                if self.vel_y > 0 and self.y < enemy.y:  # Jump on enemy
                    self.vel_y = JUMP_STRENGTH // 2
                    self.score += 200
                    enemies.remove(enemy)  # Remove enemy immediately
                else:  # Hit by enemy - respawn
                    self.respawn()
    
    def respawn(self):
        """Reset player to spawn position and lose a life"""
        self.lives -= 1
        self.score = max(0, self.score - 50)  # Lose 50 points, but don't go below 0
        if self.lives <= 0:
            self.dead = True
        else:
            self.x = self.spawn_x
            self.y = self.spawn_y
            self.vel_x = 0
            self.vel_y = 0
            self.on_ground = False
        
    def draw(self, screen):
        if self.dead:
            return
            
        # Create a small surface for pixel-perfect drawing
        player_surface = pygame.Surface((self.width // PIXEL_SCALE, self.height // PIXEL_SCALE))
        player_surface.fill(self.color)
        
        # Draw pixelated details
        # Hat
        pygame.draw.rect(player_surface, BLACK, (1, 0, 6, 2))
        
        # Eyes
        if self.facing_right:
            pygame.draw.rect(player_surface, WHITE, (5, 3, 2, 2))
            pygame.draw.rect(player_surface, BLACK, (6, 3, 1, 1))
        else:
            pygame.draw.rect(player_surface, WHITE, (1, 3, 2, 2))
            pygame.draw.rect(player_surface, BLACK, (1, 3, 1, 1))
            
        # Overalls/clothes details
        pygame.draw.rect(player_surface, BLACK, (2, 6, 4, 1))
        pygame.draw.rect(player_surface, BLACK, (1, 8, 1, 2))
        pygame.draw.rect(player_surface, BLACK, (6, 8, 1, 2))
        
        # Scale up the surface
        scaled_surface = pygame.transform.scale(player_surface, (self.width, self.height))
        screen.blit(scaled_surface, (self.x, self.y))

class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        
    def draw(self, screen):
        # Create pixelated brick pattern
        brick_size = 16
        for i in range(0, self.rect.width, brick_size):
            for j in range(0, self.rect.height, brick_size):
                brick_rect = pygame.Rect(self.rect.x + i, self.rect.y + j, brick_size, brick_size)
                pygame.draw.rect(screen, BRICK_RED, brick_rect)
                # Pixelated brick outline
                pygame.draw.rect(screen, (140, 12, 0), brick_rect, 2)
                # Inner highlight
                pygame.draw.rect(screen, (200, 20, 0), (brick_rect.x + 2, brick_rect.y + 2, brick_size - 4, brick_size - 4))

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.animation_timer = 0
        
    def update(self):
        self.animation_timer += 1
        
    def draw(self, screen):
        # Pixelated animated coin
        offset = int(math.sin(self.animation_timer * 0.2) * 2)
        coin_rect = pygame.Rect(self.rect.x, self.rect.y + offset, 20, 20)
        
        # Create coin sprite
        pygame.draw.rect(screen, COIN_YELLOW, coin_rect)
        pygame.draw.rect(screen, (200, 148, 0), coin_rect, 2)
        
        # Inner details
        inner_rect = pygame.Rect(coin_rect.x + 4, coin_rect.y + 4, 12, 12)
        pygame.draw.rect(screen, (255, 220, 50), inner_rect)
        
        # Center symbol
        center_rect = pygame.Rect(coin_rect.x + 8, coin_rect.y + 8, 4, 4)
        pygame.draw.rect(screen, (200, 148, 0), center_rect)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 24
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.vel_x = random.choice([-2, 2])
        self.animation_timer = 0
        self.alive = True
        
    def update(self, platforms):
        if not self.alive:
            return
            
        self.animation_timer += 1
        self.x += self.vel_x
        
        # Bounce off screen edges
        if self.x <= 0 or self.x + self.width >= SCREEN_WIDTH:
            self.vel_x *= -1
            
        # Simple platform collision
        self.rect.x = self.x
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                self.vel_x *= -1
                break
                
        self.rect.x = self.x
        self.rect.y = self.y
        
    def hit(self):
        self.alive = False
        
    def draw(self, screen):
        if not self.alive:
            return
            
        # Create pixelated enemy (Goomba-style)
        enemy_surface = pygame.Surface((self.width, self.height))
        color = (139, 69, 19) if self.animation_timer % 60 < 30 else (160, 82, 45)
        enemy_surface.fill(color)
        
        # Mushroom cap
        pygame.draw.rect(enemy_surface, color, (0, 0, self.width, self.height // 2))
        pygame.draw.rect(enemy_surface, (100, 50, 10), (0, 0, self.width, self.height // 2), 2)
        
        # Body
        body_color = (222, 173, 98)
        pygame.draw.rect(enemy_surface, body_color, (4, self.height // 2, self.width - 8, self.height // 2))
        
        # Eyes (pixelated)
        pygame.draw.rect(enemy_surface, BLACK, (4, 6, 3, 3))
        pygame.draw.rect(enemy_surface, BLACK, (17, 6, 3, 3))
        pygame.draw.rect(enemy_surface, WHITE, (5, 7, 1, 1))
        pygame.draw.rect(enemy_surface, WHITE, (18, 7, 1, 1))
        
        # Feet
        pygame.draw.rect(enemy_surface, (139, 69, 19), (2, self.height - 4, 4, 4))
        pygame.draw.rect(enemy_surface, (139, 69, 19), (18, self.height - 4, 4, 4))
        
        screen.blit(enemy_surface, (self.x, self.y))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Jump Bros - Nintendo-Style Multiplayer Platformer")
        self.clock = pygame.time.Clock()
        self.game_over = False
        self.title_screen = True
        self.winner_text = ""
        self.current_level = 1
        self.max_level = 3
        self.level_complete = False
        
        # Create players (spawn them on the ground)
        self.player1 = Player(100, SCREEN_HEIGHT - 50 - 48, MARIO_RED, {
            'left': pygame.K_a,
            'right': pygame.K_d,
            'jump': pygame.K_w
        })
        
        self.player2 = Player(300, SCREEN_HEIGHT - 50 - 48, LUIGI_GREEN, {
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT,
            'jump': pygame.K_UP
        })
        
        self.setup_level(self.current_level)
        
        self.font = pygame.font.Font(None, 36)
        
    def setup_level(self, level_num):
        """Setup platforms, coins, and enemies for a specific level"""
        if level_num == 1:
            # Level 1 - Basic platforms
            self.platforms = [
                Platform(200, 600, 200, 32),
                Platform(500, 500, 150, 32),
                Platform(700, 400, 200, 32),
                Platform(300, 350, 100, 32),
                Platform(800, 250, 150, 32),
                Platform(50, 200, 132, 32),
            ]
            
            coin_positions = [
                (250, 550), (550, 450), (750, 350), (350, 300), (850, 200), (100, 150)
            ]
            
            enemy_positions = [
                (250, 576), (550, 476), (750, 376)
            ]
            
        elif level_num == 2:
            # Level 2 - More challenging layout
            self.platforms = [
                Platform(150, 650, 100, 32),
                Platform(350, 550, 100, 32),
                Platform(550, 450, 100, 32),
                Platform(750, 350, 100, 32),
                Platform(200, 300, 120, 32),
                Platform(500, 200, 120, 32),
                Platform(800, 150, 120, 32),
                Platform(100, 100, 100, 32),
                Platform(195, 240, 32, 120),  # Vertical platform
                Platform(620, 200, 80, 32),   # Extra platform in circled area
            ]
            
            coin_positions = [
                (175, 600), (375, 500), (575, 400), (775, 300), 
                (230, 250), (530, 150), (830, 100), (125, 50)
            ]
            
            enemy_positions = [
                (175, 626), (375, 526), (575, 426), (775, 326), (530, 176)
            ]
            
        elif level_num == 3:
            # Level 3 - Expert level with many platforms
            self.platforms = [
                Platform(100, 650, 80, 32),
                Platform(250, 600, 80, 32),
                Platform(400, 550, 80, 32),
                Platform(550, 500, 80, 32),
                Platform(700, 450, 80, 32),
                Platform(850, 400, 80, 32),
                Platform(750, 300, 100, 32),
                Platform(500, 250, 100, 32),
                Platform(250, 200, 100, 32),
                Platform(50, 150, 100, 32),
                Platform(400, 100, 200, 32),
            ]
            
            coin_positions = [
                (125, 600), (275, 550), (425, 500), (575, 450), (725, 400), (875, 350),
                (775, 250), (525, 200), (275, 150), (75, 100), (450, 50), (525, 50)
            ]
            
            enemy_positions = [
                (125, 626), (275, 576), (425, 526), (575, 476), (725, 426),
                (775, 276), (525, 226), (275, 176), (450, 76)
            ]
        
        # Create coins for this level
        self.coins = []
        for x, y in coin_positions:
            self.coins.append(Coin(x, y))
            
        # Create enemies for this level
        self.enemies = []
        for x, y in enemy_positions:
            self.enemies.append(Enemy(x, y))
            
        # Reset players to spawn positions
        self.player1.x = self.player1.spawn_x
        self.player1.y = self.player1.spawn_y
        self.player1.vel_x = 0
        self.player1.vel_y = 0
        self.player1.on_ground = False
        
        self.player2.x = self.player2.spawn_x
        self.player2.y = self.player2.spawn_y
        self.player2.vel_x = 0
        self.player2.vel_y = 0
        self.player2.on_ground = False
        
        self.game_over = False
        self.level_complete = False
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.title_screen and event.key == pygame.K_SPACE:
                    self.title_screen = False  # Start the game
                elif event.key == pygame.K_r:
                    self.__init__()  # Restart game
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                if self.level_complete:
                    # Check level complete screen buttons
                    restart_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 60, 120, 50)
                    next_level_button_rect = pygame.Rect(SCREEN_WIDTH // 2 + 30, SCREEN_HEIGHT // 2 + 60, 120, 50)
                    
                    if restart_button_rect.collidepoint(mouse_x, mouse_y):
                        self.setup_level(self.current_level)  # Restart current level
                    elif next_level_button_rect.collidepoint(mouse_x, mouse_y):
                        if self.current_level < self.max_level:
                            self.current_level += 1
                            # Reset lives when advancing to next level
                            self.player1.lives = 3
                            self.player2.lives = 3
                            self.player1.dead = False
                            self.player2.dead = False
                            self.setup_level(self.current_level)
                        else:
                            self.__init__()  # Start from level 1 if completed all levels
                            
                elif self.game_over:
                    # Check if restart button was clicked on game over screen
                    restart_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 60, 200, 50)
                    if restart_button_rect.collidepoint(mouse_x, mouse_y):
                        self.setup_level(self.current_level)  # Restart current level
        return True
        
    def update(self):
        if not self.title_screen:
            self.player1.update(self.platforms, self.coins, self.enemies)
            self.player2.update(self.platforms, self.coins, self.enemies)
            
            for coin in self.coins:
                coin.update()
                
            # Update enemies and remove dead ones
            self.enemies = [enemy for enemy in self.enemies if enemy.alive]
            for enemy in self.enemies:
                enemy.update(self.platforms)
            
    def draw(self):
        if self.title_screen:
            draw_title_screen(self.screen, self.font)
            pygame.display.flip()
            return
            
        # Sky background
        self.screen.fill(SKY_BLUE)
        
        # Draw pixelated clouds
        for i in range(0, SCREEN_WIDTH + 100, 200):
            # Main cloud body (pixelated)
            cloud_rects = [
                pygame.Rect(i - 40, 110, 16, 16),
                pygame.Rect(i - 24, 110, 16, 16),
                pygame.Rect(i - 8, 110, 16, 16),
                pygame.Rect(i + 8, 110, 16, 16),
                pygame.Rect(i - 32, 94, 16, 16),
                pygame.Rect(i - 16, 94, 16, 16),
                pygame.Rect(i, 94, 16, 16),
                pygame.Rect(i - 24, 78, 16, 16),
                pygame.Rect(i - 8, 78, 16, 16),
            ]
            for rect in cloud_rects:
                pygame.draw.rect(self.screen, WHITE, rect)
            
        # Ground
        pygame.draw.rect(self.screen, GROUND_GREEN, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
        
        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen)
            
        # Draw coins
        for coin in self.coins:
            coin.draw(self.screen)
            
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
            
        # Draw players
        self.player1.draw(self.screen)
        self.player2.draw(self.screen)
        
        # Draw UI
        score1_text = self.font.render(f"Player 1: {self.player1.score} | Lives: {self.player1.lives}", True, WHITE)
        score2_text = self.font.render(f"Player 2: {self.player2.score} | Lives: {self.player2.lives}", True, WHITE)
        controls_text = self.font.render("P1: WASD | P2: Arrow Keys | R: Restart", True, WHITE)
        
        self.screen.blit(score1_text, (10, 10))
        self.screen.blit(score2_text, (10, 50))
        self.screen.blit(controls_text, (10, SCREEN_HEIGHT - 40))
        
        # Level complete check - need all coins AND all enemies eliminated
        if len(self.coins) == 0 and len(self.enemies) == 0 and not self.player1.dead and not self.player2.dead:
            self.level_complete = True
            
            if self.player1.score > self.player2.score:
                self.winner_text = "Player 1 Wins Level!"
            elif self.player2.score > self.player1.score:
                self.winner_text = "Player 2 Wins Level!"
            else:
                self.winner_text = "Level Complete - Tie!"
            
            # Draw level complete screen
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            # Level complete text
            level_text = self.font.render(f"Level {self.current_level} Complete!", True, COIN_YELLOW)
            level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
            
            # Winner text
            winner_surface = self.font.render(self.winner_text, True, WHITE)
            winner_rect = winner_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            
            # Pixelated border around text
            border_rect = level_rect.union(winner_rect).inflate(40, 20)
            pygame.draw.rect(self.screen, WHITE, border_rect)
            pygame.draw.rect(self.screen, BLACK, border_rect, 4)
            self.screen.blit(level_text, level_rect)
            self.screen.blit(winner_surface, winner_rect)
            
            # Buttons
            restart_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 60, 120, 50)
            next_level_button_rect = pygame.Rect(SCREEN_WIDTH // 2 + 30, SCREEN_HEIGHT // 2 + 60, 120, 50)
            
            # Restart button
            pygame.draw.rect(self.screen, MARIO_RED, restart_button_rect)
            pygame.draw.rect(self.screen, WHITE, restart_button_rect, 4)
            restart_text = self.font.render("RESTART", True, WHITE)
            restart_text_rect = restart_text.get_rect(center=restart_button_rect.center)
            self.screen.blit(restart_text, restart_text_rect)
            
            # Next level button
            if self.current_level < self.max_level:
                pygame.draw.rect(self.screen, LUIGI_GREEN, next_level_button_rect)
                pygame.draw.rect(self.screen, WHITE, next_level_button_rect, 4)
                next_text = self.font.render("NEXT", True, WHITE)
                next_text_rect = next_text.get_rect(center=next_level_button_rect.center)
                self.screen.blit(next_text, next_text_rect)
            else:
                pygame.draw.rect(self.screen, COIN_YELLOW, next_level_button_rect)
                pygame.draw.rect(self.screen, WHITE, next_level_button_rect, 4)
                complete_text = pygame.font.Font(None, 24).render("COMPLETE!", True, BLACK)
                complete_text_rect = complete_text.get_rect(center=next_level_button_rect.center)
                self.screen.blit(complete_text, complete_text_rect)
            
            # Instructions
            instruction_text = pygame.font.Font(None, 24).render("Click buttons or press R to restart", True, WHITE)
            instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 130))
            self.screen.blit(instruction_text, instruction_rect)
            
        # Game over check - one or both players dead
        elif self.player1.dead or self.player2.dead:
            self.game_over = True
            
            if self.player1.dead and self.player2.dead:
                self.winner_text = "Both Players Lost!"
            elif self.player1.dead:
                self.winner_text = "Player 2 Wins!"
            elif self.player2.dead:
                self.winner_text = "Player 1 Wins!"
            
            # Draw game over screen with pixelated style
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            # Game over text
            game_over_text = self.font.render("Game Over!", True, MARIO_RED)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
            
            # Winner text
            winner_surface = self.font.render(self.winner_text, True, WHITE)
            winner_rect = winner_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            
            # Pixelated border around winner text
            border_rect = game_over_rect.union(winner_rect).inflate(40, 20)
            pygame.draw.rect(self.screen, WHITE, border_rect)
            pygame.draw.rect(self.screen, BLACK, border_rect, 4)
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(winner_surface, winner_rect)
            
            # Restart button
            restart_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 60, 200, 50)
            pygame.draw.rect(self.screen, MARIO_RED, restart_button_rect)
            pygame.draw.rect(self.screen, WHITE, restart_button_rect, 4)
            
            restart_text = self.font.render("RESTART", True, WHITE)
            restart_text_rect = restart_text.get_rect(center=restart_button_rect.center)
            self.screen.blit(restart_text, restart_text_rect)
            
            # Instructions
            instruction_text = pygame.font.Font(None, 24).render("Click RESTART or press R", True, WHITE)
            instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 130))
            self.screen.blit(instruction_text, instruction_rect)
            
        # Display level info and remaining objectives
        level_text = self.font.render(f"Level {self.current_level}/{self.max_level}", True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH - 150, 10))
        
        coins_left = len(self.coins)
        enemies_left = len(self.enemies)
        objective_text = self.font.render(f"Coins: {coins_left} | Enemies: {enemies_left}", True, WHITE)
        self.screen.blit(objective_text, (SCREEN_WIDTH // 2 - 100, 10))
            
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