"""
Sistema de Otimizações Avançadas para o jogo Desprogramados
Melhora performance através de técnicas de otimização
"""

import pygame
import time
import weakref
from collections import defaultdict
from logger import log_debug, log_performance
from config import GameConfig

class RenderManager:
    """Gerenciador de renderização otimizado"""
    
    def __init__(self):
        self.dirty_rects = []
        self.background_cache = {}
        self.sprite_cache = {}
        self.last_render_time = 0
        self.render_stats = {
            'frames_rendered': 0,
            'total_render_time': 0,
            'avg_render_time': 0
        }
    
    def add_dirty_rect(self, rect):
        """Adiciona área suja para renderização otimizada"""
        if rect not in self.dirty_rects:
            self.dirty_rects.append(rect)
    
    def clear_dirty_rects(self):
        """Limpa lista de áreas sujas"""
        self.dirty_rects.clear()
    
    def get_dirty_rects(self):
        """Retorna áreas sujas para renderização"""
        return self.dirty_rects.copy()
    
    def cache_background(self, level_id, background):
        """Cache de backgrounds para evitar recarregamento"""
        self.background_cache[level_id] = background
    
    def get_cached_background(self, level_id):
        """Retorna background do cache"""
        return self.background_cache.get(level_id)
    
    def cache_sprite(self, sprite_key, sprite_surface):
        """Cache de sprites para reutilização"""
        self.sprite_cache[sprite_key] = sprite_surface
    
    def get_cached_sprite(self, sprite_key):
        """Retorna sprite do cache"""
        return self.sprite_cache.get(sprite_key)
    
    def update_render_stats(self, render_time):
        """Atualiza estatísticas de renderização"""
        self.render_stats['frames_rendered'] += 1
        self.render_stats['total_render_time'] += render_time
        self.render_stats['avg_render_time'] = (
            self.render_stats['total_render_time'] / self.render_stats['frames_rendered']
        )
        
        log_performance('render_frame', render_time)

class ObjectPool:
    """Pool de objetos para reduzir alocação de memória"""
    
    def __init__(self, object_class, initial_size=10):
        self.object_class = object_class
        self.pool = [object_class() for _ in range(initial_size)]
        self.active_objects = []
    
    def get_object(self):
        """Obtém objeto do pool ou cria novo"""
        if self.pool:
            obj = self.pool.pop()
            self.active_objects.append(obj)
            return obj
        else:
            obj = self.object_class()
            self.active_objects.append(obj)
            return obj
    
    def return_object(self, obj):
        """Retorna objeto ao pool"""
        if obj in self.active_objects:
            self.active_objects.remove(obj)
            # Reset do objeto se tiver método reset
            if hasattr(obj, 'reset'):
                obj.reset()
            self.pool.append(obj)
    
    def cleanup(self):
        """Limpa objetos inativos"""
        self.pool.clear()

class SpatialHash:
    """Hash espacial para otimizar colisões"""
    
    def __init__(self, cell_size=64):
        self.cell_size = cell_size
        self.grid = defaultdict(list)
    
    def get_cell_key(self, x, y):
        """Calcula chave da célula para posição"""
        return (x // self.cell_size, y // self.cell_size)
    
    def add_object(self, obj, x, y, width, height):
        """Adiciona objeto ao hash espacial"""
        # Calcular células que o objeto ocupa
        start_cell = self.get_cell_key(x, y)
        end_cell = self.get_cell_key(x + width, y + height)
        
        for cell_x in range(start_cell[0], end_cell[0] + 1):
            for cell_y in range(start_cell[1], end_cell[1] + 1):
                self.grid[(cell_x, cell_y)].append(obj)
    
    def get_nearby_objects(self, x, y, radius):
        """Retorna objetos próximos à posição"""
        center_cell = self.get_cell_key(x, y)
        cells_to_check = radius // self.cell_size + 1
        
        nearby_objects = set()
        for dx in range(-cells_to_check, cells_to_check + 1):
            for dy in range(-cells_to_check, cells_to_check + 1):
                cell_key = (center_cell[0] + dx, center_cell[1] + dy)
                if cell_key in self.grid:
                    nearby_objects.update(self.grid[cell_key])
        
        return list(nearby_objects)
    
    def clear(self):
        """Limpa hash espacial"""
        self.grid.clear()

class FrameRateController:
    """Controlador de taxa de quadros otimizado"""
    
    def __init__(self, target_fps=60):
        self.target_fps = target_fps
        self.target_frame_time = 1000.0 / target_fps
        self.last_frame_time = time.time()
        self.frame_times = []
        self.max_frame_history = 60
        
    def update(self):
        """Atualiza controlador de FPS"""
        current_time = time.time()
        frame_time = (current_time - self.last_frame_time) * 1000  # em ms
        self.last_frame_time = current_time
        
        self.frame_times.append(frame_time)
        if len(self.frame_times) > self.max_frame_history:
            self.frame_times.pop(0)
        
        # Calcular FPS atual
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        current_fps = 1000.0 / avg_frame_time if avg_frame_time > 0 else 0
        
        return current_fps, frame_time
    
    def should_skip_frame(self):
        """Determina se deve pular frame para manter FPS"""
        if len(self.frame_times) < 2:
            return False
        
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return avg_frame_time > self.target_frame_time * 1.1

class MemoryManager:
    """Gerenciador de memória para otimização"""
    
    def __init__(self):
        self.texture_cache = {}
        self.sound_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get_texture(self, path):
        """Obtém textura do cache ou carrega"""
        if path in self.texture_cache:
            self.cache_hits += 1
            return self.texture_cache[path]
        else:
            self.cache_misses += 1
            try:
                texture = pygame.image.load(path).convert_alpha()
                self.texture_cache[path] = texture
                return texture
            except Exception as e:
                log_debug(f"Erro ao carregar textura {path}: {e}")
                return None
    
    def get_sound(self, path):
        """Obtém som do cache ou carrega"""
        if path in self.sound_cache:
            self.cache_hits += 1
            return self.sound_cache[path]
        else:
            self.cache_misses += 1
            try:
                sound = pygame.mixer.Sound(path)
                self.sound_cache[path] = sound
                return sound
            except Exception as e:
                log_debug(f"Erro ao carregar som {path}: {e}")
                return None
    
    def clear_unused_cache(self):
        """Limpa cache não utilizado"""
        # Implementar lógica para limpar cache baseado em uso
        pass
    
    def get_cache_stats(self):
        """Retorna estatísticas do cache"""
        return {
            'texture_cache_size': len(self.texture_cache),
            'sound_cache_size': len(self.sound_cache),
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0
        }

class PerformanceMonitor:
    """Monitor de performance em tempo real"""
    
    def __init__(self):
        self.metrics = {
            'fps': [],
            'render_time': [],
            'update_time': [],
            'memory_usage': []
        }
        self.max_history = 100
        self.start_time = time.time()
    
    def add_metric(self, metric_type, value):
        """Adiciona métrica de performance"""
        if metric_type in self.metrics:
            self.metrics[metric_type].append(value)
            if len(self.metrics[metric_type]) > self.max_history:
                self.metrics[metric_type].pop(0)
    
    def get_average(self, metric_type):
        """Retorna média de uma métrica"""
        if metric_type in self.metrics and self.metrics[metric_type]:
            return sum(self.metrics[metric_type]) / len(self.metrics[metric_type])
        return 0
    
    def get_performance_report(self):
        """Gera relatório de performance"""
        return {
            'avg_fps': self.get_average('fps'),
            'avg_render_time': self.get_average('render_time'),
            'avg_update_time': self.get_average('update_time'),
            'uptime': time.time() - self.start_time
        }

class OptimizedSurface:
    """Superfície otimizada com cache de transformações"""
    
    def __init__(self, surface):
        self.original_surface = surface
        self.scaled_cache = {}
        self.rotated_cache = {}
    
    def get_scaled(self, size):
        """Retorna versão escalada da superfície (com cache)"""
        if size not in self.scaled_cache:
            self.scaled_cache[size] = pygame.transform.smoothscale(self.original_surface, size)
        return self.scaled_cache[size]
    
    def get_rotated(self, angle):
        """Retorna versão rotacionada da superfície (com cache)"""
        if angle not in self.rotated_cache:
            self.rotated_cache[angle] = pygame.transform.rotate(self.original_surface, angle)
        return self.rotated_cache[angle]
    
    def clear_cache(self):
        """Limpa cache de transformações"""
        self.scaled_cache.clear()
        self.rotated_cache.clear()

# Instâncias globais dos sistemas de otimização
render_manager = RenderManager()
object_pool = ObjectPool(object)  # Pool genérico
spatial_hash = SpatialHash()
frame_rate_controller = FrameRateController(GameConfig.FPS)
memory_manager = MemoryManager()
performance_monitor = PerformanceMonitor()

def optimize_surface_loading(surface_path):
    """Otimiza carregamento de superfícies"""
    return memory_manager.get_texture(surface_path)

def optimize_sound_loading(sound_path):
    """Otimiza carregamento de sons"""
    return memory_manager.get_sound(sound_path)

def update_performance_metrics(fps, render_time, update_time):
    """Atualiza métricas de performance"""
    performance_monitor.add_metric('fps', fps)
    performance_monitor.add_metric('render_time', render_time)
    performance_monitor.add_metric('update_time', update_time)

def get_performance_report():
    """Retorna relatório de performance"""
    return performance_monitor.get_performance_report()

def get_cache_stats():
    """Retorna estatísticas do cache"""
    return memory_manager.get_cache_stats() 