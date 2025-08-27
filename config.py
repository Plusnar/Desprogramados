"""
Configuração centralizada para o jogo Desprogramados
Todas as constantes e configurações do jogo estão aqui centralizadas
"""

import pygame
import os

class GameConfig:
    """Configurações principais do jogo"""
    
    # ===== RESOLUÇÃO E DISPLAY =====
    BASE_WIDTH = 1920
    BASE_HEIGHT = 1080
    FPS = 60
    WINDOW_TITLE = 'Desprogramados - Plataforma'
    
    # ===== FÍSICA DO JOGO =====
    GRAVITY = 1.2
    JUMP_VELOCITY = -16
    MOVE_VELOCITY = 8
    MAX_FALL_VELOCITY = 22
    RAMP_TOLERANCE = 5
    
    # ===== PERSONAGENS =====
    PLAYER_SIZE = 128
    SPRITE_WIDTH = 128
    SPRITE_HEIGHT = 128
    SPRITE_COLS = 7
    SPRITE_ROWS = 54
    
    # ===== ANIMAÇÕES =====
    ANIMATION_SPEEDS = {
        'idle': 12,
        'run': 4,
        'jump': 4
    }
    
    # ===== CONTROLES =====
    CONTROLS = [
        {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w, 'name': 'Jackson'},
        {'left': pygame.K_j, 'right': pygame.K_l, 'jump': pygame.K_i, 'name': 'Jean'},
        {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP, 'name': 'Jean'},
    ]
    
    # ===== INTERFACE =====
    CHAT_WIDTH = 540
    CHAT_HEIGHT = 174
    CHAT_TEXT_X = 270
    CHAT_TEXT_Y = 87
    CHAT_TEXT_WIDTH = 500
    CHAT_TEXT_HEIGHT = 120
    
    # ===== DIALOGO =====
    DIALOG_SPEED = 20
    DIALOG_WAIT_TIME = 1500
    DIALOG_FONT_SIZE = 50
    DIALOG_MIN_FONT_SIZE = 25
    
    # ===== ANIMAÇÕES DE TRANSIÇÃO =====
    ZOOM_DURATION = 3000
    MENU_ANIMATION_SPEED = 0.5
    FADE_DURATION = 2000
    
    # ===== ROBÔS =====
    ROBOT_WIDTH = 230
    ROBOT_HEIGHT = 125
    ROBOT_FRAMES = 2
    ROBOT_SPEED = 8
    ROBOT_COUNT = 20
    
    ROBO_PILOTO_WIDTH = 230
    ROBO_PILOTO_HEIGHT = 125
    ROBO_PILOTO_Y = 289
    ROBO_PILOTO_X1 = 2895
    ROBO_PILOTO_X2 = 5096
    ROBO_PILOTO_SPEED = 6
    
    # ===== CORES =====
    COLORS = {
        'exit_blue': (0, 0, 255, 255),
        'green': (0, 255, 0),
        'red': (255, 0, 0),
        'black': (0, 0, 0, 255),
        'white': (255, 255, 255, 255),
        'cyan': (0, 255, 255),
        'transparent_white': (255, 255, 255, 230),
        'button_alpha': 80
    }
    
    # ===== TOLERÂNCIAS =====
    COLOR_TOLERANCE = 40
    BRUSH_RADIUS = 15
    
    # ===== POSIÇÕES INICIAIS =====
    PLAYER_START_POSITIONS = {
        'paint': [
            (100, 800),
            (300, 800)
        ],
        'plataforma': [
            (200, 350),
            (350, 350)
        ],
        'begin': [
            (100, 800),
            (300, 800)
        ]
    }
    
    # ===== CAMINHOS DE ARQUIVOS =====
    ASSETS_DIR = 'assets'
    MUSIC_DIR = 'music'
    
    SPRITES = {
        'Jackson': os.path.join(ASSETS_DIR, 'jackson.png'),
        'Jean': os.path.join(ASSETS_DIR, 'Jean.png'),
    }
    
    # ===== MÚSICA =====
    MUSIC_FILES = {
        'menu': 'music/menu_theme.ogg',
        'paint': 'music/paint_creative.ogg',
        'plataforma': 'music/platform_action.ogg',
        'begin': 'music/intro_theme.ogg'
    }
    
    # ===== AUDIO =====
    AUDIO_CONFIG = {
        'frequency': 22050,
        'size': -16,
        'channels': 2,
        'buffer': 512,
        'default_volume': 0.7,
        'fade_duration': 1000
    }
    
    # ===== ESTADOS DO JOGO =====
    GAME_STATES = {
        'MENU': 'menu',
        'BEGIN': 'begin',
        'PAINT': 'paint',
        'PLATAFORMA': 'plataforma',
        'QUIT': 'quit'
    }
    
    # ===== SEQUÊNCIA DE FASES =====
    PHASES = ['begin', 'plataforma', 'paint']
    
    # ===== LOGGING =====
    LOG_CONFIG = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': 'game.log',
        'max_size': 1024 * 1024,  # 1MB
        'backup_count': 3
    }
    
    # ===== ANALYTICS =====
    ANALYTICS_CONFIG = {
        'enabled': True,
        'save_interval': 30,  # segundos
        'metrics_file': 'analytics.json'
    } 