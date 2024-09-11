import pygame
import random
import math
import sys

# Inicialização do Pygame
pygame.init()

# Constantes
MAP_WIDTH, MAP_HEIGHT = 3840, 2160  # Tamanho do mapa
WIDTH, HEIGHT = 1920, 1080  # Tamanho da tela
PLAYER_SIZE = 120
ENEMY_SIZE = 50
PROJECTILE_SIZE = 35
BACKGROUND_COLOR = (0, 0, 0)
BACKGROUND_IMAGE_PATH = 'images/background.jpg'
PLAYER_IMAGE_PATH = 'player.png'
ENEMY_IMAGE_PATH = 'images/enemy1.png'
PROJECTILE_IMAGE_PATH = 'images/projectile.png'
FPS = 60
PLAYER_SPEED = 5
MIN_ENEMY_SPEED = 2
MAX_ENEMY_SPEED = 6
PROJECTILE_SPEED = 7
SHOOT_INTERVAL = 500  # Intervalo de disparo automático em milissegundos
PROJECTILE_LIFE_TIME = 2000  # Tempo de vida dos projéteis em milissegundos
LEVEL_DURATION = 60000  # Duração da fase em milissegundos (60 segundos)
ENEMY_SPAWN_INTERVAL = 5000  # Intervalo para adicionar novos inimigos em milissegundos
ENEMY_INCREASE_INTERVAL = 30000  # Intervalo para dobrar o número de inimigos em milissegundos
ENEMIES_INITIAL_COUNT = 5

# Configuração da tela
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jogo com Mapa Gigante")

# Carregar imagens
try:
    background_image = pygame.image.load(BACKGROUND_IMAGE_PATH)
    background_image = pygame.transform.scale(background_image, (MAP_WIDTH, MAP_HEIGHT))
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
    
try:
    projectile_image = pygame.image.load(PROJECTILE_IMAGE_PATH)
    projectile_image = pygame.transform.scale(projectile_image, (PROJECTILE_SIZE, PROJECTILE_SIZE))
    print("Imagem do projétil carregada com sucesso.")
except pygame.error as e:
    print(f"Erro ao carregar imagem do projétil: {e}")
    pygame.quit()
    sys.exit()

# Função para criar inimigos com velocidade aleatória
def create_enemy():
    border = random.choice(['top', 'bottom', 'left', 'right'])

    if border == 'top':
        x_pos = random.randint(0, MAP_WIDTH - ENEMY_SIZE)
        y_pos = 0
    elif border == 'bottom':
        x_pos = random.randint(0, MAP_WIDTH - ENEMY_SIZE)
        y_pos = MAP_HEIGHT - ENEMY_SIZE
    elif border == 'left':
        x_pos = 0
        y_pos = random.randint(0, MAP_HEIGHT - ENEMY_SIZE)
    elif border == 'right':
        x_pos = MAP_WIDTH - ENEMY_SIZE
        y_pos = random.randint(0, MAP_HEIGHT - ENEMY_SIZE)

    speed = random.uniform(MIN_ENEMY_SPEED, MAX_ENEMY_SPEED)
    return [x_pos, y_pos, speed]

# Função para criar projéteis
def create_projectile(player_x, player_y, direction):
    current_time = pygame.time.get_ticks()
    return [player_x + PLAYER_SIZE // 2 - PROJECTILE_SIZE // 2,
            player_y + PLAYER_SIZE // 2 - PROJECTILE_SIZE // 2,
            direction,
            current_time]  # Adiciona o timestamp de criação

# Função para desenhar o jogador usando a imagem
def draw_player(x, y):
    screen.blit(player_image, (x, y))

# Função para desenhar inimigos usando a imagem
def draw_enemy(x, y):
    screen.blit(enemy_image, (x, y))

# Função para desenhar projéteis
def draw_projectile(x, y):
    screen.blit(projectile_image, (x, y))

# Função para desenhar o cronômetro
def draw_timer(start_time):
    current_time = pygame.time.get_ticks()
    elapsed_time = current_time - start_time
    elapsed_seconds = elapsed_time // 1000

    font = pygame.font.Font(None, 36)
    timer_text = font.render(f"Tempo Vivo: {elapsed_seconds}s", True, (255, 255, 255))
    screen.blit(timer_text, (10, 10))

# Função para mover o jogador
def move_player(x, y, dx, dy):
    x += dx
    y += dy
    x = max(0, min(MAP_WIDTH - PLAYER_SIZE, x))
    y = max(0, min(MAP_HEIGHT - PLAYER_SIZE, y))
    return x, y

# Função para mover inimigos com velocidade aleatória
def move_enemies(player_x, player_y, enemies):
    new_enemies = []
    for ex, ey, speed in enemies:
        dx = player_x - ex
        dy = player_y - ey
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            dx /= distance
            dy /= distance
        ex += dx * speed
        ey += dy * speed

        if 0 <= ex <= MAP_WIDTH - ENEMY_SIZE and 0 <= ey <= MAP_HEIGHT - ENEMY_SIZE:
            new_enemies.append([ex, ey, speed])
    return new_enemies

# Função para mover projéteis e verificar colisões
def move_and_check_projectiles(projectiles, enemies):
    new_projectiles = []
    remaining_enemies = []

    for ex, ey, speed in enemies:
        remaining_enemies.append([ex, ey, speed])  # Preservar todos os inimigos inicialmente
    
    current_time = pygame.time.get_ticks()
    for px, py, direction, creation_time in projectiles:
        # Movimento dos projéteis
        px += direction[0] * PROJECTILE_SPEED
        py += direction[1] * PROJECTILE_SPEED

        # Verificar tempo de vida do projétil
        if current_time - creation_time > PROJECTILE_LIFE_TIME:
            continue  # Ignorar projéteis que passaram do tempo de vida

        projectile_rect = pygame.Rect(px, py, PROJECTILE_SIZE, PROJECTILE_SIZE)
        projectile_destroyed = False

        for ex, ey, _ in remaining_enemies:
            enemy_rect = pygame.Rect(ex, ey, ENEMY_SIZE, ENEMY_SIZE)
            if projectile_rect.colliderect(enemy_rect):
                projectile_destroyed = True
                remaining_enemies.remove([ex, ey, _])
                break

        if 0 <= px <= MAP_WIDTH and 0 <= py <= MAP_HEIGHT and not projectile_destroyed:
            new_projectiles.append([px, py, direction, creation_time])

    return new_projectiles, remaining_enemies

# Função para verificar colisões entre o jogador e inimigos
def check_collision(player_x, player_y, enemies):
    for ex, ey, _ in enemies:
        if (player_x < ex + ENEMY_SIZE and
            player_x + PLAYER_SIZE > ex and
            player_y < ey + ENEMY_SIZE and
            player_y + PLAYER_SIZE > ey):
            return True
    return False

# Função para exibir a tela de Game Over
def show_game_over():
    font = pygame.font.Font(None, 74)
    text = font.render('Game Over', True, (255, 0, 0))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()

    # Aguardar até que o jogador pressione uma tecla
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

# Função para exibir o menu inicial
def show_main_menu():
    font = pygame.font.Font(None, 74)
    text_new_game = font.render('Press N for New Game', True, (255, 255, 255))
    text_quit = font.render('Press Q to Quit', True, (255, 255, 255))

    screen.fill(BACKGROUND_COLOR)
    screen.blit(text_new_game, (WIDTH // 2 - text_new_game.get_width() // 2, HEIGHT // 2 - text_new_game.get_height() // 2 - 50))
    screen.blit(text_quit, (WIDTH // 2 - text_quit.get_width() // 2, HEIGHT // 2 - text_quit.get_height() // 2 + 50))
    pygame.display.flip()

    # Aguardar a escolha do jogador
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    waiting = False
                    return "new_game"
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

# Loop principal do jogo
# Função para encontrar o inimigo mais próximo do jogador
def find_closest_enemy(player_x, player_y, enemies):
    closest_enemy = None
    min_distance = float('inf')
    for ex, ey, _ in enemies:
        distance = math.sqrt((ex - player_x) ** 2 + (ey - player_y) ** 2)
        if distance < min_distance:
            min_distance = distance
            closest_enemy = (ex, ey)
    return closest_enemy

# Função para criar projéteis em direção ao inimigo mais próximo
def create_projectile_towards_enemy(player_x, player_y, enemy_x, enemy_y):
    direction_x = enemy_x - (player_x + PLAYER_SIZE // 2)
    direction_y = enemy_y - (player_y + PLAYER_SIZE // 2)
    distance = math.sqrt(direction_x**2 + direction_y**2)
    if distance > 0:
        direction_x /= distance
        direction_y /= distance
    return create_projectile(player_x, player_y, (direction_x, direction_y))

# Loop principal do jogo
def game_loop():
    player_x, player_y = WIDTH // 2, HEIGHT // 2
    player_dx, player_dy = 0, 0
    initial_enemy_count = ENEMIES_INITIAL_COUNT
    enemies = [create_enemy() for _ in range(initial_enemy_count)]
    projectiles = []

    clock = pygame.time.Clock()
    running = True
    last_shoot_time = pygame.time.get_ticks()
    last_enemy_spawn_time = pygame.time.get_ticks()
    last_enemy_increase_time = pygame.time.get_ticks()
    level_start_time = pygame.time.get_ticks()  # Tempo de início da fase

    # Multiplicador de inimigos
    enemy_multiplier = 1

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Mover o jogador com WSAD
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            player_dx = -PLAYER_SPEED
        elif keys[pygame.K_d]:
            player_dx = PLAYER_SPEED
        else:
            player_dx = 0

        if keys[pygame.K_w]:
            player_dy = -PLAYER_SPEED
        elif keys[pygame.K_s]:
            player_dy = PLAYER_SPEED
        else:
            player_dy = 0

        player_x, player_y = move_player(player_x, player_y, player_dx, player_dy)
        enemies = move_enemies(player_x, player_y, enemies)
        projectiles, enemies = move_and_check_projectiles(projectiles, enemies)

        # Adicionar um novo projétil a cada intervalo de tempo
        current_time = pygame.time.get_ticks()
        if current_time - last_shoot_time >= SHOOT_INTERVAL:
            closest_enemy = find_closest_enemy(player_x, player_y, enemies)
            if closest_enemy:
                enemy_x, enemy_y = closest_enemy
                projectiles.append(create_projectile_towards_enemy(player_x, player_y, enemy_x, enemy_y))
                last_shoot_time = current_time

        # Adicionar novos inimigos a cada 5 segundos
        if current_time - last_enemy_spawn_time >= ENEMY_SPAWN_INTERVAL:
            for _ in range(initial_enemy_count * enemy_multiplier):
                enemies.append(create_enemy())
            last_enemy_spawn_time = current_time

        # Aumentar o número total de inimigos a cada 30 segundos
        if current_time - last_enemy_increase_time >= ENEMY_INCREASE_INTERVAL:
            enemy_multiplier *= 2
            last_enemy_increase_time = current_time

        # Verificar colisões entre o jogador e inimigos
        if check_collision(player_x, player_y, enemies):
            show_game_over()
            return

        # Atualizar a posição da câmera
        camera_x = max(0, min(MAP_WIDTH - WIDTH, player_x - WIDTH // 2))
        camera_y = max(0, min(MAP_HEIGHT - HEIGHT, player_y - HEIGHT // 2))

        # Limpar a tela
        screen.fill(BACKGROUND_COLOR)

        # Desenhar o fundo
        screen.blit(background_image, (-camera_x, -camera_y))

        # Desenhar o cronômetro
        draw_timer(level_start_time)

        # Desenhar o jogador, inimigos e projéteis
        draw_player(player_x - camera_x, player_y - camera_y)
        for ex, ey, _ in enemies:
            draw_enemy(ex - camera_x, ey - camera_y)
        for px, py, _, _ in projectiles:
            draw_projectile(px - camera_x, py - camera_y)

        pygame.display.flip()
        clock.tick(FPS)


def main():
    while True:
        show_main_menu()
        game_loop()

# Iniciar o jogo
if __name__ == "__main__":
    main()
