"""
Sistema de Analytics para o jogo Desprogramados
Coleta métricas de gameplay para análise e melhorias
"""

import json
import time
import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from logger import log_info, log_debug, log_error
from config import GameConfig

class GameAnalytics:
    """Sistema de analytics para coletar métricas do jogo"""
    
    def __init__(self):
        self.enabled = GameConfig.ANALYTICS_CONFIG['enabled']
        self.save_interval = GameConfig.ANALYTICS_CONFIG['save_interval']
        self.metrics_file = GameConfig.ANALYTICS_CONFIG['metrics_file']
        
        # Métricas em tempo real
        self.session_start = time.time()
        self.current_session = {
            'start_time': datetime.now().isoformat(),
            'play_time': 0,
            'levels_completed': 0,
            'deaths': 0,
            'paint_actions': 0,
            'jumps': 0,
            'player_actions': defaultdict(int),
            'level_times': {},
            'errors': 0,
            'performance_metrics': []
        }
        
        # Contadores por jogador
        self.player_stats = {
            'Jackson': defaultdict(int),
            'Jean': defaultdict(int)
        }
        
        # Métricas de performance
        self.frame_times = []
        self.last_save_time = time.time()
        
        # Carregar dados históricos se existirem
        self.historical_data = self._load_historical_data()
        
        log_info("Sistema de Analytics inicializado")
    
    def _load_historical_data(self):
        """Carrega dados históricos de analytics"""
        try:
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    log_debug(f"Analytics históricos carregados: {len(data.get('sessions', []))} sessões")
                    return data
        except Exception as e:
            log_error(f"Erro ao carregar analytics históricos: {e}")
        
        return {'sessions': [], 'total_stats': {}}
    
    def _save_data(self):
        """Salva dados de analytics no arquivo"""
        try:
            # Finalizar sessão atual
            self.current_session['end_time'] = datetime.now().isoformat()
            self.current_session['duration'] = time.time() - self.session_start
            
            # Adicionar à lista de sessões
            self.historical_data['sessions'].append(self.current_session)
            
            # Manter apenas as últimas 100 sessões
            if len(self.historical_data['sessions']) > 100:
                self.historical_data['sessions'] = self.historical_data['sessions'][-100:]
            
            # Calcular estatísticas totais
            self._calculate_total_stats()
            
            # Salvar no arquivo
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(self.historical_data, f, indent=2, ensure_ascii=False)
            
            log_debug("Dados de analytics salvos")
            
        except Exception as e:
            log_error(f"Erro ao salvar analytics: {e}")
    
    def _calculate_total_stats(self):
        """Calcula estatísticas totais de todas as sessões"""
        total_stats = {
            'total_sessions': len(self.historical_data['sessions']),
            'total_play_time': 0,
            'total_levels_completed': 0,
            'total_deaths': 0,
            'total_paint_actions': 0,
            'total_jumps': 0,
            'average_session_duration': 0,
            'most_played_level': None,
            'player_preferences': defaultdict(int)
        }
        
        level_completions = Counter()
        
        for session in self.historical_data['sessions']:
            total_stats['total_play_time'] += session.get('play_time', 0)
            total_stats['total_levels_completed'] += session.get('levels_completed', 0)
            total_stats['total_deaths'] += session.get('deaths', 0)
            total_stats['total_paint_actions'] += session.get('paint_actions', 0)
            total_stats['total_jumps'] += session.get('jumps', 0)
            
            # Contar níveis completados
            for level, time_taken in session.get('level_times', {}).items():
                level_completions[level] += 1
            
            # Contar ações dos jogadores
            for player, actions in session.get('player_actions', {}).items():
                total_stats['player_preferences'][player] += actions
        
        # Calcular médias
        if total_stats['total_sessions'] > 0:
            total_stats['average_session_duration'] = total_stats['total_play_time'] / total_stats['total_sessions']
        
        # Nível mais jogado
        if level_completions:
            total_stats['most_played_level'] = level_completions.most_common(1)[0][0]
        
        self.historical_data['total_stats'] = total_stats
    
    def track_event(self, event_type, data=None):
        """Registra um evento do jogo"""
        if not self.enabled:
            return
        
        timestamp = time.time()
        
        if event_type == 'level_completed':
            level_name = data.get('level', 'unknown')
            time_taken = data.get('time', 0)
            self.current_session['levels_completed'] += 1
            self.current_session['level_times'][level_name] = time_taken
            log_debug(f"Level completado: {level_name} em {time_taken:.2f}s")
            
        elif event_type == 'player_action':
            player_name = data.get('player', 'unknown')
            action = data.get('action', 'unknown')
            self.current_session['player_actions'][player_name] += 1
            self.player_stats[player_name][action] += 1
            
            if action == 'jump':
                self.current_session['jumps'] += 1
            elif action == 'paint':
                self.current_session['paint_actions'] += 1
                
        elif event_type == 'death':
            self.current_session['deaths'] += 1
            log_debug(f"Morte registrada - Total: {self.current_session['deaths']}")
            
        elif event_type == 'error':
            self.current_session['errors'] += 1
            log_debug(f"Erro registrado: {data}")
            
        elif event_type == 'performance':
            frame_time = data.get('frame_time', 0)
            self.current_session['performance_metrics'].append({
                'timestamp': timestamp,
                'frame_time': frame_time
            })
            
            # Manter apenas os últimos 1000 registros de performance
            if len(self.current_session['performance_metrics']) > 1000:
                self.current_session['performance_metrics'] = self.current_session['performance_metrics'][-1000:]
    
    def update_play_time(self, delta_time):
        """Atualiza o tempo de jogo"""
        if self.enabled:
            self.current_session['play_time'] += delta_time
            
            # Salvar dados periodicamente
            current_time = time.time()
            if current_time - self.last_save_time > self.save_interval:
                self._save_data()
                self.last_save_time = current_time
    
    def track_frame_time(self, frame_time):
        """Registra tempo de frame para análise de performance"""
        if self.enabled:
            self.track_event('performance', {'frame_time': frame_time})
    
    def get_session_summary(self):
        """Retorna resumo da sessão atual"""
        return {
            'duration': time.time() - self.session_start,
            'play_time': self.current_session['play_time'],
            'levels_completed': self.current_session['levels_completed'],
            'deaths': self.current_session['deaths'],
            'paint_actions': self.current_session['paint_actions'],
            'jumps': self.current_session['jumps'],
            'errors': self.current_session['errors']
        }
    
    def get_player_stats(self, player_name):
        """Retorna estatísticas de um jogador específico"""
        if player_name in self.player_stats:
            return dict(self.player_stats[player_name])
        return {}
    
    def get_performance_metrics(self):
        """Retorna métricas de performance da sessão atual"""
        metrics = self.current_session['performance_metrics']
        if not metrics:
            return {}
        
        frame_times = [m['frame_time'] for m in metrics]
        return {
            'avg_frame_time': sum(frame_times) / len(frame_times),
            'min_frame_time': min(frame_times),
            'max_frame_time': max(frame_times),
            'fps_avg': 1000 / (sum(frame_times) / len(frame_times)) if frame_times else 0,
            'total_frames': len(frame_times)
        }
    
    def generate_report(self):
        """Gera relatório completo de analytics"""
        current_summary = self.get_session_summary()
        performance = self.get_performance_metrics()
        
        report = {
            'session_summary': current_summary,
            'performance': performance,
            'player_stats': {player: dict(stats) for player, stats in self.player_stats.items()},
            'historical_data': self.historical_data.get('total_stats', {})
        }
        
        return report
    
    def save_and_reset(self):
        """Salva dados atuais e reseta para nova sessão"""
        if self.enabled:
            self._save_data()
            
            # Reset para nova sessão
            self.session_start = time.time()
            self.current_session = {
                'start_time': datetime.now().isoformat(),
                'play_time': 0,
                'levels_completed': 0,
                'deaths': 0,
                'paint_actions': 0,
                'jumps': 0,
                'player_actions': defaultdict(int),
                'level_times': {},
                'errors': 0,
                'performance_metrics': []
            }
            
            self.player_stats = {
                'Jackson': defaultdict(int),
                'Jean': defaultdict(int)
            }
            
            log_info("Analytics resetados para nova sessão")

# Instância global do analytics
game_analytics = GameAnalytics()

# Funções de conveniência
def track_event(event_type, data=None):
    game_analytics.track_event(event_type, data)

def track_level_completed(level_name, time_taken):
    game_analytics.track_event('level_completed', {'level': level_name, 'time': time_taken})

def track_player_action(player_name, action):
    game_analytics.track_event('player_action', {'player': player_name, 'action': action})

def track_death():
    game_analytics.track_event('death')

def track_error(error_message):
    game_analytics.track_event('error', {'message': error_message})

def track_frame_time(frame_time):
    game_analytics.track_frame_time(frame_time)

def get_analytics_report():
    return game_analytics.generate_report() 