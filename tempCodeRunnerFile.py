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
            turret = TurretEnemy(turret_x, turret_y, health=15, shoot_interval=90, projectile_speed=6)
            self.enemies.append(turret)