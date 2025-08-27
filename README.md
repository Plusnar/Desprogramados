# Desprogramados

Projeto de melhorias para o jogo Desprogramados, focado em arquitetura profissional, performance, monitoramento e experiência do usuário. Inclui sistemas avançados de logging, analytics, tratamento de erros, configurações centralizadas, otimizações e gerenciamento de música.

## Visão Geral

Este repositório traz uma base modular para jogos em Python usando Pygame, com foco em:
- Logging estruturado
- Analytics persistente
- Tratamento robusto de erros
- Configurações centralizadas
- Otimizações de performance
- Gerenciamento de música

## Estrutura de Arquivos
```
├── main.py                # Arquivo principal do jogo
├── config.py              # Configurações centralizadas
├── logger.py              # Sistema de logging
├── exceptions.py          # Tratamento de erros
├── analytics.py           # Sistema de analytics
├── optimizations.py       # Otimizações de performance
├── music_manager.py       # Gerenciador de música
├── example_usage.py       # Exemplos de uso dos sistemas
├── assets/                # Imagens, fontes, etc
├── music/                 # Arquivos de música
├── logs/                  # Logs do jogo
├── minigames/             # Minigames (paint, plataforma)
```

## Sistemas Implementados
- **Configurações Centralizadas:** Todas as constantes e parâmetros do jogo em um só lugar.
- **Logging Estruturado:** Logs em arquivo e console, rotação automática, níveis INFO/DEBUG/ERROR.
- **Tratamento de Erros:** Exceções customizadas, fallback de recursos, tela de erro.
- **Analytics:** Tracking de eventos, métricas por jogador, relatórios automáticos.
- **Otimizações:** Cache de texturas/sons, pool de objetos, monitor de performance.
- **Gerenciamento de Música:** Trilha sonora dinâmica por estado do jogo, fácil personalização.

## Como Usar
1. Instale as dependências:
   ```bash
   pip install pygame
   ```
2. Execute o jogo:
   ```bash
   python main.py
   ```
3. Teste os sistemas:
   ```bash
   python example_usage.py
   ```

## Requisitos
- Python 3.7+
- Pygame 2.0+
- Compatível com Windows, macOS, Linux

## Métricas e Monitoramento
- Logs em `logs/game.log`
- Analytics em `analytics.json`
- Métricas de performance: FPS, uso de memória, cache

## Personalização
- Adicione músicas na pasta `music/` (formatos .ogg, .mp3, .wav)
- Configure parâmetros em `config.py`
- Consulte exemplos em `example_usage.py`

## Contribuição
- Use os sistemas implementados
- Adicione logs e tratamento de erros
- Documente mudanças
- Teste performance

## Licença
Consulte as licenças dos arquivos de música utilizados. Recomenda-se uso de músicas livres de direitos ou Creative Commons.

---
**Autor:** Plusnar (William Fagundes)
**Versão:** 1.0
**Ano:** 2025
