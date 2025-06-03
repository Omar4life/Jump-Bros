
import pygame

def create_game_logo(scale=1):
    """Create a pixelated Nintendo-style game logo"""
    # Logo dimensions
    logo_width = 64 * scale
    logo_height = 32 * scale
    
    # Create surface for the logo
    logo_surface = pygame.Surface((logo_width, logo_height))
    logo_surface.fill((0, 0, 0, 0))  # Transparent background
    
    # Nintendo-like colors
    red = (228, 0, 88)
    green = (0, 168, 68)
    yellow = (252, 188, 0)
    white = (255, 255, 255)
    black = (0, 0, 0)
    blue = (92, 148, 252)
    
    # Create pixelated "JUMP BROS" text
    pixel_size = 2 * scale
    
    # Letter J
    j_pattern = [
        [0,0,1,1,1,1],
        [0,0,0,0,1,1],
        [0,0,0,0,1,1],
        [0,0,0,0,1,1],
        [1,1,0,0,1,1],
        [0,1,1,1,1,0]
    ]
    
    # Letter U
    u_pattern = [
        [1,1,0,0,1,1],
        [1,1,0,0,1,1],
        [1,1,0,0,1,1],
        [1,1,0,0,1,1],
        [1,1,0,0,1,1],
        [0,1,1,1,1,0]
    ]
    
    # Letter M
    m_pattern = [
        [1,1,0,0,0,0,1,1],
        [1,1,1,0,0,1,1,1],
        [1,1,1,1,1,1,1,1],
        [1,1,0,1,1,0,1,1],
        [1,1,0,0,0,0,1,1],
        [1,1,0,0,0,0,1,1]
    ]
    
    # Letter P
    p_pattern = [
        [1,1,1,1,1,0],
        [1,1,0,0,1,1],
        [1,1,0,0,1,1],
        [1,1,1,1,1,0],
        [1,1,0,0,0,0],
        [1,1,0,0,0,0]
    ]
    
    # Draw "JUMP" in red
    x_offset = 2 * scale
    y_offset = 2 * scale
    
    # J
    for y, row in enumerate(j_pattern):
        for x, pixel in enumerate(row):
            if pixel:
                rect = pygame.Rect(x_offset + x * pixel_size, y_offset + y * pixel_size, pixel_size, pixel_size)
                pygame.draw.rect(logo_surface, red, rect)
    
    # U
    x_offset += 8 * pixel_size
    for y, row in enumerate(u_pattern):
        for x, pixel in enumerate(row):
            if pixel:
                rect = pygame.Rect(x_offset + x * pixel_size, y_offset + y * pixel_size, pixel_size, pixel_size)
                pygame.draw.rect(logo_surface, red, rect)
    
    # M
    x_offset += 8 * pixel_size
    for y, row in enumerate(m_pattern):
        for x, pixel in enumerate(row):
            if pixel:
                rect = pygame.Rect(x_offset + x * pixel_size, y_offset + y * pixel_size, pixel_size, pixel_size)
                pygame.draw.rect(logo_surface, red, rect)
    
    # P
    x_offset += 10 * pixel_size
    for y, row in enumerate(p_pattern):
        for x, pixel in enumerate(row):
            if pixel:
                rect = pygame.Rect(x_offset + x * pixel_size, y_offset + y * pixel_size, pixel_size, pixel_size)
                pygame.draw.rect(logo_surface, red, rect)
    
    # Draw "BROS" in green below
    x_offset = 2 * scale
    y_offset = 16 * scale
    
    # B
    b_pattern = [
        [1,1,1,1,1,0],
        [1,1,0,0,1,1],
        [1,1,1,1,1,0],
        [1,1,1,1,1,0],
        [1,1,0,0,1,1],
        [1,1,1,1,1,0]
    ]
    
    # R
    r_pattern = [
        [1,1,1,1,1,0],
        [1,1,0,0,1,1],
        [1,1,1,1,1,0],
        [1,1,1,0,0,0],
        [1,1,0,1,0,0],
        [1,1,0,0,1,1]
    ]
    
    # O
    o_pattern = [
        [0,1,1,1,1,0],
        [1,1,0,0,1,1],
        [1,1,0,0,1,1],
        [1,1,0,0,1,1],
        [1,1,0,0,1,1],
        [0,1,1,1,1,0]
    ]
    
    # S
    s_pattern = [
        [0,1,1,1,1,1],
        [1,1,0,0,0,0],
        [0,1,1,1,0,0],
        [0,0,0,1,1,0],
        [0,0,0,0,1,1],
        [1,1,1,1,1,0]
    ]
    
    # B
    for y, row in enumerate(b_pattern):
        for x, pixel in enumerate(row):
            if pixel:
                rect = pygame.Rect(x_offset + x * pixel_size, y_offset + y * pixel_size, pixel_size, pixel_size)
                pygame.draw.rect(logo_surface, green, rect)
    
    # R
    x_offset += 8 * pixel_size
    for y, row in enumerate(r_pattern):
        for x, pixel in enumerate(row):
            if pixel:
                rect = pygame.Rect(x_offset + x * pixel_size, y_offset + y * pixel_size, pixel_size, pixel_size)
                pygame.draw.rect(logo_surface, green, rect)
    
    # O
    x_offset += 8 * pixel_size
    for y, row in enumerate(o_pattern):
        for x, pixel in enumerate(row):
            if pixel:
                rect = pygame.Rect(x_offset + x * pixel_size, y_offset + y * pixel_size, pixel_size, pixel_size)
                pygame.draw.rect(logo_surface, green, rect)
    
    # S
    x_offset += 8 * pixel_size
    for y, row in enumerate(s_pattern):
        for x, pixel in enumerate(row):
            if pixel:
                rect = pygame.Rect(x_offset + x * pixel_size, y_offset + y * pixel_size, pixel_size, pixel_size)
                pygame.draw.rect(logo_surface, green, rect)
    
    # Add a decorative border
    pygame.draw.rect(logo_surface, yellow, (0, 0, logo_width, logo_height), 2 * scale)
    
    return logo_surface

def draw_title_screen(screen, font):
    """Draw a title screen with the logo"""
    screen.fill((92, 148, 252))  # Sky blue background
    
    # Create and draw the logo
    logo = create_game_logo(3)  # 3x scale for title screen
    logo_rect = logo.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50))
    screen.blit(logo, logo_rect)
    
    # Add "Press any key to start" text
    start_text = font.render("Press SPACE to Start!", True, (255, 255, 255))
    start_rect = start_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 100))
    
    # Add black outline to text
    for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
        outline_text = font.render("Press SPACE to Start!", True, (0, 0, 0))
        screen.blit(outline_text, (start_rect.x + dx, start_rect.y + dy))
    
    screen.blit(start_text, start_rect)
    
    # Add controls info
    controls_font = pygame.font.Font(None, 24)
    controls_text = controls_font.render("P1: WASD | P2: Arrow Keys", True, (255, 255, 255))
    controls_rect = controls_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 150))
    
    # Add black outline
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        outline_text = controls_font.render("P1: WASD | P2: Arrow Keys", True, (0, 0, 0))
        screen.blit(outline_text, (controls_rect.x + dx, controls_rect.y + dy))
    
    screen.blit(controls_text, controls_rect)
