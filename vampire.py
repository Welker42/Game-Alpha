import pygame
import random
import math
import sys

# Inicialização do Pygame
pygame.init()

# Constantes
WIDTH, HEIGHT = 1920, 1080
PLAYER_SIZE = 100
ENEMY_SIZE = 30
PROJECTILE_SIZE = 20
BACKGROUND_COLOR = (0, 0, 0)
BACKGROUND_IMAGE_PATH = 'background.jpg'
PLAYER_IMAGE_PATH = 'player.png'
ENEMY_IMAGE_PATH = 'enemy.png'  # Adiciona o caminho para a imagem do inimigo
FPS = 60
PLAYER_SPEED = 8
MIN_ENEMY_SPEED = 2
MAX_ENEMY_SPEED = 3
PROJECTILE_SPEED = 10
SHOOT_INTERVAL = 500
PROJECTILE_LIFE_TIME = 2000
ENEMY_SPAWN_INTERVAL = 5000
ENEMY_INCREASE_INTERVAL = 30000
ENEMIES_INITIAL_COUNT = 5
ENEMY_INCREMENT_FACTOR = 1.5
PROJECTILE_DAMAGE = 50
ENEMY_INITIAL_HEALTH = 100
XP_PER_ENEMY = 20
XP_FOR_LEVEL_UP = 100

# Configuração da tela
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Alpha 0.15")

# Carregar imagens
try:
    background_image = pygame.image.load(BACKGROUND_IMAGE_PATH)
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
except pygame.error as e:
    print(f"Erro ao carregar imagem de fundo: {e}")
    pygame.quit()
    sys.exit()

try:
    player_image = pygame.image.load(PLAYER_IMAGE_PATH)
    player_image = pygame.transform.scale(player_image, (PLAYER_SIZE, PLAYER_SIZE))
except pygame.error as e:
    print(f"Erro ao carregar imagem do jogador: {e}")
    pygame.quit()
    sys.exit()

try:
    enemy_image = pygame.image.load(ENEMY_IMAGE_PATH)
    enemy_image = pygame.transform.scale(enemy_image, (ENEMY_SIZE, ENEMY_SIZE))
except pygame.error as e:
    print(f"Erro ao carregar imagem do inimigo: {e}")
    pygame.quit()
    sys.exit()

# Função para criar inimigos
def create_enemy():
    border = random.choice(['top', 'bottom', 'left', 'right'])
    if border == 'top':
        x_pos = random.randint(0, WIDTH - ENEMY_SIZE)
        y_pos = 0
    elif border == 'bottom':
        x_pos = random.randint(0, WIDTH - ENEMY_SIZE)
        y_pos = HEIGHT - ENEMY_SIZE
    elif border == 'left':
        x_pos = 0
        y_pos = random.randint(0, HEIGHT - ENEMY_SIZE)
    elif border == 'right':
        x_pos = WIDTH - ENEMY_SIZE
        y_pos = random.randint(0, HEIGHT - ENEMY_SIZE)
    
    speed = random.uniform(MIN_ENEMY_SPEED, MAX_ENEMY_SPEED)
    health = ENEMY_INITIAL_HEALTH
    return [x_pos, y_pos, speed, health]

# Função para criar projéteis
def create_projectile(player_x, player_y, direction):
    current_time = pygame.time.get_ticks()
    return [player_x + PLAYER_SIZE // 2 - PROJECTILE_SIZE // 2,
            player_y + PLAYER_SIZE // 2 - PROJECTILE_SIZE // 2,
            direction,
            current_time]

# Função para desenhar o jogador
def draw_player(x, y):
    screen.blit(player_image, (x, y))

# Função para desenhar inimigos
def draw_enemy(x, y):
    screen.blit(enemy_image, (x, y))  # Usa a imagem do inimigo

# Função para desenhar projéteis
def draw_projectile(x, y):
    pygame.draw.rect(screen, (0, 0, 255), [x, y, PROJECTILE_SIZE, PROJECTILE_SIZE])

# Função para desenhar o cronômetro
def draw_timer(start_time):
    current_time = pygame.time.get_ticks()
    elapsed_time = current_time - start_time
    elapsed_seconds = elapsed_time // 1000

    font = pygame.font.Font(None, 36)
    timer_text = font.render(f"Tempo Vivo: {elapsed_seconds}s", True, (255, 255, 255))
    screen.blit(timer_text, (10, 10))

# Função para desenhar o contador de inimigos mortos
def draw_killed_enemies(count):
    font = pygame.font.Font(None, 36)
    killed_text = font.render(f"Inimigos Mortos: {count}", True, (255, 255, 255))
    screen.blit(killed_text, (10, 50))

# Função para desenhar o XP e nível
def draw_xp_and_level(xp, level):
    font = pygame.font.Font(None, 36)
    xp_text = font.render(f"XP: {xp}/{XP_FOR_LEVEL_UP}", True, (255, 255, 255))
    level_text = font.render(f"Nível: {level}", True, (255, 255, 255))
    screen.blit(xp_text, (10, 90))
    screen.blit(level_text, (10, 130))

    xp_bar_width = 200
    xp_percentage = xp / XP_FOR_LEVEL_UP
    pygame.draw.rect(screen, (255, 255, 255), [10, 170, xp_bar_width, 20], 2)
    pygame.draw.rect(screen, (0, 255, 0), [10, 170, xp_bar_width * xp_percentage, 20])

# Função para desenhar a tela de Game Over
def draw_game_over():
    font = pygame.font.Font(None, 74)
    game_over_text = font.render("Game Over", True, (255, 0, 0))
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))

    pygame.display.update()
    pygame.time.delay(2000)  # Atraso para que o jogador possa ver a tela de Game Over

# Função para desenhar o menu
def draw_menu():
    screen.fill(BACKGROUND_COLOR)
    font = pygame.font.Font(None, 74)
    title_text = font.render("Menu", True, (255, 255, 255))
    start_text = font.render("Pressione ENTER para iniciar", True, (255, 255, 255))
    quit_text = font.render("Pressione ESC para sair", True, (255, 255, 255))
    
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - title_text.get_height() // 2 - 50))
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 - start_text.get_height() // 2 + 50))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 - quit_text.get_height() // 2 + 100))
    
    pygame.display.update()

# Função para mover o jogador
def move_player(x, y, dx, dy):
    x += dx
    y += dy
    x = max(0, min(WIDTH - PLAYER_SIZE, x))
    y = max(0, min(HEIGHT - PLAYER_SIZE, y))
    return x, y

# Função para mover inimigos
def move_enemies(player_x, player_y, enemies):
    new_enemies = []
    for ex, ey, speed, health in enemies:
        dx = player_x - ex
        dy = player_y - ey
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            dx /= distance
            dy /= distance
        ex += dx * speed
        ey += dy * speed

        if 0 <= ex <= WIDTH - ENEMY_SIZE and 0 <= ey <= HEIGHT - ENEMY_SIZE:
            new_enemies.append([ex, ey, speed, health])
    return new_enemies

# Função para mover projéteis e verificar colisões
def move_and_check_projectiles(projectiles, enemies):
    new_projectiles = []
    remaining_enemies = []
    enemy_killed = False

    for ex, ey, speed, health in enemies:
        remaining_enemies.append([ex, ey, speed, health])
    
    current_time = pygame.time.get_ticks()
    for px, py, direction, creation_time in projectiles:
        px += direction[0] * PROJECTILE_SPEED
        py += direction[1] * PROJECTILE_SPEED

        if current_time - creation_time > PROJECTILE_LIFE_TIME:
            continue

        projectile_rect = pygame.Rect(px, py, PROJECTILE_SIZE, PROJECTILE_SIZE)
        projectile_destroyed = False

        for i, (ex, ey, speed, health) in enumerate(remaining_enemies):
            enemy_rect = pygame.Rect(ex, ey, ENEMY_SIZE, ENEMY_SIZE)
            if projectile_rect.colliderect(enemy_rect):
                projectile_destroyed = True
                health -= PROJECTILE_DAMAGE
                if health <= 0:
                    remaining_enemies.pop(i)
                    enemy_killed = True
                    break
                else:
                    remaining_enemies[i][3] = health
                break

        if 0 <= px <= WIDTH and 0 <= py <= HEIGHT and not projectile_destroyed:
            new_projectiles.append([px, py, direction, creation_time])

    return new_projectiles, remaining_enemies, enemy_killed

# Função para verificar colisões entre o jogador e inimigos
def check_collision(player_x, player_y, enemies):
    for ex, ey, _, _ in enemies:
        if (player_x < ex + ENEMY_SIZE and
            player_x + PLAYER_SIZE > ex and
            player_y < ey + ENEMY_SIZE and
            player_y + PLAYER_SIZE > ey):
            return True
    return False

# Função para o loop principal do jogo
def game_loop():
    global PLAYER_SPEED

    player_x, player_y = WIDTH // 2, HEIGHT // 2
    dx, dy = 0, 0

    running = True
    clock = pygame.time.Clock()

    enemies = [create_enemy() for _ in range(ENEMIES_INITIAL_COUNT)]
    projectiles = []
    last_shot_time = pygame.time.get_ticks()
    last_enemy_spawn_time = pygame.time.get_ticks()
    last_enemy_increase_time = pygame.time.get_ticks()
    start_time = pygame.time.get_ticks()
    killed_enemies_count = 0
    xp = 0
    level = 1

    # Define a quantidade inicial de inimigos a ser criada
    enemies_to_spawn = ENEMIES_INITIAL_COUNT

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    dx = -PLAYER_SPEED
                elif event.key == pygame.K_d:
                    dx = PLAYER_SPEED
                elif event.key == pygame.K_w:
                    dy = -PLAYER_SPEED
                elif event.key == pygame.K_s:
                    dy = PLAYER_SPEED
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a or event.key == pygame.K_d:
                    dx = 0
                if event.key == pygame.K_w or event.key == pygame.K_s:
                    dy = 0

        player_x, player_y = move_player(player_x, player_y, dx, dy)
        enemies = move_enemies(player_x, player_y, enemies)

        current_time = pygame.time.get_ticks()

        # Adiciona novos inimigos a cada 5 segundos
        if current_time - last_enemy_spawn_time >= ENEMY_SPAWN_INTERVAL:
            new_enemies = [create_enemy() for _ in range(enemies_to_spawn)]
            enemies.extend(new_enemies)
            last_enemy_spawn_time = current_time

        # Aumenta a quantidade de inimigos a cada 30 segundos
        if current_time - last_enemy_increase_time >= ENEMY_INCREASE_INTERVAL:
            enemies_to_spawn = int(enemies_to_spawn * ENEMY_INCREMENT_FACTOR)
            last_enemy_increase_time = current_time

        # Lógica de tiro
        if current_time - last_shot_time >= SHOOT_INTERVAL:
            direction = pygame.math.Vector2(pygame.mouse.get_pos()) - pygame.math.Vector2(player_x, player_y)
            direction = direction.normalize() if direction.length() > 0 else pygame.math.Vector2(1, 0)
            projectiles.append(create_projectile(player_x, player_y, direction))
            last_shot_time = current_time

        projectiles, enemies, enemy_killed = move_and_check_projectiles(projectiles, enemies)

        if enemy_killed:
            killed_enemies_count += 1
            xp += XP_PER_ENEMY
            if xp >= XP_FOR_LEVEL_UP:
                level += 1
                PLAYER_SPEED += 2
                xp = 0

        if check_collision(player_x, player_y, enemies):
            draw_game_over()
            return  # Retorna ao menu após a morte

        screen.blit(background_image, (0, 0))
        draw_player(player_x, player_y)
        for ex, ey, _, _ in enemies:
            draw_enemy(ex, ey)
        for px, py, _, _ in projectiles:
            draw_projectile(px, py)
        draw_timer(start_time)
        draw_killed_enemies(killed_enemies_count)
        draw_xp_and_level(xp, level)

        pygame.display.update()
        clock.tick(FPS)

# Função para o loop principal do menu
def menu_loop():
    running = True
    while running:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_loop()  # Inicia o jogo
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

if __name__ == "__main__":
    menu_loop()  # Inicia o menu
