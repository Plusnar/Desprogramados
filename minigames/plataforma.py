import pygame
import os
import random
import math

SPRITES = {
    'Jackson': os.path.join('assets', 'jackson.png'),
    'Jean': os.path.join('assets', 'Jean.png'),
}
COLORMAP_PATH = os.path.join('assets', 'color_map1.png')
MAP_PATH = os.path.join('assets', 'map1.png')
ROBOT_PATH = os.path.join('assets', 'robot_puzzle_sprite1.png')
ROBO_PILOTO_PATH = os.path.join('assets', 'robot_puzzle_ligado.png')
ROBO_PILOTO_W, ROBO_PILOTO_H = 230, 125  # tamanho corrigido
ROBO_PILOTO_Y = 289
ROBO_PILOTO_X1 = 2895
ROBO_PILOTO_X2 = 5096
ROBO_PILOTO_SPEED = 6

PLAYER_SIZE = 128
SPRITE_COLS = 13
SPRITE_ROWS = 54
SPRITE_W, SPRITE_H = 128, 128
GRAVITY = 1.2
JUMP_V = -28
MOVE_V = 14
RAMP_TOLERANCE = 5

ROBOT_W, ROBOT_H = 230, 125
ROBOT_FRAMES = 2
ROBOT_SPEED = 8
ROBOT_COUNT = 20

# Configurações da plataforma móvel
MOVEL_PATH = os.path.join('assets', 'movel.png')
MOVEL_COLORMAP_PATH = os.path.join('assets', 'movel_colormap.png')
MOVEL_WIDTH = 445  # Metade da largura total (890/2)
MOVEL_HEIGHT = 600
MOVEL_FRAMES = 2  # 2 colunas
MOVEL_ANIMATION_SPEED = 0.005  # Velocidade da animação
MOVEL_SPAWN_X = 2922
MOVEL_SPAWN_Y = 480

ANIM = {
    'idle':    {'row': 24, 'frames': 2},
    'run_l':   {'row': 39, 'frames': 8},
    'run_r':   {'row': 41, 'frames': 8},
    'jump_l':  {'row': 27, 'frames': 5},
    'jump_r':  {'row': 29, 'frames': 5},
}

CONTROLS = [
    {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w, 'name': 'Jackson'},
    {'left': pygame.K_j, 'right': pygame.K_l, 'jump': pygame.K_i, 'name': 'Jean'},
    {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP, 'name': 'Jean'},
]

class Player:
    def __init__(self, name, x, y, spritesheet):
        self.name = name
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.state = 'idle'  # idle, run_l, run_r, jump_l, jump_r
        self.anim_frame = 0
        self.anim_timer = 0
        self.dir = 1  # 1: direita, -1: esquerda
        self.spritesheet = spritesheet
        self.masks = self._make_masks()

    def _make_masks(self):
        # Gera máscara para cada quadro do spritesheet
        masks = {}
        for key, anim in ANIM.items():
            row = anim['row']
            for col in range(anim['frames']):
                surf = self.spritesheet.subsurface((col*SPRITE_W, row*SPRITE_H, SPRITE_W, SPRITE_H)).convert_alpha()
                masks[(key, col)] = pygame.mask.from_surface(surf)
        return masks

    def get_frame(self):
        anim = ANIM[self.state]
        frame = self.anim_frame % anim['frames']
        return anim['row'], frame

    def get_mask(self):
        row, frame = self.get_frame()
        return self.masks[(self.state, frame)]

    def get_surface(self):
        row, frame = self.get_frame()
        return self.spritesheet.subsurface((frame*SPRITE_W, row*SPRITE_H, SPRITE_W, SPRITE_H)).convert_alpha()

    def rect(self):
        return pygame.Rect(int(self.x - SPRITE_W//2), int(self.y), SPRITE_W, SPRITE_H)

    def update_anim(self, moving):
        self.anim_timer += 1
        if self.state.startswith('run') or self.state.startswith('jump'):
            speed = 4
        else:
            speed = 12
        if self.anim_timer >= speed:
            self.anim_frame = (self.anim_frame + 1) % ANIM[self.state]['frames']
            self.anim_timer = 0
        if not moving:
            self.anim_frame = 0
            self.anim_timer = 0

    def draw(self, surf, cam_x, cam_y, font):
        img = self.get_surface()
        px = int(self.x - cam_x - SPRITE_W//2)
        py = int(self.y - cam_y)
        surf.blit(img, (px, py))
        label = font.render(self.name, True, (0,255,255))
        surf.blit(label, (px, py-32))

    def try_move(self, dx, dy, colormap_mask):
        # Tenta mover pixel a pixel, respeitando rampas e paredes
        new_x = self.x + dx
        new_y = self.y + dy
        mask = self.get_mask()
        for ramp in range(RAMP_TOLERANCE+1):
            test_y = new_y - ramp if dx != 0 else new_y
            offset = (int(new_x - SPRITE_W//2), int(test_y))
            if not colormap_mask.overlap(mask, offset):
                # Só checa parede vertical se não estiver subindo rampa
                if dx != 0 and ramp == 0 and self.detect_vertical_wall(colormap_mask, new_x, test_y):
                    continue
                self.x = new_x
                self.y = test_y
                return True
        return False

    def detect_vertical_wall(self, colormap_mask, x, y):
        mask = self.get_mask()
        for dx in [0, SPRITE_W-1]:
            wall_height = 0
            for dy in range(SPRITE_H):
                if mask.get_at((dx, dy)) and colormap_mask.get_at((int(x - SPRITE_W//2) + dx, int(y) + dy)):
                    wall_height += 1
                    if wall_height > RAMP_TOLERANCE:
                        return True
        return False

    def check_on_ground(self, colormap_mask):
        mask = self.get_mask()
        offset = (int(self.x - SPRITE_W//2), int(self.y + 1))
        return colormap_mask.overlap(mask, offset) is not None

    def update_state(self, moving, jumping):
        if jumping:
            if self.dir == 1:
                self.state = 'jump_r'
            else:
                self.state = 'jump_l'
        elif moving:
            if self.dir == 1:
                self.state = 'run_r'
            else:
                self.state = 'run_l'
        else:
            self.state = 'idle'

    def unstick_from_map(self, colormap_mask):
        # Tenta mover o player para cima, esquerda, direita, baixo até sair da colisão
        max_attempts = 20
        mask = self.get_mask()
        for dy in range(1, max_attempts):
            offset = (int(self.x - SPRITE_W//2), int(self.y - dy))
            if not colormap_mask.overlap(mask, offset):
                self.y -= dy
                return
        for dx in range(1, max_attempts):
            offset = (int(self.x - SPRITE_W//2 - dx), int(self.y))
            if not colormap_mask.overlap(mask, offset):
                self.x -= dx
                return
            offset = (int(self.x - SPRITE_W//2 + dx), int(self.y))
            if not colormap_mask.overlap(mask, offset):
                self.x += dx
                return
        for dy in range(1, max_attempts):
            offset = (int(self.x - SPRITE_W//2), int(self.y + dy))
            if not colormap_mask.overlap(mask, offset):
                self.y += dy
                return

class MovelPlatform:
    """Plataforma móvel que alterna entre duas animações"""
    
    def __init__(self, spritesheet, colormap):
        self.spritesheet = spritesheet
        self.colormap = colormap
        self.x = MOVEL_SPAWN_X
        self.y = MOVEL_SPAWN_Y
        self.anim_frame = 0
        self.anim_timer = 0
        self.animation_speed = MOVEL_ANIMATION_SPEED
        
        # Criar máscara para colisão usando o colormap invisível
        self.mask = pygame.mask.from_surface(self.get_invisible_colormap_frame())
    
    def get_current_frame(self):
        """Retorna o frame atual da animação"""
        return self.spritesheet.subsurface((
            self.anim_frame * MOVEL_WIDTH, 
            0, 
            MOVEL_WIDTH, 
            MOVEL_HEIGHT
        )).convert_alpha()
    
    def get_current_colormap_frame(self):
        """Retorna o frame atual do colormap para colisão"""
        # O colormap tem apenas 1 quadro, então sempre usa o frame 0
        # Mas deve estar na mesma posição que o frame visual atual
        return self.colormap.subsurface((
            self.anim_frame * MOVEL_WIDTH, 
            0, 
            MOVEL_WIDTH, 
            MOVEL_HEIGHT
        )).convert_alpha()
    
    def get_invisible_colormap_frame(self):
        """Retorna o frame do colormap invisível para colisão"""
        # O colormap invisível sempre usa o frame 0 (primeira coluna)
        return self.colormap.subsurface((
            0, 
            0, 
            MOVEL_WIDTH, 
            MOVEL_HEIGHT
        )).convert_alpha()
    
    def update(self):
        """Atualiza a animação da plataforma"""
        self.anim_timer += 1
        if self.anim_timer >= 60:  # Mudar frame a cada 60 frames (1 segundo a 60 FPS)
            self.anim_frame = (self.anim_frame + 1) % MOVEL_FRAMES
            self.anim_timer = 0
            # Atualizar máscara para colisão usando o colormap invisível
            self.mask = pygame.mask.from_surface(self.get_invisible_colormap_frame())
    
    def draw(self, surface, cam_x, cam_y):
        """Desenha a plataforma na tela"""
        # Desenhar o frame visual da animação
        frame = self.get_current_frame()
        px = int(self.x - cam_x)
        py = int(self.y - cam_y)
        surface.blit(frame, (px, py))
        
        # Desenhar o colormap visível (para debug/visualização)
        colormap_frame = self.get_invisible_colormap_frame()
        surface.blit(colormap_frame, (px, py))
    
    def get_rect(self):
        """Retorna o retângulo da plataforma para colisão"""
        return pygame.Rect(self.x, self.y, MOVEL_WIDTH, MOVEL_HEIGHT)
    
    def check_collision(self, player):
        """Verifica colisão com o jogador"""
        player_rect = player.rect()
        platform_rect = self.get_rect()
        
        # Primeiro verifica se os retângulos se intersectam
        if not player_rect.colliderect(platform_rect):
            return False
            
        # Verificar colisão pixel-perfect usando máscaras
        player_mask = player.get_mask()
        
        # Calcular offset correto para a colisão
        player_offset = (
            int(player_rect.x - self.x),
            int(player_rect.y - self.y)
        )
        
        # Verificar se há sobreposição de pixels
        overlap = self.mask.overlap(player_mask, player_offset)
        return overlap is not None
    
    def check_player_on_top(self, player):
        """Verifica se o jogador está em cima da plataforma"""
        player_rect = player.rect()
        platform_rect = self.get_rect()
        
        # Verificar se há colisão básica
        if not player_rect.colliderect(platform_rect):
            return False
            
        # Verificar se o jogador está caindo (velocidade vertical positiva)
        if player.vy < 0:
            return False
            
        # Verificar se os pés do jogador estão próximos ao topo da plataforma
        feet_y = player_rect.bottom
        platform_top = platform_rect.top
        
        # Tolerância para estar "em cima" (16 pixels)
        if abs(feet_y - platform_top) <= 16:
            # Verificar se há sobreposição horizontal significativa
            overlap_left = max(player_rect.left, platform_rect.left)
            overlap_right = min(player_rect.right, platform_rect.right)
            overlap_width = overlap_right - overlap_left
            
            # Pelo menos 10 pixels de sobreposição horizontal
            if overlap_width >= 10:
                # Verificar colisão pixel-perfect usando o colormap
                player_mask = player.get_mask()
                colormap_frame = self.get_invisible_colormap_frame()
                colormap_mask = pygame.mask.from_surface(colormap_frame)
                
                # Calcular offset para a colisão
                player_offset = (
                    int(player_rect.x - self.x),
                    int(player_rect.y - self.y)
                )
                
                # Verificar se há sobreposição de pixels no colormap
                overlap = colormap_mask.overlap(player_mask, player_offset)
                return overlap is not None
                
        return False

class DroneRobot:
    def __init__(self, spritesheet, map_width, map_height):
        self.spritesheet = spritesheet
        self.x = random.randint(map_width, map_width + 1000)
        self.y_base = random.randint(0, map_height - ROBOT_H)
        self.y = self.y_base
        self.frame = random.randint(0, 1)
        self.anim_timer = random.randint(0, 10)
        self.map_width = map_width
        self.map_height = map_height
        self.speed = ROBOT_SPEED + random.randint(-2, 2)
        self.tilt_phase = random.uniform(0, 2 * 3.1415)
    def update(self):
        self.x -= self.speed
        self.anim_timer += 1
        if self.anim_timer >= 10:
            self.frame = (self.frame + 1) % ROBOT_FRAMES
            self.anim_timer = 0
        # Tilt vertical suave (senoidal)
        self.tilt_phase += 0.08 + random.uniform(-0.01, 0.01)
        self.y = self.y_base + int(10 * math.sin(self.tilt_phase))
    def draw(self, surf, cam_x, cam_y):
        img = self.spritesheet.subsurface((self.frame*ROBOT_W, 0, ROBOT_W, ROBOT_H)).convert_alpha()
        px = int(self.x - cam_x)
        py = int(self.y - cam_y)
        surf.blit(img, (px, py))
    def is_off_screen(self, cam_x):
        return self.x < cam_x - ROBOT_W

class RoboPiloto:
    def __init__(self, img):
        self.img = img
        self.x = ROBO_PILOTO_X1
        self.y = ROBO_PILOTO_Y
        self.dir = 1  # 1: direita, -1: esquerda
    def update(self):
        self.x += self.dir * ROBO_PILOTO_SPEED
        if self.x >= ROBO_PILOTO_X2:
            self.x = ROBO_PILOTO_X2
            self.dir = -1
        elif self.x <= ROBO_PILOTO_X1:
            self.x = ROBO_PILOTO_X1
            self.dir = 1
    def draw(self, surf, cam_x, cam_y):
        frame_img = self.img.subsurface((0, 0, ROBO_PILOTO_W, ROBO_PILOTO_H)).copy()
        # Espelhar apenas na volta (dir == -1)
        if self.dir == -1:
            frame_img = pygame.transform.flip(frame_img, True, False)
        px = int(self.x - cam_x)
        py = int(self.y - cam_y)
        surf.blit(frame_img, (px, py))


def run_plataforma_minigame(screen, clock):
    pygame.display.set_caption('Desprogramados - Plataforma')
    base_width, base_height = 1920, 1080
    font = pygame.font.SysFont('Arial', 28)
    spritesheets = {name: pygame.image.load(path).convert_alpha() for name, path in SPRITES.items()}
    colormap_img = pygame.image.load(COLORMAP_PATH).convert_alpha()
    colormap_mask = pygame.mask.from_surface(colormap_img)
    map_img = pygame.image.load(MAP_PATH).convert_alpha()
    robot_sheet = pygame.image.load(ROBOT_PATH).convert_alpha()
    players = [
        Player('Jackson', 200, 350, spritesheets['Jackson']),
        Player('Jean', 350, 350, spritesheets['Jean']),
    ]
    robo_piloto_img = pygame.image.load(ROBO_PILOTO_PATH).convert_alpha()
    robo_piloto = RoboPiloto(robo_piloto_img)
    
    # Carregar plataforma móvel
    movel_img = pygame.image.load(MOVEL_PATH).convert_alpha()
    movel_colormap_img = pygame.image.load(MOVEL_COLORMAP_PATH).convert_alpha()
    movel_platform = MovelPlatform(movel_img, movel_colormap_img)
    
    map_w, map_h = colormap_img.get_width(), colormap_img.get_height()
    robots = [DroneRobot(robot_sheet, map_w, map_h) for _ in range(ROBOT_COUNT)]
    running = True
    # Remover variáveis e lógica de transição de céu
    # sky_transition_started = False
    # sky_transition_start_time = None
    # sky_transition_duration = 5000  # 5 segundos em ms
    # sky_switch_delay = 5000  # 5 segundos até começar a transição
    # dia_img = pygame.image.load(os.path.join('assets', 'dia.png')).convert()
    noite_img = pygame.image.load(os.path.join('assets', 'noite.png')).convert()
    # start_time = pygame.time.get_ticks()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        keys = pygame.key.get_pressed()
        # --- UPDATE PLAYERS ---
        for idx, player in enumerate(players):
            ctrl = CONTROLS[idx]
            dx = 0
            jumping = False
            if keys[ctrl['left']]:
                dx = -MOVE_V
                player.dir = -1
            if keys[ctrl['right']]:
                dx = MOVE_V
                player.dir = 1
            moving = dx != 0
            if dx != 0:
                for _ in range(abs(dx)):
                    player.try_move(int(dx/abs(dx)), 0, colormap_mask)
            player.vy += GRAVITY
            if player.vy > 22:
                player.vy = 22
            # --- COLISÃO COM ROBO PILOTO COMO PLATAFORMA ---
            # Verifica se o player está em cima do robô piloto
            player_rect = player.rect()
            robo_rect = pygame.Rect(int(robo_piloto.x), int(robo_piloto.y), ROBO_PILOTO_W, ROBO_PILOTO_H)
            # Considera "em cima" se os pés do player estão tocando o topo do robô e há interseção horizontal
            on_robo = (
                player_rect.bottom <= robo_rect.top + 16 and
                player_rect.bottom >= robo_rect.top - 16 and
                player_rect.right > robo_rect.left + 10 and
                player_rect.left < robo_rect.right - 10
            )
            
            # --- COLISÃO COM PLATAFORMA MÓVEL ---
            movel_rect = movel_platform.get_rect()
            on_movel = movel_platform.check_player_on_top(player)
            
            if on_robo and player.vy >= 0:
                player.y = robo_rect.top - SPRITE_H
                player.vy = 0
                player.on_ground = True
                # Move junto com o robô piloto
                player.x += robo_piloto.dir * ROBO_PILOTO_SPEED
            elif on_movel and player.vy >= 0:
                player.y = movel_rect.top - SPRITE_H
                player.vy = 0
                player.on_ground = True
                # Move junto com a plataforma móvel (mantém posição relativa)
            else:
                # Queda normal
                for _ in range(abs(int(player.vy))):
                    if not player.try_move(0, int(player.vy/abs(player.vy)), colormap_mask):
                        player.vy = 0
                        break
            if keys[ctrl['jump']] and (player.check_on_ground(colormap_mask) or on_robo or on_movel):
                player.vy = JUMP_V
                jumping = True
            player.on_ground = player.check_on_ground(colormap_mask) or on_robo or on_movel
            player.update_state(moving, not player.on_ground)
            player.update_anim(moving)
            player.unstick_from_map(colormap_mask)
            # Limitar os jogadores dentro do mapa (colormap)
            if player.x < SPRITE_W // 2:
                player.x = SPRITE_W // 2
            if player.x > map_w - SPRITE_W // 2:
                player.x = map_w - SPRITE_W // 2
            # Permitir sair da borda superior (não limitar y < 0)
            if player.y > base_height - SPRITE_H:
                player.y = base_height - SPRITE_H
        # Atualiza robôs
        for robot in robots:
            robot.update()
        robo_piloto.update()
        
        # Atualiza plataforma móvel
        movel_platform.update()
        robots = [r for r in robots if not r.is_off_screen(0)]
        while len(robots) < ROBOT_COUNT:
            robots.append(DroneRobot(robot_sheet, map_w, map_h))
        # --- CAMERA ---
        # Centralizar a câmera no centro dos jogadores
        min_x = min(p.x for p in players)
        max_x = max(p.x for p in players)
        min_y = min(p.y for p in players)
        max_y = max(p.y for p in players)
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        cam_x = center_x - base_width // 2
        cam_y = center_y - base_height // 2
        # Limitar a câmera para não mostrar fora do mapa
        cam_x = max(0, min(cam_x, map_w - base_width))
        cam_y = max(0, min(cam_y, map_h - base_height))
        # --- DESENHO ---
        game_surface = pygame.Surface((base_width, base_height))
        # Desenhar apenas o fundo noite.png em todo o mapa
        for x in range(0, map_w, noite_img.get_width()):
            game_surface.blit(noite_img, (x - cam_x, 0 - cam_y))
        game_surface.blit(map_img, (-cam_x, -cam_y))
        for player in players:
            player.draw(game_surface, cam_x, cam_y, font)
        for robot in robots:
            robot.draw(game_surface, cam_x, cam_y)
        robo_piloto.draw(game_surface, cam_x, cam_y)
        
        # Desenhar plataforma móvel
        movel_platform.draw(game_surface, cam_x, cam_y)
        instr = font.render('Jackson: A/D/W | Jean: J/L/I | Jean: ←/→/↑', True, (0,255,255))
        game_surface.blit(instr, (game_surface.get_width()/2 - instr.get_width()/2, 30))
        # Ajuste de proporção e centralização igual ao main.py
        window_width, window_height = screen.get_size()
        scale = min(window_width / base_width, window_height / base_height)
        scaled_width = int(base_width * scale)
        scaled_height = int(base_height * scale)
        scaled_surface = pygame.transform.smoothscale(game_surface, (scaled_width, scaled_height))
        x_offset = (window_width - scaled_width) // 2
        y_offset = (window_height - scaled_height) // 2
        screen.fill((0, 0, 0))
        screen.blit(scaled_surface, (x_offset, y_offset))
        pygame.display.flip()
        clock.tick(60)
    return 'success' 