import pygame
import os
import random
import math

SPRITES = {
    'Jackson': os.path.join('assets', 'jackson.png'),
    'Jean': os.path.join('assets', 'Jean.png'),
}
COLORMAP_PATH = os.path.join('assets', 'paint_colormap.png')
BUTTONS_PATH = os.path.join('assets', 'paint_buttons.png')
ERRO_PATH = os.path.join('assets', 'paint_erro.png')
SCREEN_PATH = os.path.join('assets', 'paint_screen.png')

PLAYER_SIZE = 128
SPRITE_W, SPRITE_H = 128, 128
GRAVITY = 1.2
JUMP_V = -16
MOVE_V = 8

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

def is_color_near(color, target, tol=40):
    return all(abs(c-t) <= tol for c, t in zip(color, target))

class Player:
    def __init__(self, name, x, y, spritesheet):
        self.name = name
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.state = 'idle'
        self.anim_frame = 0
        self.anim_timer = 0
        self.dir = 1
        self.spritesheet = spritesheet
        self.masks = self._make_masks()
        self.visible = True  # Novo atributo para visibilidade

    def _make_masks(self):
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

    def draw(self, surf, font):
        img = self.get_surface()
        px = int(self.x - SPRITE_W//2)
        py = int(self.y)
        surf.blit(img, (px, py))
        label = font.render(self.name, True, (0,255,255))
        surf.blit(label, (px, py-32))

    def try_move(self, dx, dy, colormap_mask, draw_mask):
        new_x = self.x + dx
        new_y = self.y + dy
        mask = self.get_mask()
        for ramp in range(5):  # RAMP_TOLERANCE = 5
            test_y = new_y - ramp if dx != 0 else new_y
            offset = (int(new_x - SPRITE_W//2), int(test_y))
            # Permite andar se NÃO houver colisão no colormap (preto) OU se houver plataforma desenhada
            if not colormap_mask.overlap(mask, offset) or draw_mask.overlap(mask, offset):
                # Só checa parede vertical se não estiver subindo rampa
                if dx != 0 and ramp == 0 and self.detect_vertical_wall(colormap_mask, draw_mask, new_x, test_y):
                    continue
                self.x = new_x
                self.y = test_y
                return True
        return False

    def detect_vertical_wall(self, colormap_mask, draw_mask, x, y):
        mask = self.get_mask()
        for dx in [0, SPRITE_W-1]:
            wall_height = 0
            for dy in range(SPRITE_H):
                if mask.get_at((dx, dy)) and (colormap_mask.get_at((int(x - SPRITE_W//2) + dx, int(y) + dy)) or draw_mask.get_at((int(x - SPRITE_W//2) + dx, int(y) + dy))):
                    wall_height += 1
                    if wall_height > 5:
                        return True
        return False

    def check_on_ground(self, colormap_mask, draw_mask):
        # Cria uma máscara retangular fina sob os pés do personagem
        foot_mask = pygame.Mask((SPRITE_W, 2), fill=True)
        offset = (int(self.x - SPRITE_W//2), int(self.y + SPRITE_H - 2))
        for mask in [draw_mask, colormap_mask]:
            if mask.overlap(foot_mask, offset):
                return True
        return False

    def unstick_from_map(self, colormap_mask, draw_mask):
        max_attempts = 20
        mask = self.get_mask()
        for dy in range(1, max_attempts):
            offset = (int(self.x - SPRITE_W//2), int(self.y - dy))
            if not (colormap_mask.overlap(mask, offset) or draw_mask.overlap(mask, offset)):
                self.y -= dy
                return
        for dx in range(1, max_attempts):
            offset = (int(self.x - SPRITE_W//2 - dx), int(self.y))
            if not (colormap_mask.overlap(mask, offset) or draw_mask.overlap(mask, offset)):
                self.x -= dx
                return
            offset = (int(self.x - SPRITE_W//2 + dx), int(self.y))
            if not (colormap_mask.overlap(mask, offset) or draw_mask.overlap(mask, offset)):
                self.x += dx
                return
        for dy in range(1, max_attempts):
            offset = (int(self.x - SPRITE_W//2), int(self.y + dy))
            if not (colormap_mask.overlap(mask, offset) or draw_mask.overlap(mask, offset)):
                self.y += dy
                return

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


def run_paint_minigame(screen, clock):
    pygame.display.set_caption('Desprogramados - Paint')
    base_width, base_height = 1920, 1080
    font = pygame.font.SysFont('Arial', 28)
    spritesheets = {name: pygame.image.load(path).convert_alpha() for name, path in SPRITES.items()}
    colormap_img = pygame.image.load(COLORMAP_PATH).convert_alpha()
    colormap_mask = pygame.mask.from_surface(colormap_img)
    exit_mask = pygame.mask.from_threshold(colormap_img, (0,0,255,255), (1,1,1,255)) # azul = saída
    buttons_img = pygame.image.load(BUTTONS_PATH).convert_alpha()
    # --- Remover lógica de erro ---
    # 1. Não carregar erro_img
    # 2. Não criar erro_rects, erro_active
    # 3. Não ativar erro ao clicar no preto
    # 4. Não desenhar erro na tela
    screen_img = pygame.image.load(SCREEN_PATH).convert_alpha() if os.path.exists(SCREEN_PATH) else None
    players = [
        Player('Jackson', 100, 800, spritesheets['Jackson']),
        Player('Jean', 300, 800, spritesheets['Jean']),
    ]
    removed_players = []  # Lista de jogadores que já sumiram
    draw_layer = pygame.Surface((base_width, base_height), pygame.SRCALPHA)
    draw_layer.fill((0,0,0,0))  # Inicializa totalmente transparente
    # Círculo de teste fixo
    pygame.draw.circle(draw_layer, (255,0,0,255), (100,100), 30)
    draw_mask = pygame.mask.from_surface(draw_layer)
    mode = 'none' # 'draw', 'erase', 'none', 'erro'
    # Remover erro_img, erro_rects, erro_active, e lógica associada
    # Substituir o bloco de ativação do erro por um pass
    # Exemplo:
    # if is_color_near(color, (0,0,0)):
    #     pass  # botão preto não faz nada
    running = True
    brush_radius = 8  # Pincel menor
    last_draw_pos = None  # Para evitar atualizações desnecessárias
    while running:
        updated_draw = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                mx = int(mx * base_width / screen.get_width())
                my = int(my * base_height / screen.get_height())
                color = buttons_img.get_at((mx, my))[:3]
                if is_color_near(color, (0,255,0)):
                    mode = 'draw'
                elif is_color_near(color, (255,0,0)):
                    mode = 'erase'
                elif is_color_near(color, (0,0,0)):
                    pass
        if mode in ['draw', 'erase'] and pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            mx = int(mx * base_width / screen.get_width())
            my = int(my * base_height / screen.get_height())
            color = colormap_img.get_at((mx, my))[:3]
            if last_draw_pos != (mx, my, mode):
                if mode == 'draw':
                    if color != (0,0,0):
                        pygame.draw.circle(draw_layer, (0,0,0,255), (mx, my), brush_radius)
                        updated_draw = True
                elif mode == 'erase':
                    pygame.draw.circle(draw_layer, (0,0,0,0), (mx, my), brush_radius)
                    updated_draw = True
                last_draw_pos = (mx, my, mode)
        else:
            last_draw_pos = None
        if updated_draw:
            draw_mask = pygame.mask.from_surface(draw_layer)
        keys = pygame.key.get_pressed()
        # Atualização dos jogadores
        for idx, player in enumerate(players):  # Iterar sobre cópia para remoção segura
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
                    player.try_move(int(dx/abs(dx)), 0, colormap_mask, draw_mask)
            player.vy += GRAVITY
            if player.vy > 22:
                player.vy = 22
            for _ in range(abs(int(player.vy))):
                if not player.try_move(0, int(player.vy/abs(player.vy)), colormap_mask, draw_mask):
                    player.vy = 0
                    break
            if keys[ctrl['jump']] and player.check_on_ground(colormap_mask, draw_mask):
                player.vy = JUMP_V
                jumping = True
            player.on_ground = player.check_on_ground(colormap_mask, draw_mask)
            player.update_state(moving, not player.on_ground)
            player.update_anim(moving)
            player.unstick_from_map(colormap_mask, draw_mask)
            # Se encostar no azul, fica invisível
            if player.visible and exit_mask.overlap(player.get_mask(), (int(player.x - SPRITE_W//2), int(player.y))):
                player.visible = False
        # Vitória: todos invisíveis
        if all(not p.visible for p in players):
            return 'success'

        # Desenho da fase
        surf = pygame.Surface((base_width, base_height))
        surf.blit(colormap_img, (0,0))  # paint_colormap
        if screen_img:
            surf.blit(screen_img, (0,0))  # paint_screen
        for player in players:
            if player.visible:
                player.draw(surf, font)       # jogadores
        # O desenho deve ficar acima de tudo, exceto erro e botões
        surf.blit(draw_layer, (0,0))      # desenho do jogador (acima dos jogadores)
        # Remover erro_img, erro_rects, erro_active, e lógica associada
        # Substituir o bloco de ativação do erro por um pass
        # Exemplo:
        # if erro_active: ... (remover)
        # paint_buttons semi-transparente por cima de tudo
        buttons_alpha = 80
        buttons_img_alpha = buttons_img.copy()
        buttons_img_alpha.fill((255,255,255,buttons_alpha), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(buttons_img_alpha, (0,0))
        # paint_buttons invisível, mas clicável
        # Não desenhar visualmente, mas manter a lógica de clique
        # (Nada a fazer aqui, pois já usamos buttons_img.get_at para detecção de clique)
        window_width, window_height = screen.get_size()
        if window_width == base_width and window_height == base_height:
            screen.blit(surf, (0,0))
        else:
            scaled_surface = pygame.transform.smoothscale(surf, (window_width, window_height))
            screen.blit(scaled_surface, (0,0))
        pygame.display.flip()
        clock.tick(60) 

def run_paint_minigame_custom(screen, clock, bg_path, colormap_path, screen_path=None, char_positions=None):
    pygame.display.set_caption('Desprogramados - Paint')
    base_width, base_height = 1920, 1080
    font = pygame.font.SysFont('Arial', 28)
    # Fonte do diálogo
    dialog_font_path = os.path.join('assets', 'Pixellari.ttf')
    dialog_font = pygame.font.Font(dialog_font_path, 50)
    # Caixa de diálogo
    chat_img = pygame.image.load(os.path.join('assets', 'chat.png')).convert_alpha()
    CHAT_W, CHAT_H = 540, 174
    CHAT_TEXT_X, CHAT_TEXT_Y = 270, 87
    CHAT_TEXT_W, CHAT_TEXT_H = 500, 120
    # Diálogos de exemplo (substitua pelo texto desejado)
    dialog_sequence = [
        {'speaker': 'Jackson', 'text': 'Mas o que está acontecendo!? Isso aqui virou uma Schlachtfest ou um episódio perdido de Black Mirror?'},
        {'speaker': 'Jackson', 'text': 'A inteligência artificial se revoltou? Ou é só um grupo de robôs dançando Macarena?'},
        {'speaker': 'Jean', 'text': 'Eu sabia que devia ter dado bom dia pro ChatGPT... Agora ele tá de TPM digital!'},
        {'speaker': 'Jackson', 'text': 'Vamos investigar! Eles estão vindo daquela direção!'},
        {'speaker': 'Jean', 'text': 'As ruas estão perigosas! Vamos pelo telhado... igual no Assassins Creed, só que com menos preparo físico.'},

       
    ]
    dialog_index = 0
    dialog_char_index = 0
    dialog_timer = 0
    dialog_speed = 20  # ms por letra (mais rápido)
    dialog_active = False
    dialog_done = False
    dialog_wait_next = False
    dialog_end_time = None
    auto_run = False
    auto_run_start = None
    spritesheets = {name: pygame.image.load(path).convert_alpha() for name, path in SPRITES.items()}
    colormap_img = pygame.image.load(colormap_path).convert_alpha()
    colormap_mask = pygame.mask.from_surface(colormap_img)
    exit_mask = pygame.mask.from_threshold(colormap_img, (0,0,255,255), (1,1,1,255)) # azul = saída
    buttons_img = pygame.image.load(BUTTONS_PATH).convert_alpha()
    bg_img = pygame.image.load(bg_path).convert_alpha()
    screen_img = pygame.image.load(screen_path).convert_alpha() if screen_path and os.path.exists(screen_path) else None
    if char_positions is not None:
        players = [
            Player('Jackson', char_positions[0][0], char_positions[0][1], spritesheets['Jackson']),
            Player('Jean', char_positions[1][0], char_positions[1][1], spritesheets['Jean']),
        ]
    else:
        players = [
            Player('Jackson', 100, 800, spritesheets['Jackson']),
            Player('Jean', 300, 800, spritesheets['Jean']),
        ]
    draw_layer = pygame.Surface((base_width, base_height), pygame.SRCALPHA)
    draw_layer.fill((0,0,0,0))
    pygame.draw.circle(draw_layer, (255,0,0,255), (100,100), 30)
    draw_mask = pygame.mask.from_surface(draw_layer)
    mode = 'none'
    running = True
    brush_radius = 8
    # Variáveis para animar o robo_marcha.png na fase begin
    robo_offset = 0
    robo_speed = 2  # velocidade reduzida
    robo_img = None
    robo_phase = 0.0
    is_begin_phase = os.path.basename(colormap_path) == 'begin_colormap.png'
    if is_begin_phase:
        robo_img = pygame.image.load(os.path.join('assets', 'robo_marcha.png')).convert_alpha()
        robo_w, robo_h = robo_img.get_width(), robo_img.get_height()
        dialog_active = True
        dialog_start_time = pygame.time.get_ticks()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if dialog_active and is_begin_phase:
                if event.type == pygame.KEYDOWN and event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    if dialog_wait_next:
                        dialog_index += 1
                        dialog_char_index = 0
                        dialog_wait_next = False
                        if dialog_index >= len(dialog_sequence):
                            dialog_active = False
                            dialog_done = True
                            dialog_end_time = pygame.time.get_ticks()
            if not dialog_active or not is_begin_phase:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    mx = int(mx * base_width / screen.get_width())
                    my = int(my * base_height / screen.get_height())
                    color = buttons_img.get_at((mx, my))[:3]
                    if is_color_near(color, (0,255,0)):
                        mode = 'draw'
                    elif is_color_near(color, (255,0,0)):
                        mode = 'erase'
                    elif is_color_near(color, (0,0,0)):
                        pass
        if dialog_active and is_begin_phase:
            now = pygame.time.get_ticks()
            if not dialog_wait_next:
                if dialog_char_index < len(dialog_sequence[dialog_index]['text']):
                    if now - dialog_timer > dialog_speed:
                        dialog_char_index += 1
                        dialog_timer = now
                else:
                    dialog_wait_next = True
        # Após o fim do diálogo, aguarda 1.5s e inicia corrida automática
        if dialog_done and not auto_run and dialog_end_time is not None:
            if pygame.time.get_ticks() - dialog_end_time > 1500:
                auto_run = True
                auto_run_start = pygame.time.get_ticks()
        if mode in ['draw', 'erase'] and pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            mx = int(mx * base_width / screen.get_width())
            my = int(my * base_height / screen.get_height())
            color = colormap_img.get_at((mx, my))[:3]
            if mode == 'draw':
                if color != (0,0,0):
                    pygame.draw.circle(draw_layer, (0,0,0,255), (mx, my), brush_radius)
            elif mode == 'erase':
                pygame.draw.circle(draw_layer, (0,0,0,0), (mx, my), brush_radius)
            draw_mask = pygame.mask.from_surface(draw_layer)
        keys = pygame.key.get_pressed()
        for idx, player in enumerate(players):
            ctrl = CONTROLS[idx]
            dx = 0
            jumping = False
            # Desativa controles esquerda/direita/pulo na tela begin
            if not is_begin_phase or not dialog_active:
                if keys[ctrl['left']]:
                    dx = -MOVE_V
                    player.dir = -1
                if keys[ctrl['right']]:
                    dx = MOVE_V
                    player.dir = 1
            # Corrida automática após diálogo
            if is_begin_phase and auto_run:
                dx = MOVE_V
                player.dir = 1
            moving = dx != 0
            if dx != 0:
                for _ in range(abs(dx)):
                    player.try_move(int(dx/abs(dx)), 0, colormap_mask, draw_mask)
            player.vy += GRAVITY
            if player.vy > 22:
                player.vy = 22
            for _ in range(abs(int(player.vy))):
                if not player.try_move(0, int(player.vy/abs(player.vy)), colormap_mask, draw_mask):
                    player.vy = 0
                    break
            # Desativa pulo na tela begin
            if not is_begin_phase or not dialog_active:
                if keys[ctrl['jump']] and player.check_on_ground(colormap_mask, draw_mask):
                    player.vy = JUMP_V
                    jumping = True
            player.on_ground = player.check_on_ground(colormap_mask, draw_mask)
            player.update_state(moving, not player.on_ground)
            player.update_anim(moving)
            player.unstick_from_map(colormap_mask, draw_mask)
            if player.visible and exit_mask.overlap(player.get_mask(), (int(player.x - SPRITE_W//2), int(player.y))):
                player.visible = False
        # Após todos saírem da tela, termina a fase
        if auto_run:
            if all(p.x > base_width + SPRITE_W for p in players):
                return 'success'
        elif all(not p.visible for p in players):
            return 'success'
        surf = pygame.Surface((base_width, base_height))
        surf.blit(bg_img, (0,0))
        # Só desenha o colormap se não for o begin_colormap.png
        if not (os.path.basename(colormap_path) == 'begin_colormap.png'):
            surf.blit(colormap_img, (0,0))
        if screen_img:
            surf.blit(screen_img, (0,0))
        for player in players:
            if player.visible:
                player.draw(surf, font)
        surf.blit(draw_layer, (0,0))
        # Efeito tile do robo_marcha.png sobrepondo tudo na fase begin
        if robo_img is not None:
            robo_offset = (robo_offset + robo_speed) % robo_w
            robo_phase += 0.28  # rápido, mas não tão abrupto
            amplitude = 14
            robo_y_offset = int(amplitude * abs(math.sin(robo_phase)))
            for y_tile in range(0, base_height, robo_h):
                for x_tile in range(-robo_w, base_width + robo_w, robo_w):
                    surf.blit(robo_img, (x_tile - robo_offset, y_tile + robo_y_offset))
        # Nova camada: robo_marcha2.png na frente de tudo
        if os.path.basename(colormap_path) == 'begin_colormap.png':
            robo2_img = pygame.image.load(os.path.join('assets', 'robo_marcha2.png')).convert_alpha()
            robo2_w, robo2_h = robo2_img.get_width(), robo2_img.get_height()
            if not hasattr(run_paint_minigame_custom, '_robo2_offset'):
                run_paint_minigame_custom._robo2_offset = 0
                run_paint_minigame_custom._robo2_phase = 0.0
            run_paint_minigame_custom._robo2_offset = (run_paint_minigame_custom._robo2_offset + 1.3) % robo2_w
            run_paint_minigame_custom._robo2_phase += 0.19  # mais lento
            amplitude2 = 14
            robo2_y_offset = int(amplitude2 * abs(math.sin(run_paint_minigame_custom._robo2_phase)))
            for y_tile in range(0, base_height, robo2_h):
                for x_tile in range(-robo2_w, base_width + robo2_w, robo2_w):
                    surf.blit(robo2_img, (x_tile - int(run_paint_minigame_custom._robo2_offset), y_tile + robo2_y_offset))
        # --- Desenhar diálogo se ativo ---
        if dialog_active and is_begin_phase:
            dialog = dialog_sequence[dialog_index]
            speaker = dialog['speaker']
            text = dialog['text'][:dialog_char_index]
            # Posição do personagem que está falando
            speaker_idx = next(i for i, p in enumerate(players) if p.name == speaker)
            px = int(players[speaker_idx].x)
            py = int(players[speaker_idx].y)
            chat_x = px - CHAT_W // 2
            chat_y = py - 35 - CHAT_H
            # Padding
            padding_left = 40
            padding_right = 40
            padding_top = 40
            padding_bottom = 40
            max_text_width = CHAT_TEXT_W - padding_left - padding_right
            max_text_height = CHAT_TEXT_H - padding_top - padding_bottom
            # Função para quebrar texto
            def wrap_text(text, font, max_width):
                words = text.split(' ')
                if not words:
                    return []
                
                lines = []
                current = ''
                for word in words:
                    test = current + (' ' if current else '') + word
                    if font.size(test)[0] <= max_width:
                        current = test
                    else:
                        if current:
                            lines.append(current)
                        current = word
                if current:
                    lines.append(current)
                return lines
            # Ajuste dinâmico do tamanho da fonte
            font_size = 60  # Revertido de 56 para 48
            min_font_size = 59  # Revertido de 24 para 20
            while font_size >= min_font_size:
                test_font = pygame.font.Font(dialog_font_path, font_size)
                lines = wrap_text(text, test_font, max_text_width)
                line_height = test_font.get_linesize()
                max_lines_by_height = max_text_height // line_height
                max_lines = min(3, max_lines_by_height)
                if len(lines) <= max_lines:
                    break
                font_size -= 2
            dialog_font_dynamic = pygame.font.Font(dialog_font_path, font_size)
            lines = wrap_text(text, dialog_font_dynamic, max_text_width)
            line_height = dialog_font_dynamic.get_linesize()
            max_lines_by_height = max_text_height // line_height
            max_lines = min(3, max_lines_by_height)
            lines = lines[:max_lines]
            text_x = chat_x + (CHAT_TEXT_X - (CHAT_W//2)) + padding_left
            text_y = chat_y + (CHAT_TEXT_Y - (CHAT_H//2)) + padding_top
            # Criar versão semi-transparente do chat (90% opacidade = 10% transparência)
            chat_alpha = chat_img.copy()
            chat_alpha.fill((255, 255, 255, 230), special_flags=pygame.BLEND_RGBA_MULT)  # 230/255 = ~90% opacidade
            surf.blit(chat_alpha, (chat_x, chat_y))
            for i, line in enumerate(lines):
                rendered = dialog_font_dynamic.render(line, True, (0,0,0))
                # Centralizar o texto horizontalmente
                line_width = rendered.get_width()
                centered_x = text_x + (max_text_width - line_width) // 2
                surf.blit(rendered, (centered_x, text_y + i * dialog_font_dynamic.get_linesize()))
            # Seta para continuar
            # (Removido: não desenhar mais o sinal '>>')
        buttons_alpha = 80
        buttons_img_alpha = buttons_img.copy()
        buttons_img_alpha.fill((255,255,255,buttons_alpha), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(buttons_img_alpha, (0,0))
        window_width, window_height = screen.get_size()
        scale = min(window_width / base_width, window_height / base_height)
        scaled_width = int(base_width * scale)
        scaled_height = int(base_height * scale)
        scaled_surface = pygame.transform.smoothscale(surf, (scaled_width, scaled_height))
        x_offset = (window_width - scaled_width) // 2
        y_offset = (window_height - scaled_height) // 2
        screen.fill((0,0,0))
        screen.blit(scaled_surface, (x_offset, y_offset))
        pygame.display.flip()
        clock.tick(60) 

def run_begin_minigame(screen, clock, bg_path, colormap_path, screen_path=None, char_positions=None):
    """Fase BEGIN separada da fase paint. Copiada de run_paint_minigame_custom, mas dedicada à introdução."""
    pygame.display.set_caption('Desprogramados - Begin')
    base_width, base_height = 1920, 1080
    font = pygame.font.SysFont('Arial', 56)
    dialog_font_path = os.path.join('assets', 'Pixellari.ttf')
    dialog_font = pygame.font.Font(dialog_font_path, 50)
    chat_img = pygame.image.load(os.path.join('assets', 'chat.png')).convert_alpha()
    CHAT_W, CHAT_H = 540, 174
    CHAT_TEXT_X, CHAT_TEXT_Y = 270, 87
    CHAT_TEXT_W, CHAT_TEXT_H = 540, 120
    dialog_sequence = [
        {'speaker': 'Jackson', 'text': 'Mas o que está acontecendo!? Isso aqui virou uma Schlachtfest ou um episódio perdido de Black Mirror?'},
        {'speaker': 'Jackson', 'text': 'A inteligência artificial se revoltou? Ou é só um grupo de robôs dançando Macarena?'},
        {'speaker': 'Jean', 'text': 'Eu sabia que devia ter dado bom dia pro ChatGPT... Agora ele tá de TPM digital!'},
        {'speaker': 'Jackson', 'text': 'Vamos investigar! Eles estão vindo daquela direção!'},
        {'speaker': 'Jean', 'text': 'As ruas estão perigosas! Vamos pelo telhado... igual no Assassins Creed, só que com menos preparo físico.'},
    ]
    dialog_index = 0
    dialog_char_index = 0
    dialog_timer = 0
    dialog_speed = 20
    dialog_active = True
    dialog_done = False
    dialog_wait_next = False
    dialog_end_time = None
    auto_run = False
    auto_run_start = None
    spritesheets = {name: pygame.image.load(path).convert_alpha() for name, path in SPRITES.items()}
    colormap_img = pygame.image.load(colormap_path).convert_alpha()
    colormap_mask = pygame.mask.from_surface(colormap_img)
    exit_mask = pygame.mask.from_threshold(colormap_img, (0,0,255,255), (1,1,1,255))
    buttons_img = pygame.image.load(BUTTONS_PATH).convert_alpha()
    bg_img = pygame.image.load(bg_path).convert_alpha()
    screen_img = pygame.image.load(screen_path).convert_alpha() if screen_path and os.path.exists(screen_path) else None
    if char_positions is not None:
        players = [
            Player('Jackson', char_positions[0][0], char_positions[0][1], spritesheets['Jackson']),
            Player('Jean', char_positions[1][0], char_positions[1][1], spritesheets['Jean']),
        ]
    else:
        # Posicionar personagens centralizados na tela
        num_players = 2
        total_width = num_players * 200  # 200 pixels de espaçamento entre personagens
        start_x = base_width // 2 - total_width // 2
        center_y = base_height - 300  # 300 pixels do fundo da tela
        
        players = [
            Player('Jackson', start_x + 100, center_y, spritesheets['Jackson']),
            Player('Jean', start_x + 300, center_y, spritesheets['Jean']),
        ]
    draw_layer = pygame.Surface((base_width, base_height), pygame.SRCALPHA)
    draw_layer.fill((0,0,0,0))
    pygame.draw.circle(draw_layer, (255,0,0,255), (100,100), 30)
    draw_mask = pygame.mask.from_surface(draw_layer)
    mode = 'none'
    running = True
    brush_radius = 8
    robo_offset = 0
    robo_speed = 2
    robo_img = pygame.image.load(os.path.join('assets', 'robo_marcha.png')).convert_alpha()
    robo_w, robo_h = robo_img.get_width(), robo_img.get_height()
    robo_phase = 0.0
    dialog_start_time = pygame.time.get_ticks()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if dialog_active:
                if event.type == pygame.KEYDOWN and event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    if dialog_wait_next:
                        dialog_index += 1
                        dialog_char_index = 0
                        dialog_wait_next = False
                        if dialog_index >= len(dialog_sequence):
                            dialog_active = False
                            dialog_done = True
                            dialog_end_time = pygame.time.get_ticks()
        now = pygame.time.get_ticks()
        if dialog_active:
            if not dialog_wait_next:
                if dialog_char_index < len(dialog_sequence[dialog_index]['text']):
                    if now - dialog_timer > dialog_speed:
                        dialog_char_index += 1
                        dialog_timer = now
                else:
                    dialog_wait_next = True
        if dialog_done and not auto_run and dialog_end_time is not None:
            if pygame.time.get_ticks() - dialog_end_time > 1500:
                auto_run = True
                auto_run_start = pygame.time.get_ticks()
                print("AUTO-RUN ATIVADO! Personagens começando a correr para a direita...")
        keys = pygame.key.get_pressed()
        for idx, player in enumerate(players):
            ctrl = CONTROLS[idx]
            dx = 0
            moving = False
            if auto_run:
                dx = int(MOVE_V * 2.0)  # velocidade reduzida para movimento mais lento
                player.dir = 1
                player.state = 'run_r'  # Força animação de correr para a direita
                moving = True
            if dx != 0:
                # Força movimento para a direita ignorando colisões durante auto_run
                if auto_run:
                    player.x += dx  # Move diretamente sem verificar colisões
                else:
                    for _ in range(abs(dx)):
                        player.try_move(int(dx/abs(dx)), 0, colormap_mask, draw_mask)
            player.vy += GRAVITY
            if player.vy > 22:
                player.vy = 22
            for _ in range(abs(int(player.vy))):
                if not player.try_move(0, int(player.vy/abs(player.vy)), colormap_mask, draw_mask):
                    player.vy = 0
                    break
            player.on_ground = player.check_on_ground(colormap_mask, draw_mask)
            player.update_state(moving, not player.on_ground)
            player.update_anim(moving)
            player.unstick_from_map(colormap_mask, draw_mask)
            if player.visible and exit_mask.overlap(player.get_mask(), (int(player.x - SPRITE_W//2), int(player.y))):
                player.visible = False
        # Efeito cinematic de zoom após todos saírem
        if auto_run:
            # Debug: mostrar posições dos jogadores
            if auto_run_start and (pygame.time.get_ticks() - auto_run_start) % 1000 < 16:  # A cada segundo
                print(f"Auto-run: Jackson({players[0].x:.1f}), Jean({players[1].x:.1f})")
            # Condição muito leniente: verifica se os jogadores estão próximos da borda direita
            if all(p.x > base_width - 400 for p in players):
                print("CONDIÇÃO DE SAÍDA ATINGIDA! Iniciando efeito cinematic...")
                # Cinematic: zoom in no bg_img
                zoom_duration = 3000  # 3 segundos
                zoom_start = pygame.time.get_ticks()
                while pygame.time.get_ticks() - zoom_start < zoom_duration:
                    t = (pygame.time.get_ticks() - zoom_start) / zoom_duration
                    zoom = 1.0 + 0.5 * t  # zoom de 1.0 até 1.5
                    zoom_w = int(base_width * zoom)
                    zoom_h = int(base_height * zoom)
                    zoomed_bg = pygame.transform.smoothscale(bg_img, (zoom_w, zoom_h))
                    surf = pygame.Surface((base_width, base_height))
                    surf.blit(zoomed_bg, (-(zoom_w - base_width)//2, -(zoom_h - base_height)//2))
                    window_width, window_height = screen.get_size()
                    scale = min(window_width / base_width, window_height / base_height)
                    scaled_width = int(base_width * scale)
                    scaled_height = int(base_height * scale)
                    scaled_surface = pygame.transform.smoothscale(surf, (scaled_width, scaled_height))
                    x_offset = (window_width - scaled_width) // 2
                    y_offset = (window_height - scaled_height) // 2
                    screen.fill((0,0,0))
                    screen.blit(scaled_surface, (x_offset, y_offset))
                    pygame.display.flip()
                    clock.tick(60)
                return 'success'
        elif all(not p.visible for p in players):
            return 'success'
        surf = pygame.Surface((base_width, base_height))
        surf.blit(bg_img, (0,0))
        if screen_img:
            surf.blit(screen_img, (0,0))
        for player in players:
            if player.visible:
                player.draw(surf, font)
        surf.blit(draw_layer, (0,0))
        if robo_img is not None:
            robo_offset = (robo_offset + robo_speed) % robo_w
            robo_phase += 0.28
            amplitude = 14
            robo_y_offset = int(amplitude * abs(math.sin(robo_phase)))
            for y_tile in range(0, base_height, robo_h):
                for x_tile in range(-robo_w, base_width + robo_w, robo_w):
                    surf.blit(robo_img, (x_tile - robo_offset, y_tile + robo_y_offset))
        robo2_img = pygame.image.load(os.path.join('assets', 'robo_marcha2.png')).convert_alpha()
        robo2_w, robo2_h = robo2_img.get_width(), robo2_img.get_height()
        if not hasattr(run_begin_minigame, '_robo2_offset'):
            run_begin_minigame._robo2_offset = 0
            run_begin_minigame._robo2_phase = 0.0
        run_begin_minigame._robo2_offset = (run_begin_minigame._robo2_offset + 1.3) % robo2_w
        run_begin_minigame._robo2_phase += 0.19
        amplitude2 = 14
        robo2_y_offset = int(amplitude2 * abs(math.sin(run_begin_minigame._robo2_phase)))
        for y_tile in range(0, base_height, robo2_h):
            for x_tile in range(-robo2_w, base_width + robo2_w, robo2_w):
                surf.blit(robo2_img, (x_tile - int(run_begin_minigame._robo2_offset), y_tile + robo2_y_offset))
        if dialog_active:
            dialog = dialog_sequence[dialog_index]
            speaker = dialog['speaker']
            text = dialog['text'][:dialog_char_index]
            speaker_idx = next(i for i, p in enumerate(players) if p.name == speaker)
            px = int(players[speaker_idx].x)
            py = int(players[speaker_idx].y)
            chat_x = px - CHAT_W // 2
            chat_y = py - 35 - CHAT_H
            padding_left = 40
            padding_right = 40
            padding_top = 40
            padding_bottom = 40
            max_text_width = CHAT_TEXT_W - padding_left - padding_right
            max_text_height = CHAT_TEXT_H - padding_top - padding_bottom
            def wrap_text(text, font, max_width):
                words = text.split(' ')
                if not words:
                    return []
                
                lines = []
                current = ''
                for word in words:
                    test = current + (' ' if current else '') + word
                    if font.size(test)[0] <= max_width:
                        current = test
                    else:
                        if current:
                            lines.append(current)
                        current = word
                if current:
                    lines.append(current)
                return lines
            font_size = 48  # Revertido de 56 para 48
            min_font_size = 20  # Revertido de 24 para 20
            while font_size >= min_font_size:
                test_font = pygame.font.Font(dialog_font_path, font_size)
                lines = wrap_text(text, test_font, max_text_width)
                line_height = test_font.get_linesize()
                max_lines_by_height = max_text_height // line_height
                max_lines = min(3, max_lines_by_height)
                if len(lines) <= max_lines:
                    break
                font_size -= 2
            dialog_font_dynamic = pygame.font.Font(dialog_font_path, font_size)
            lines = wrap_text(text, dialog_font_dynamic, max_text_width)
            line_height = dialog_font_dynamic.get_linesize()
            max_lines_by_height = max_text_height // line_height
            max_lines = min(3, max_lines_by_height)
            lines = lines[:max_lines]
            text_x = chat_x + (CHAT_TEXT_X - (CHAT_W//2)) + padding_left
            text_y = chat_y + (CHAT_TEXT_Y - (CHAT_H//2)) + padding_top
            # Criar versão semi-transparente do chat (90% opacidade = 10% transparência)
            chat_alpha = chat_img.copy()
            chat_alpha.fill((255, 255, 255, 230), special_flags=pygame.BLEND_RGBA_MULT)  # 230/255 = ~90% opacidade
            surf.blit(chat_alpha, (chat_x, chat_y))
            for i, line in enumerate(lines):
                rendered = dialog_font_dynamic.render(line, True, (0,0,0))
                # Centralizar o texto horizontalmente
                line_width = rendered.get_width()
                centered_x = text_x + (max_text_width - line_width) // 2
                surf.blit(rendered, (centered_x, text_y + i * dialog_font_dynamic.get_linesize()))
            # (Removido: não desenhar mais o sinal '>>' aqui também)
        buttons_alpha = 80
        buttons_img_alpha = buttons_img.copy()
        buttons_img_alpha.fill((255,255,255,buttons_alpha), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(buttons_img_alpha, (0,0))
        window_width, window_height = screen.get_size()
        scale = min(window_width / base_width, window_height / base_height)
        scaled_width = int(base_width * scale)
        scaled_height = int(base_height * scale)
        scaled_surface = pygame.transform.smoothscale(surf, (scaled_width, scaled_height))
        x_offset = (window_width - scaled_width) // 2
        y_offset = (window_height - scaled_height) // 2
        screen.fill((0,0,0))
        screen.blit(scaled_surface, (x_offset, y_offset))
        pygame.display.flip()
        clock.tick(60) 