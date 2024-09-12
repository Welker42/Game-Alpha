import pygame
import random
import math
import sys

# Inicialização do Pygame
pygame.init()

# Função para alternar entre tela cheia e janela
def toggle_fullscreen(is_fullscreen):
    if is_fullscreen:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    return screen, not is_fullscreen

# Função para ajustar o volume da música
def set_volume(volume_level):
    pygame.mixer.music.set_volume(volume_level)

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
MUSIC_PATH = 'sound/background_music.mp3'
FPS = 60
PLAYER_SPEED = 5
MIN_ENEMY_SPEED = 2
MAX_ENEMY_SPEED = 6
PROJECTILE_SPEED = 7
SHOOT_INTERVAL = 800  # Intervalo de disparo automático em milissegundos
PROJECTILE_LIFE_TIME = 2000  # Tempo de vida dos projéteis em milissegundos
LEVEL_DURATION = 60000  # Duração da fase em milissegundos (60 segundos)
ENEMY_SPAWN_INTERVAL = 5000  # Intervalo para adicionar novos inimigos em milissegundos
ENEMY_INCREASE_INTERVAL = 30000  # Intervalo para dobrar o número de inimigos em milissegundos
ENEMIES_INITIAL_COUNT = 5
IMMUNITY_TIME = 1000  # Tempo de imunidade em milissegundos (1 segundo)

player_last_hit_time = 0
is_fullscreen = False

# Configuração da tela
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jogo com Mapa Gigante")

# Carregar imagens
def load_image(path, size):
    try:
        image = pygame.image.load(path)
        image = pygame.transform.scale(image, size)
        return image
    except pygame.error as e:
        print(f"Erro ao carregar imagem {path}: {e}")
        pygame.quit()
        sys.exit()

background_image = load_image(BACKGROUND_IMAGE_PATH, (MAP_WIDTH, MAP_HEIGHT))
player_image = load_image(PLAYER_IMAGE_PATH, (PLAYER_SIZE, PLAYER_SIZE))
enemy_image = load_image(ENEMY_IMAGE_PATH, (ENEMY_SIZE, ENEMY_SIZE))
projectile_image = load_image(PROJECTILE_IMAGE_PATH, (PROJECTILE_SIZE, PROJECTILE_SIZE))

# Carregar música
try:
    pygame.mixer.music.load(MUSIC_PATH)
    pygame.mixer.music.play(-1)  # Tocar a música em loop
except pygame.error as e:
    print(f"Erro ao carregar música de fundo: {e}")
    pygame.quit()
    sys.exit()

# Função para criar inimigos com velocidade aleatória
def create_enemy():
    border = random.choice(['top', 'bottom', 'left', 'right'])
    x_pos, y_pos = 0, 0

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

# Função para desenhar a barra de vida
def draw_health_bar(life):
    bar_width = 200
    bar_height = 20
    bar_x = 10
    bar_y = 50
    fill_color = (255, 0, 0)  # Cor da vida
    border_color = (255, 255, 255)  # Cor da borda

    # Desenha a borda da barra de vida
    pygame.draw.rect(screen, border_color, pygame.Rect(bar_x, bar_y, bar_width, bar_height), 2)

    # Calcula a largura da barra preenchida com base na vida restante
    fill_width = max(0, (life / 100) * bar_width)
    pygame.draw.rect(screen, fill_color, pygame.Rect(bar_x, bar_y, fill_width, bar_height))

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
    remaining_enemies = [list(enemy) for enemy in enemies]  # Preservar todos os inimigos inicialmente
    
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
def check_collision(player_x, player_y, enemies, current_time):
    global player_last_hit_time
    
    if current_time - player_last_hit_time < IMMUNITY_TIME:
        return False  # O jogador está imune
    
    for ex, ey, _ in enemies:
        if (player_x < ex + ENEMY_SIZE and
            player_x + PLAYER_SIZE > ex and
            player_y < ey + ENEMY_SIZE and
            player_y + PLAYER_SIZE > ey):
            player_last_hit_time = current_time
            return True
    return False

# Função para encontrar o inimigo mais próximo
def find_closest_enemy(player_x, player_y, enemies):
    closest_enemy = None
    min_distance = float('inf')

    for ex, ey, _ in enemies:
        distance = math.sqrt((player_x - ex) ** 2 + (player_y - ey) ** 2)
        if distance < min_distance:
            min_distance = distance
            closest_enemy = (ex, ey)

    return closest_enemy

# Função para criar um projétil em direção ao inimigo mais próximo
def create_projectile_towards_enemy(player_x, player_y, enemy_x, enemy_y):
    direction_x = enemy_x - player_x
    direction_y = enemy_y - player_y
    length = math.sqrt(direction_x**2 + direction_y**2)
    direction_x /= length
    direction_y /= length
    return create_projectile(player_x, player_y, (direction_x, direction_y))

# Função para mostrar a tela de game over
def show_game_over():
    font = pygame.font.Font(None, 74)
    game_over_text = font.render('Game Over', True, (255, 0, 0))
    screen.fill(BACKGROUND_COLOR)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(3000)

# Função para mostrar o menu principal
def show_main_menu():
    global screen, is_fullscreen

    font = pygame.font.Font(None, 74)
    title_text = font.render('Menu Principal', True, (255, 255, 255))
    start_text = font.render('Pressione ENTER para Iniciar', True, (255, 255, 255))
    fullscreen_text = font.render('Pressione F para Tela Cheia', True, (255, 255, 255))
    volume_text = font.render(f'Volume: {int(pygame.mixer.music.get_volume() * 100)}%', True, (255, 255, 255))
    quit_text = font.render('Pressione ESC para Sair', True, (255, 255, 255))

    screen.fill(BACKGROUND_COLOR)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - title_text.get_height() // 2 - 100))
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 - start_text.get_height() // 2))
    screen.blit(fullscreen_text, (WIDTH // 2 - fullscreen_text.get_width() // 2, HEIGHT // 2 - fullscreen_text.get_height() // 2 + 60))
    screen.blit(volume_text, (WIDTH // 2 - volume_text.get_width() // 2, HEIGHT // 2 - volume_text.get_height() // 2 + 120))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 - quit_text.get_height() // 2 + 180))
    pygame.display.flip()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting_for_input = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_f:
                    screen, is_fullscreen = toggle_fullscreen(is_fullscreen)
                    show_main_menu()  # Atualiza o menu após mudar para tela cheia/sem tela cheia
                elif event.key == pygame.K_UP:
                    current_volume = pygame.mixer.music.get_volume()
                    new_volume = min(1.0, current_volume + 0.1)
                    set_volume(new_volume)
                    show_main_menu()  # Atualiza o menu após alterar o volume
                elif event.key == pygame.K_DOWN:
                    current_volume = pygame.mixer.music.get_volume()
                    new_volume = max(0.0, current_volume - 0.1)
                    set_volume(new_volume)
                    show_main_menu()  # Atualiza o menu após alterar o volume

# Função para iniciar o loop do jogo
def game_loop():
    global player_last_hit_time

    player_x, player_y = WIDTH // 2, HEIGHT // 2
    player_dx, player_dy = 0, 0
    player_life = 100
    initial_enemy_count = ENEMIES_INITIAL_COUNT
    enemies = [create_enemy() for _ in range(initial_enemy_count)]
    projectiles = []

    clock = pygame.time.Clock()
    running = True
    last_shoot_time = pygame.time.get_ticks()
    last_enemy_spawn_time = pygame.time.get_ticks()
    last_enemy_increase_time = pygame.time.get_ticks()
    level_start_time = pygame.time.get_ticks()

    enemy_multiplier = 1

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

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

        current_time = pygame.time.get_ticks()
        if current_time - last_shoot_time >= SHOOT_INTERVAL:
            closest_enemy = find_closest_enemy(player_x, player_y, enemies)
            if closest_enemy:
                enemy_x, enemy_y = closest_enemy
                projectiles.append(create_projectile_towards_enemy(player_x, player_y, enemy_x, enemy_y))
                last_shoot_time = current_time

        if current_time - last_enemy_spawn_time >= ENEMY_SPAWN_INTERVAL:
            for _ in range(initial_enemy_count * enemy_multiplier):
                enemies.append(create_enemy())
            last_enemy_spawn_time = current_time

        if current_time - last_enemy_increase_time >= ENEMY_INCREASE_INTERVAL:
            enemy_multiplier *= 2
            last_enemy_increase_time = current_time

        if check_collision(player_x, player_y, enemies, current_time):
            player_life -= 10
            if player_life <= 0:
                show_game_over()
                return

        camera_x = max(0, min(MAP_WIDTH - WIDTH, player_x - WIDTH // 2))
        camera_y = max(0, min(MAP_HEIGHT - HEIGHT, player_y - HEIGHT // 2))

        screen.fill(BACKGROUND_COLOR)
        screen.blit(background_image, (-camera_x, -camera_y))
        draw_timer(level_start_time)
        draw_player(player_x - camera_x, player_y - camera_y)
        for ex, ey, _ in enemies:
            draw_enemy(ex - camera_x, ey - camera_y)
        for px, py, _, _ in projectiles:
            draw_projectile(px - camera_x, py - camera_y)
        draw_health_bar(player_life)

        pygame.display.flip()
        clock.tick(FPS)

# Iniciar o menu principal e o jogo
def main():
    while True:
        show_main_menu()
        game_loop()

if __name__ == "__main__":
    main()