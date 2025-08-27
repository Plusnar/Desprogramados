"""
Sistema de tratamento de erros robusto para o jogo Desprogramados
Exceções customizadas para diferentes tipos de erro
"""

import pygame
import os
from logger import log_error, log_critical

class GameError(Exception):
    """Exceção base para todos os erros do jogo"""
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details
        log_error(f"GameError: {message}")
        if details:
            log_error(f"Details: {details}")

class ResourceLoadError(GameError):
    """Erro ao carregar recursos (imagens, sons, etc.)"""
    def __init__(self, resource_type, path, original_error=None):
        message = f"Falha ao carregar {resource_type}: {path}"
        details = f"Original error: {original_error}" if original_error else None
        super().__init__(message, details)
        self.resource_type = resource_type
        self.path = path
        self.original_error = original_error

class AudioError(GameError):
    """Erro relacionado ao sistema de áudio"""
    def __init__(self, operation, details=None):
        message = f"Erro de áudio durante {operation}"
        super().__init__(message, details)
        self.operation = operation

class PhysicsError(GameError):
    """Erro relacionado ao sistema de física"""
    def __init__(self, component, details=None):
        message = f"Erro de física no componente: {component}"
        super().__init__(message, details)
        self.component = component

class StateError(GameError):
    """Erro relacionado ao gerenciamento de estados do jogo"""
    def __init__(self, current_state, attempted_action, details=None):
        message = f"Ação inválida '{attempted_action}' no estado '{current_state}'"
        super().__init__(message, details)
        self.current_state = current_state
        self.attempted_action = attempted_action

class ConfigError(GameError):
    """Erro relacionado à configuração do jogo"""
    def __init__(self, config_key, details=None):
        message = f"Erro de configuração para: {config_key}"
        super().__init__(message, details)
        self.config_key = config_key

class ValidationError(GameError):
    """Erro de validação de dados"""
    def __init__(self, field, value, expected_type=None):
        message = f"Valor inválido para {field}: {value}"
        details = f"Tipo esperado: {expected_type}" if expected_type else None
        super().__init__(message, details)
        self.field = field
        self.value = value
        self.expected_type = expected_type

def safe_resource_load(load_func, resource_type, path, fallback=None):
    """
    Função segura para carregar recursos com tratamento de erro
    
    Args:
        load_func: Função de carregamento (ex: pygame.image.load)
        resource_type: Tipo do recurso (ex: "imagem", "som")
        path: Caminho do arquivo
        fallback: Valor de fallback se o carregamento falhar
    
    Returns:
        Recurso carregado ou fallback
    """
    try:
        if not os.path.exists(path):
            raise ResourceLoadError(resource_type, path, "Arquivo não encontrado")
        
        result = load_func(path)
        return result
        
    except Exception as e:
        log_error(f"Falha ao carregar {resource_type} '{path}': {e}")
        
        if fallback is not None:
            log_error(f"Usando fallback para {resource_type}")
            return fallback
        
        raise ResourceLoadError(resource_type, path, str(e))

def safe_pygame_operation(operation_func, operation_name, *args, **kwargs):
    """
    Executa operações do pygame com tratamento de erro seguro
    
    Args:
        operation_func: Função do pygame a ser executada
        operation_name: Nome da operação para logging
        *args, **kwargs: Argumentos para a função
    
    Returns:
        Resultado da operação ou None se falhar
    """
    try:
        return operation_func(*args, **kwargs)
    except pygame.error as e:
        log_error(f"Erro do pygame durante {operation_name}: {e}")
        return None
    except Exception as e:
        log_error(f"Erro inesperado durante {operation_name}: {e}")
        return None

def validate_game_state(current_state, valid_states):
    """
    Valida se o estado atual é válido
    
    Args:
        current_state: Estado atual do jogo
        valid_states: Lista de estados válidos
    
    Raises:
        StateError: Se o estado for inválido
    """
    if current_state not in valid_states:
        raise StateError(current_state, "validação", f"Estados válidos: {valid_states}")

def handle_critical_error(error, context=""):
    """
    Trata erros críticos que podem causar crash do jogo
    
    Args:
        error: Exceção que ocorreu
        context: Contexto adicional do erro
    """
    log_critical(f"ERRO CRÍTICO: {error}")
    if context:
        log_critical(f"Contexto: {context}")
    
    # Aqui você pode adicionar lógica para salvar estado do jogo
    # ou mostrar tela de erro para o usuário
    
    # Por enquanto, apenas registra o erro
    return False

def create_error_surface(error_message, screen_size):
    """
    Cria uma superfície com mensagem de erro para exibir ao usuário
    
    Args:
        error_message: Mensagem de erro
        screen_size: Tamanho da tela (width, height)
    
    Returns:
        pygame.Surface com a mensagem de erro
    """
    try:
        surface = pygame.Surface(screen_size)
        surface.fill((50, 0, 0))  # Fundo vermelho escuro
        
        font = pygame.font.SysFont('Arial', 24)
        
        # Título
        title = font.render("ERRO DO JOGO", True, (255, 255, 255))
        title_rect = title.get_rect(center=(screen_size[0]//2, 100))
        surface.blit(title, title_rect)
        
        # Mensagem de erro
        lines = error_message.split('\n')
        y_offset = 150
        for line in lines:
            if line.strip():
                text = font.render(line, True, (255, 200, 200))
                text_rect = text.get_rect(center=(screen_size[0]//2, y_offset))
                surface.blit(text, text_rect)
                y_offset += 30
        
        # Instruções
        instructions = [
            "Pressione ESC para sair",
            "Verifique o arquivo de log para mais detalhes"
        ]
        
        y_offset += 50
        for instruction in instructions:
            text = font.render(instruction, True, (200, 200, 255))
            text_rect = text.get_rect(center=(screen_size[0]//2, y_offset))
            surface.blit(text, text_rect)
            y_offset += 30
        
        return surface
        
    except Exception as e:
        # Se falhar ao criar a superfície de erro, retorna uma superfície simples
        surface = pygame.Surface(screen_size)
        surface.fill((255, 0, 0))
        return surface 