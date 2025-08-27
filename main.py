import pygame
import sys
import time
import math
import os
import contextlib

# Suprimir avisos libpng no terminal
class SuppressLibPngWarnings(contextlib.ContextDecorator):
    def __enter__(self):
        import io
        self._stderr = sys.stderr
        sys.stderr = io.StringIO()
    def __exit__(self, exc_type, exc_value, traceback):
        sys.stderr = self._stderr

with SuppressLibPngWarnings():
    pass  # O restante do código será executado normalmente

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Importar sistemas de melhoria
from config import GameConfig
from logger import log_info, log_debug, log_warning, log_error, log_game_event
from exceptions import safe_resource_load, handle_critical_error, create_error_surface
from analytics import track_event, track_level_completed, get_analytics_report
from optimizations import (
    render_manager, frame_rate_controller, memory_manager, 
    performance_monitor, update_performance_metrics, get_performance_report
)

from minigames.plataforma import run_plataforma_minigame
from minigames.paint import run_paint_minigame

# Sistema de música simples integrado
class SimpleMusicManager:
    def __init__(self):
        try:
            pygame.mixer.init(
                frequency=GameConfig.AUDIO_CONFIG['frequency'],
                size=GameConfig.AUDIO_CONFIG['size'],
                channels=GameConfig.AUDIO_CONFIG['channels'],
                buffer=GameConfig.AUDIO_CONFIG['buffer']
            )
            self.current_state = None
            self.volume = GameConfig.AUDIO_CONFIG['default_volume']
            self.music_enabled = True
            log_info("Sistema de música inicializado")
        except pygame.error as e:
            log_error(f"Erro ao inicializar música: {e}")
            self.music_enabled = False
    
    def play_for_state(self, game_state):
        if not self.music_enabled:
            return
            
        if game_state == self.current_state:
            return
            
        # Para música atual
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(1000)
        
        # Mapear estados para arquivos de música (quando disponíveis)
        music_files = GameConfig.MUSIC_FILES
        
        if game_state in music_files:
            music_file = music_files[game_state]
            if os.path.exists(music_file):
                try:
                    pygame.mixer.music.load(music_file)
                    pygame.mixer.music.set_volume(self.volume)
                    pygame.mixer.music.play(-1)  # Loop infinito
                    self.current_state = game_state
                    log_info(f"Tocando música para: {game_state}")
                    track_event('music_changed', {'state': game_state, 'file': music_file})
                except pygame.error as e:
                    log_error(f"Erro ao tocar música {music_file}: {e}")
            else:
                log_warning(f"Arquivo de música não encontrado: {music_file}")
    
    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))
        if self.music_enabled:
            pygame.mixer.music.set_volume(self.volume)
    
    def get_volume(self):
        return self.volume
    
    def toggle_music(self):
        if not self.music_enabled:
            return False
            
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            return False
        else:
            pygame.mixer.music.unpause()
            return True

# Instância global do gerenciador de música
music_manager = SimpleMusicManager()

pygame.init()

# Resolução base do jogo
BASE_WIDTH, BASE_HEIGHT = GameConfig.BASE_WIDTH, GameConfig.BASE_HEIGHT
BASE_SURFACE = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))

# Iniciar em modo janela redimensionável, tamanho inicial 1080x720
SCREEN = pygame.display.set_mode((1080, 720), pygame.RESIZABLE)
pygame.display.set_caption(GameConfig.WINDOW_TITLE)
FONT = pygame.font.SysFont('Arial', 32)

STATE_MENU = GameConfig.GAME_STATES['MENU']
STATE_BEGIN = GameConfig.GAME_STATES['BEGIN']
STATE_PAINT = GameConfig.GAME_STATES['PAINT']
STATE_PLATAFORMA = GameConfig.GAME_STATES['PLATAFORMA']
STATE_QUIT = GameConfig.GAME_STATES['QUIT']

# Atualizar lista de fases para incluir 'begin' separadamente
FASES = GameConfig.PHASES

game_state = STATE_MENU
clock = pygame.time.Clock()

fase_atual = 0

# Variável global para animar o fundo do menu
# Substituir menu_anim_offset por menu_anim_offset_x e menu_anim_offset_y para permitir incremento fracionário
menu_anim_offset_x = 0.0
menu_anim_offset_y = 0.0

# Variáveis globais para o menu
jogar_btn_rect = None
menu_transition = False
menu_transition_start = 0
last_time = 0

def load_image_or_exit(path, desc):
    try:
        return safe_resource_load(pygame.image.load, "imagem", path)
    except Exception as e:
        log_error(f'Erro ao carregar {desc} ({path}): {e}')
        handle_critical_error(e, f"Carregamento de {desc}")
        pygame.quit()
        sys.exit(f'Erro ao carregar {desc} ({path}): {e}')

# Carregar imagem de fundo única para o menu
MENU_BG = load_image_or_exit('assets/screen.png', 'fundo do menu')
MENU_BG_W, MENU_BG_H = MENU_BG.get_width(), MENU_BG.get_height()

# Carregar a logo do título
TITULO_LOGO = load_image_or_exit('assets/titulo.png', 'logo do título')
TITULO_LOGO_W, TITULO_LOGO_H = TITULO_LOGO.get_width(), TITULO_LOGO.get_height()

# Carregar sprites individuais dos personagens
PERSONAGEM_SPRITES = [
    load_image_or_exit('assets/jackson.png', 'sprite Jackson'),
    load_image_or_exit('assets/Jean.png', 'sprite Jean'),
    load_image_or_exit('assets/will.png', 'sprite Will'),
]
SPRITE_COLS = GameConfig.SPRITE_COLS
SPRITE_WIDTH = GameConfig.SPRITE_WIDTH
SPRITE_HEIGHT = GameConfig.SPRITE_HEIGHT
SPRITE_ROW = 2  # fileira 3 (índice 2)

# Carregar imagem do botão jogar
JOGAR_BTN = load_image_or_exit('assets/jogar.png', 'botão jogar')
JOGAR_BTN_W, JOGAR_BTN_H = 419, 217 
# Variável para controlar a animação do botão jogar
jogar_btn_animation_scale = 1.0

def draw_menu():
    global menu_anim_offset_x, menu_anim_offset_y, last_time, jogar_btn_rect, menu_transition, menu_transition_start, jogar_btn_animation_scale

    if menu_transition:
        # Fundo preto com fade-in
        elapsed = pygame.time.get_ticks() - menu_transition_start
        fade_duration = 2000  # 2 segundos
        alpha = min(255, int(255 * (elapsed / fade_duration)))
        # Desenhar fundo animado normalmente
        speed_x = 0.5
        speed_y = 0.5
        menu_anim_offset_x = (menu_anim_offset_x + speed_x) % MENU_BG_W
        menu_anim_offset_y = (menu_anim_offset_y + speed_y) % MENU_BG_H
        offset_x = int(menu_anim_offset_x)
        offset_y = int(menu_anim_offset_y)

        def tile_bg(bg, alpha_bg=255):
            temp = pygame.Surface((MENU_BG_W, MENU_BG_H), pygame.SRCALPHA)
            temp.blit(bg, (0, 0))
            if alpha_bg < 255:
                temp.set_alpha(alpha_bg)
            for y_ in range(-MENU_BG_H, BASE_HEIGHT + MENU_BG_H, MENU_BG_H):
                for x_ in range(-MENU_BG_W, BASE_WIDTH + MENU_BG_W, MENU_BG_W):
                    BASE_SURFACE.blit(temp, (x_ + offset_x, y_ + offset_y))

    # Detectar hover no botão jogar
    mouse_pos = pygame.mouse.get_pos()
    if jogar_btn_rect:
        is_hovering = jogar_btn_rect.collidepoint(mouse_pos)
    else:
        is_hovering = False

    # Ajustar escala do botão com base no hover
    if is_hovering:
        scale_factor = 1.2  # Aumentar o tamanho em 20% no hover
    else:
        scale_factor = 1.0  # Tamanho normal

    # Redimensionar o botão jogar
    jogar_btn_scaled = pygame.transform.scale(JOGAR_BTN, (int(JOGAR_BTN_W * scale_factor), int(JOGAR_BTN_H * scale_factor)))

    # Centralizar o botão na tela
    jogar_btn_x = (BASE_WIDTH - jogar_btn_scaled.get_width()) // 2
    jogar_btn_y = (BASE_HEIGHT - jogar_btn_scaled.get_height()) // 2
    jogar_btn_rect = pygame.Rect(jogar_btn_x, jogar_btn_y, jogar_btn_scaled.get_width(), jogar_btn_scaled.get_height())

    # Desenhar o botão jogar
    BASE_SURFACE.blit(jogar_btn_scaled, (jogar_btn_x, jogar_btn_y))

# Variável para controlar a animação do botão jogar
jogar_btn_animation_scale = 1.0

def draw_menu():
    global menu_anim_offset_x, menu_anim_offset_y, last_time, jogar_btn_rect, menu_transition, menu_transition_start, jogar_btn_animation_scale

    if menu_transition:
        # Fundo preto com fade-in
        elapsed = pygame.time.get_ticks() - menu_transition_start
        fade_duration = 2000  # 2 segundos
        alpha = min(255, int(255 * (elapsed / fade_duration)))
        # Desenhar fundo animado normalmente
        speed_x = 0.5
        speed_y = 0.5
        menu_anim_offset_x = (menu_anim_offset_x + speed_x) % MENU_BG_W
        menu_anim_offset_y = (menu_anim_offset_y + speed_y) % MENU_BG_H
        offset_x = int(menu_anim_offset_x)
        offset_y = int(menu_anim_offset_y)

        def tile_bg(bg, alpha_bg=255):
            temp = pygame.Surface((MENU_BG_W, MENU_BG_H), pygame.SRCALPHA)
            temp.blit(bg, (0, 0))
            if alpha_bg < 255:
                temp.set_alpha(alpha_bg)
            for y_ in range(-MENU_BG_H, BASE_HEIGHT + MENU_BG_H, MENU_BG_H):
                for x_ in range(-MENU_BG_W, BASE_WIDTH + MENU_BG_W, MENU_BG_W):
                    BASE_SURFACE.blit(temp, (x_ + offset_x, y_ + offset_y))

    # Animação do botão jogar
    time_now = pygame.time.get_ticks()
    scale_factor = 1 + 0.1 * math.sin(time_now * 0.005)  # Variação de escala entre 1.0 e 1.1
    jogar_btn_animation_scale = scale_factor

    # Redimensionar o botão jogar
    jogar_btn_scaled = pygame.transform.scale(JOGAR_BTN, (int(JOGAR_BTN_W * scale_factor), int(JOGAR_BTN_H * scale_factor)))

    # Centralizar o botão na tela
    jogar_btn_x = (BASE_WIDTH - jogar_btn_scaled.get_width()) // 2
    jogar_btn_y = (BASE_HEIGHT - jogar_btn_scaled.get_height()) // 2
    jogar_btn_rect = pygame.Rect(jogar_btn_x, jogar_btn_y, jogar_btn_scaled.get_width(), jogar_btn_scaled.get_height())
    
    # Definição da função tile_bg
    def tile_bg(bg, alpha_bg=255):
        # Cria uma superfície temporária para o fundo
        temp = pygame.Surface((MENU_BG_W, MENU_BG_H), pygame.SRCALPHA)
        temp.blit(bg, (0, 0))
        if alpha_bg < 255:
            temp.set_alpha(alpha_bg)
        # Preenche o fundo com o padrão
        for y_ in range(-MENU_BG_H, BASE_HEIGHT + MENU_BG_H, MENU_BG_H):
            for x_ in range(-MENU_BG_W, BASE_WIDTH + MENU_BG_W, MENU_BG_W):
                BASE_SURFACE.blit(temp, (x_ + offset_x, y_ + offset_y))

def draw_menu():
    global menu_anim_offset_x, menu_anim_offset_y, jogar_btn_rect

    # Fundo animado
    speed_x = 0.5
    speed_y = 0.5
    menu_anim_offset_x = (menu_anim_offset_x + speed_x) % MENU_BG_W
    menu_anim_offset_y = (menu_anim_offset_y + speed_y) % MENU_BG_H
    offset_x = int(menu_anim_offset_x)
    offset_y = int(menu_anim_offset_y)

    def tile_bg(bg, alpha_bg=255):
        temp = pygame.Surface((MENU_BG_W, MENU_BG_H), pygame.SRCALPHA)
        temp.blit(bg, (0, 0))
        if alpha_bg < 255:
            temp.set_alpha(alpha_bg)
        for y_ in range(-MENU_BG_H, BASE_HEIGHT + MENU_BG_H, MENU_BG_H):
            for x_ in range(-MENU_BG_W, BASE_WIDTH + MENU_BG_W, MENU_BG_W):
                BASE_SURFACE.blit(temp, (x_ + offset_x, y_ + offset_y))

    # Detectar hover no botão jogar
    mouse_pos = pygame.mouse.get_pos()
    if jogar_btn_rect:
        is_hovering = jogar_btn_rect.collidepoint(mouse_pos)
    else:
        is_hovering = False

    # Ajustar escala do botão com base no hover
    if is_hovering:
        scale_factor = 1.2  # Aumentar o tamanho em 20% no hover
    else:
        scale_factor = 1.0  # Tamanho normal

    # Redimensionar o botão jogar
    jogar_btn_scaled = pygame.transform.scale(
        JOGAR_BTN, 
        (int(JOGAR_BTN_W * scale_factor), int(JOGAR_BTN_H * scale_factor))
    )

    # Atualizar o retângulo do botão para refletir o novo tamanho
    jogar_btn_x = (BASE_WIDTH - jogar_btn_scaled.get_width()) // 2
    jogar_btn_y = (BASE_HEIGHT - jogar_btn_scaled.get_height()) // 2
    jogar_btn_rect = pygame.Rect(
        jogar_btn_x, jogar_btn_y, 
        jogar_btn_scaled.get_width(), jogar_btn_scaled.get_height()
    )

    # Desenhar o botão jogar
    BASE_SURFACE.blit(jogar_btn_scaled, (jogar_btn_x, jogar_btn_y))

    if menu_transition:
        # Fundo preto com fade-in
        elapsed = pygame.time.get_ticks() - menu_transition_start
        fade_duration = 2000  # 2 segundos
        alpha = min(255, int(255 * (elapsed / fade_duration)))
        # Desenhar fundo animado normalmente
        speed_x = 0.5
        speed_y = 0.5
        menu_anim_offset_x = (menu_anim_offset_x + speed_x) % MENU_BG_W
        menu_anim_offset_y = (menu_anim_offset_y + speed_y) % MENU_BG_H
        offset_x = int(menu_anim_offset_x)
        offset_y = int(menu_anim_offset_y)
        def tile_bg(bg, alpha_bg=255):
            temp = pygame.Surface((MENU_BG_W, MENU_BG_H), pygame.SRCALPHA)
            temp.blit(bg, (0, 0))
            if alpha_bg < 255:
                temp.set_alpha(alpha_bg)
            for y_ in range(-MENU_BG_H, BASE_HEIGHT + MENU_BG_H, MENU_BG_H):
                for x_ in range(-MENU_BG_W, BASE_WIDTH + MENU_BG_W, MENU_BG_W):
                    BASE_SURFACE.blit(temp, (x_ + offset_x, y_ + offset_y))
        tile_bg(MENU_BG, 255)
        # Sobrepor fade preto
        fade_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, alpha))
        BASE_SURFACE.blit(fade_surface, (0, 0))
        jogar_btn_rect = None  # botão não existe
        return
    
    # Velocidade do movimento (mais devagar)
    speed_x = GameConfig.MENU_ANIMATION_SPEED
    speed_y = GameConfig.MENU_ANIMATION_SPEED
    menu_anim_offset_x = (menu_anim_offset_x + speed_x) % MENU_BG_W
    menu_anim_offset_y = (menu_anim_offset_y + speed_y) % MENU_BG_H
    offset_x = int(menu_anim_offset_x)
    offset_y = int(menu_anim_offset_y)

    # Desenhar fundo tile da imagem única
    def tile_bg(bg):
        for y in range(-MENU_BG_H, BASE_HEIGHT + MENU_BG_H, MENU_BG_H):
            for x in range(-MENU_BG_W, BASE_WIDTH + MENU_BG_W, MENU_BG_W):
                BASE_SURFACE.blit(bg, (x + offset_x, y + offset_y))

    tile_bg(MENU_BG)

    # Animação suave de sobe e desce para a logo do título
    t = pygame.time.get_ticks() / 1000.0  # tempo em segundos
    amplitude = 20  # pixels
    period = 2.5    # segundos para um ciclo completo
    logo_y = 20 + int(amplitude * math.sin(2 * math.pi * t / period))
    logo_x = BASE_WIDTH // 2 - TITULO_LOGO_W // 2
    
    # Exibir o título
    BASE_SURFACE.blit(TITULO_LOGO, (logo_x, logo_y))

    # --- Botão jogar ---
    btn_x = BASE_WIDTH // 2 - JOGAR_BTN_W // 2
    btn_y = BASE_HEIGHT - JOGAR_BTN_H - 100  # Posição fixa para o botão
    BASE_SURFACE.blit(JOGAR_BTN, (btn_x, btn_y))
    jogar_btn_rect = pygame.Rect(btn_x, btn_y, JOGAR_BTN_W, JOGAR_BTN_H)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            # Controles de música
            elif event.key == pygame.K_m:  # M para pausar/despausar música
                music_manager.toggle_music()
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:  # + para aumentar volume
                current_vol = music_manager.get_volume()
                music_manager.set_volume(current_vol + 0.1)
                log_debug(f"Volume: {int(music_manager.get_volume() * 100)}%")
            elif event.key == pygame.K_MINUS:  # - para diminuir volume
                current_vol = music_manager.get_volume()
                music_manager.set_volume(current_vol - 0.1)
                log_debug(f"Volume: {int(music_manager.get_volume() * 100)}%")
        if event.type == pygame.VIDEORESIZE:
            SCREEN = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        if game_state == STATE_MENU:
            if not menu_transition:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    menu_transition = True
                    menu_transition_start = pygame.time.get_ticks()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    window_width, window_height = SCREEN.get_size()
                    scale = min(window_width / BASE_WIDTH, window_height / BASE_HEIGHT)
                    scaled_width = int(BASE_WIDTH * scale)
                    scaled_height = int(BASE_HEIGHT * scale)
                    x_offset = (window_width - scaled_width) // 2
                    y_offset = (window_height - scaled_height) // 2
                    mx_base = int((mx - x_offset) / scale)
                    my_base = int((my - y_offset) / scale)
                    if jogar_btn_rect and jogar_btn_rect.collidepoint(mx_base, my_base):
                        menu_transition = True
                        menu_transition_start = pygame.time.get_ticks()
            else:
                # Após 2 segundos, inicia o jogo
                if pygame.time.get_ticks() - menu_transition_start > GameConfig.FADE_DURATION:
                    game_state = STATE_BEGIN
                    menu_transition = False
                    log_game_event('game_started', {'from': 'menu', 'to': 'begin'})
    if game_state == STATE_MENU:
        music_manager.play_for_state('menu')
        draw_menu()
    elif game_state == STATE_PAINT:
        music_manager.play_for_state('paint')
        level_start_time = time.time()
        result = run_paint_minigame(SCREEN, clock)
        if result == 'success':
            level_time = time.time() - level_start_time
            track_level_completed('paint', level_time)
            game_state = STATE_MENU
            log_game_event('level_completed', {'level': 'paint', 'time': level_time})
    elif game_state == STATE_BEGIN:
        music_manager.play_for_state('begin')
        from minigames.paint import run_begin_minigame
        level_start_time = time.time()
        result = run_begin_minigame(
            SCREEN, clock,
            'assets/begin.png',
            'assets/begin_colormap.png',
            None,
            None
        )
        if result == 'success':
            level_time = time.time() - level_start_time
            track_level_completed('begin', level_time)
            game_state = STATE_PLATAFORMA
            log_game_event('level_completed', {'level': 'begin', 'time': level_time})
    elif game_state == STATE_PLATAFORMA:
        music_manager.play_for_state('plataforma')
        level_start_time = time.time()
        result = run_plataforma_minigame(SCREEN, clock)
        if result == 'success':
            level_time = time.time() - level_start_time
            track_level_completed('plataforma', level_time)
            game_state = STATE_PAINT
            log_game_event('level_completed', {'level': 'plataforma', 'time': level_time})
    # Ajuste de proporção e centralização
    window_width, window_height = SCREEN.get_size()
    scale = min(window_width / BASE_WIDTH, window_height / BASE_HEIGHT)
    scaled_width = int(BASE_WIDTH * scale)
    scaled_height = int(BASE_HEIGHT * scale)
    scaled_surface = pygame.transform.smoothscale(BASE_SURFACE, (scaled_width, scaled_height))
    x_offset = (window_width - scaled_width) // 2
    y_offset = (window_height - scaled_height) // 2
    SCREEN.fill((0, 0, 0))
    SCREEN.blit(scaled_surface, (x_offset, y_offset))
    pygame.display.flip()
    
    # Atualizar métricas de performance
    fps, frame_time = frame_rate_controller.update()
    update_performance_metrics(fps, frame_time, 0)  # update_time será calculado se necessário
    
    clock.tick(GameConfig.FPS)