"""
Exemplo de uso dos sistemas implementados no jogo Desprogramados
Demonstra como usar logging, analytics, tratamento de erros e otimizações
"""

import pygame
import time
from config import GameConfig
from logger import log_info, log_debug, log_warning, log_error, log_game_event
from exceptions import safe_resource_load, handle_critical_error
from analytics import track_event, track_player_action, get_analytics_report
from optimizations import (
    render_manager, memory_manager, performance_monitor, 
    get_performance_report, get_cache_stats
)

def example_logging_usage():
    """Exemplo de uso do sistema de logging"""
    print("=== Exemplo de Logging ===")
    
    # Logs de diferentes níveis
    log_info("Jogo iniciado com sucesso")
    log_debug("Posição do jogador: (100, 200)")
    log_warning("Arquivo de música não encontrado")
    log_error("Falha ao carregar textura")
    
    # Logs específicos do jogo
    log_game_event('player_jump', {'player': 'Jackson', 'position': (100, 200)})
    log_game_event('level_start', {'level': 'paint'})
    
    print("Logs salvos em logs/game.log")

def example_error_handling():
    """Exemplo de tratamento de erros robusto"""
    print("\n=== Exemplo de Tratamento de Erros ===")
    
    # Carregamento seguro de recursos
    try:
        # Tentar carregar uma imagem que não existe
        image = safe_resource_load(pygame.image.load, "imagem", "assets/nao_existe.png")
        if image is None:
            log_warning("Imagem não encontrada, usando fallback")
    except Exception as e:
        log_error(f"Erro crítico: {e}")
        handle_critical_error(e, "Carregamento de imagem")
    
    # Tratamento de operações do pygame
    try:
        # Simular erro do pygame
        raise pygame.error("Erro simulado do pygame")
    except pygame.error as e:
        log_error(f"Erro do pygame: {e}")

def example_analytics_usage():
    """Exemplo de uso do sistema de analytics"""
    print("\n=== Exemplo de Analytics ===")
    
    # Registrar eventos do jogo
    track_event('game_start', {'version': '1.0'})
    track_player_action('Jackson', 'jump')
    track_player_action('Jean', 'paint')
    track_player_action('Jean', 'move')
    
    # Simular algumas ações
    for i in range(5):
        track_player_action('Jackson', 'jump')
        time.sleep(0.1)
    
    # Gerar relatório
    report = get_analytics_report()
    print("Relatório de Analytics:")
    print(f"- Tempo de sessão: {report['session_summary']['duration']:.2f}s")
    print(f"- Ações do Jackson: {report['player_stats']['Jackson']}")
    print(f"- Ações do Jean: {report['player_stats']['Jean']}")

def example_optimizations_usage():
    """Exemplo de uso das otimizações"""
    print("\n=== Exemplo de Otimizações ===")
    
    # Cache de texturas
    texture1 = memory_manager.get_texture('assets/jackson.png')
    texture2 = memory_manager.get_texture('assets/Jean.png')
    
    # Carregar novamente (deve usar cache)
    texture1_cached = memory_manager.get_texture('assets/jackson.png')
    
    # Estatísticas do cache
    cache_stats = get_cache_stats()
    print("Estatísticas do Cache:")
    print(f"- Texturas em cache: {cache_stats['texture_cache_size']}")
    print(f"- Hits: {cache_stats['cache_hits']}")
    print(f"- Misses: {cache_stats['cache_misses']}")
    print(f"- Taxa de hit: {cache_stats['hit_rate']:.2%}")
    
    # Métricas de performance
    for i in range(10):
        performance_monitor.add_metric('fps', 60 + i)
        performance_monitor.add_metric('render_time', 16 + i * 0.1)
        time.sleep(0.01)
    
    perf_report = get_performance_report()
    print("\nRelatório de Performance:")
    print(f"- FPS médio: {perf_report['avg_fps']:.1f}")
    print(f"- Tempo de renderização médio: {perf_report['avg_render_time']:.2f}ms")
    print(f"- Tempo de execução: {perf_report['uptime']:.2f}s")

def example_config_usage():
    """Exemplo de uso das configurações centralizadas"""
    print("\n=== Exemplo de Configurações ===")
    
    print("Configurações do Jogo:")
    print(f"- Resolução: {GameConfig.BASE_WIDTH}x{GameConfig.BASE_HEIGHT}")
    print(f"- FPS: {GameConfig.FPS}")
    print(f"- Gravidade: {GameConfig.GRAVITY}")
    print(f"- Velocidade de movimento: {GameConfig.MOVE_VELOCITY}")
    
    print("\nControles:")
    for i, control in enumerate(GameConfig.CONTROLS):
        print(f"- {control['name']}: A/D={control['left']}/{control['right']}, Jump={control['jump']}")
    
    print(f"\nCores disponíveis: {list(GameConfig.COLORS.keys())}")
    print(f"Estados do jogo: {list(GameConfig.GAME_STATES.values())}")

def main():
    """Função principal do exemplo"""
    print("=== Exemplo de Uso dos Sistemas do Jogo Desprogramados ===\n")
    
    # Inicializar pygame para os exemplos
    pygame.init()
    
    try:
        example_logging_usage()
        example_error_handling()
        example_analytics_usage()
        example_optimizations_usage()
        example_config_usage()
        
        print("\n=== Todos os exemplos executados com sucesso! ===")
        print("Verifique os arquivos gerados:")
        print("- logs/game.log (logs do jogo)")
        print("- analytics.json (dados de analytics)")
        
    except Exception as e:
        log_error(f"Erro durante execução dos exemplos: {e}")
        handle_critical_error(e, "Execução de exemplos")
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    main() 