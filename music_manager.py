import pygame
import os
import random

class MusicManager:
    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.current_track = None
        self.current_state = None
        self.volume = 0.7
        self.fade_duration = 1000  # ms
        
        # Dicionário de músicas por estado do jogo
        self.music_tracks = {
            'menu': [
                'music/menu_theme.ogg',
                'music/menu_ambient.ogg'
            ],
            'paint': [
                'music/paint_creative.ogg',
                'music/paint_focus.ogg'
            ],
            'plataforma': [
                'music/platform_action.ogg',
                'music/platform_adventure.ogg'
            ],
            'begin': [
                'music/intro_theme.ogg'
            ]
        }
        
        # Verificar quais arquivos existem
        self._check_available_tracks()
        
    def _check_available_tracks(self):
        """Remove tracks que não existem dos dicionários"""
        for state in self.music_tracks:
            available_tracks = []
            for track in self.music_tracks[state]:
                if os.path.exists(track):
                    available_tracks.append(track)
            self.music_tracks[state] = available_tracks
    
    def play_for_state(self, game_state, loop=True, fade_in=True):
        """Toca música apropriada para o estado do jogo"""
        if game_state == self.current_state:
            return  # Já está tocando a música correta
            
        # Para a música atual se estiver tocando
        if pygame.mixer.music.get_busy():
            if fade_in:
                pygame.mixer.music.fadeout(self.fade_duration)
            else:
                pygame.mixer.music.stop()
        
        # Seleciona uma música aleatória para o estado
        if game_state in self.music_tracks and self.music_tracks[game_state]:
            track = random.choice(self.music_tracks[game_state])
            try:
                pygame.mixer.music.load(track)
                pygame.mixer.music.set_volume(self.volume)
                
                if fade_in and pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1 if loop else 0, fade_ms=self.fade_duration)
                else:
                    pygame.mixer.music.play(-1 if loop else 0)
                    
                self.current_track = track
                self.current_state = game_state
                print(f"Tocando música: {track}")
                
            except pygame.error as e:
                print(f"Erro ao carregar música {track}: {e}")
        else:
            print(f"Nenhuma música disponível para o estado: {game_state}")
    
    def stop(self, fade_out=True):
        """Para a música"""
        if pygame.mixer.music.get_busy():
            if fade_out:
                pygame.mixer.music.fadeout(self.fade_duration)
            else:
                pygame.mixer.music.stop()
        self.current_track = None
        self.current_state = None
    
    def set_volume(self, volume):
        """Define o volume (0.0 a 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
    
    def get_volume(self):
        """Retorna o volume atual"""
        return self.volume
    
    def is_playing(self):
        """Verifica se está tocando música"""
        return pygame.mixer.music.get_busy()
    
    def pause(self):
        """Pausa a música"""
        pygame.mixer.music.pause()
    
    def unpause(self):
        """Despausa a música"""
        pygame.mixer.music.unpause()
    
    def create_sample_tracks(self):
        """Cria arquivos de exemplo para demonstração"""
        # Esta função criaria arquivos de áudio simples para teste
        # Por enquanto, apenas cria arquivos vazios como placeholder
        sample_files = [
            'music/menu_theme.ogg',
            'music/menu_ambient.ogg',
            'music/paint_creative.ogg',
            'music/paint_focus.ogg',
            'music/platform_action.ogg',
            'music/platform_adventure.ogg',
            'music/intro_theme.ogg'
        ]
        
        for file_path in sample_files:
            if not os.path.exists(file_path):
                # Cria arquivo vazio como placeholder
                with open(file_path, 'w') as f:
                    f.write("# Placeholder para arquivo de música\n")
                    f.write(f"# Substitua este arquivo por: {os.path.basename(file_path)}\n")
                    f.write("# Formatos suportados: .ogg, .mp3, .wav\n")

# Instância global do gerenciador de música
music_manager = MusicManager()
