"""
Sistema de logging estruturado para o jogo Desprogramados
Substitui os print() statements por logging profissional
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from config import GameConfig

class GameLogger:
    """Sistema de logging centralizado para o jogo"""
    
    def __init__(self, name="Desprogramados"):
        self.name = name
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """Configura o logger com handlers para arquivo e console"""
        logger = logging.getLogger(self.name)
        logger.setLevel(getattr(logging, GameConfig.LOG_CONFIG['level']))
        
        # Evitar duplicação de handlers
        if logger.handlers:
            return logger
            
        # Formatter
        formatter = logging.Formatter(GameConfig.LOG_CONFIG['format'])
        
        # Handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Handler para arquivo com rotação
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join('logs', GameConfig.LOG_CONFIG['file']),
            maxBytes=GameConfig.LOG_CONFIG['max_size'],
            backupCount=GameConfig.LOG_CONFIG['backup_count']
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def info(self, message):
        """Log de informação geral"""
        self.logger.info(message)
    
    def debug(self, message):
        """Log de debug"""
        self.logger.debug(message)
    
    def warning(self, message):
        """Log de aviso"""
        self.logger.warning(message)
    
    def error(self, message):
        """Log de erro"""
        self.logger.error(message)
    
    def critical(self, message):
        """Log de erro crítico"""
        self.logger.critical(message)
    
    def game_event(self, event_type, data=None):
        """Log específico para eventos do jogo"""
        message = f"GAME_EVENT: {event_type}"
        if data:
            message += f" - {data}"
        self.logger.info(message)
    
    def performance(self, operation, duration):
        """Log de performance"""
        self.logger.debug(f"PERFORMANCE: {operation} took {duration:.3f}ms")
    
    def player_action(self, player_name, action, position=None):
        """Log de ações dos jogadores"""
        message = f"PLAYER_ACTION: {player_name} - {action}"
        if position:
            message += f" at ({position[0]:.1f}, {position[1]:.1f})"
        self.logger.debug(message)

# Instância global do logger
game_logger = GameLogger()

# Funções de conveniência para uso direto
def log_info(message):
    game_logger.info(message)

def log_debug(message):
    game_logger.debug(message)

def log_warning(message):
    game_logger.warning(message)

def log_error(message):
    game_logger.error(message)

def log_critical(message):
    game_logger.critical(message)

def log_game_event(event_type, data=None):
    game_logger.game_event(event_type, data)

def log_performance(operation, duration):
    game_logger.performance(operation, duration)

def log_player_action(player_name, action, position=None):
    game_logger.player_action(player_name, action, position) 