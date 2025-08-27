# Sistema de Música - Desprogramados

## Visão Geral

O jogo agora possui um sistema de música integrado que toca diferentes trilhas sonoras para cada estado do jogo (menu, fases, etc.).

## Estrutura de Arquivos

```
Desprogramados 22-07/
├── music/                    # Pasta para arquivos de música
│   ├── menu_theme.ogg       # Música do menu principal
│   ├── paint_creative.ogg   # Música da fase de pintura
│   ├── platform_action.ogg  # Música da fase de plataforma
│   └── intro_theme.ogg      # Música da introdução
├── main.py                  # Arquivo principal com sistema de música
└── music_manager.py         # Gerenciador de música (opcional/avançado)
```

## Formatos de Áudio Suportados

O pygame suporta os seguintes formatos:
- **.ogg** (recomendado - melhor compressão e qualidade)
- **.mp3** (amplamente suportado)
- **.wav** (sem compressão, arquivos maiores)

## Como Adicionar Música

### 1. Preparar os Arquivos de Música

Coloque seus arquivos de música na pasta `music/` com os seguintes nomes:

- `menu_theme.ogg` - Música ambiente para o menu principal
- `paint_creative.ogg` - Música relaxante para a fase de pintura
- `platform_action.ogg` - Música energética para a fase de plataforma
- `intro_theme.ogg` - Música para a tela de introdução

### 2. Características Recomendadas

**Menu Principal:**
- Música ambiente, relaxante
- Loop suave (sem cortes abruptos)
- Volume moderado
- Duração: 2-4 minutos

**Fase de Pintura:**
- Música criativa e inspiradora
- Ritmo calmo
- Pode ter elementos eletrônicos suaves
- Duração: 3-5 minutos

**Fase de Plataforma:**
- Música mais energética
- Ritmo dinâmico
- Pode ter elementos de aventura
- Duração: 2-4 minutos

**Introdução:**
- Música épica ou misteriosa
- Pode ter build-up
- Duração: 1-2 minutos

## Controles de Música

Durante o jogo, você pode usar as seguintes teclas:

- **M** - Pausar/Despausar música
- **+** ou **=** - Aumentar volume
- **-** - Diminuir volume
- **ESC** - Sair do jogo

## Configurações Técnicas

### Volume Padrão
- Volume inicial: 70%
- Range: 0% a 100%
- Incremento: 10% por tecla pressionada

### Transições
- Fade out: 1 segundo ao trocar de música
- Fade in: Automático ao carregar nova música
- Loop: Todas as músicas tocam em loop infinito

## Solução de Problemas

### Música não toca
1. Verifique se o arquivo existe na pasta `music/`
2. Confirme se o formato é suportado (.ogg, .mp3, .wav)
3. Verifique se o arquivo não está corrompido
4. Observe as mensagens no console para erros

### Música corta ou falha
1. Verifique se o arquivo tem loop suave
2. Confirme se o arquivo não está muito grande (recomendado < 10MB)
3. Teste com formato .ogg se estiver usando .mp3

### Performance
- Arquivos .ogg são recomendados para melhor performance
- Evite arquivos muito grandes (> 20MB)
- Taxa de amostragem recomendada: 44.1kHz ou 22.05kHz

## Personalização Avançada

### Adicionando Mais Músicas

Para adicionar mais variações, edite o arquivo `main.py` na classe `SimpleMusicManager`:

```python
music_files = {
    'menu': ['music/menu_theme.ogg', 'music/menu_ambient.ogg'],  # Lista de músicas
    'paint': ['music/paint_creative.ogg', 'music/paint_focus.ogg'],
    'plataforma': ['music/platform_action.ogg', 'music/platform_adventure.ogg'],
    'begin': ['music/intro_theme.ogg']
}
```

### Efeitos Sonoros

Para adicionar efeitos sonoros (SFX), você pode usar:

```python
# Carregar som
sound_effect = pygame.mixer.Sound('sounds/jump.ogg')
# Tocar som
sound_effect.play()
```

## Recursos Externos

### Onde Encontrar Música Livre

- **Freesound.org** - Efeitos sonoros e música
- **OpenGameArt.org** - Recursos para jogos
- **Zapsplat.com** - Biblioteca de áudio (requer cadastro)
- **YouTube Audio Library** - Música livre de direitos

### Ferramentas de Edição

- **Audacity** (gratuito) - Editor de áudio básico
- **LMMS** (gratuito) - Criação de música
- **FL Studio** (pago) - Produção musical profissional

## Licenças

Certifique-se de que toda música utilizada:
- Seja de sua autoria
- Tenha licença Creative Commons apropriada
- Seja livre de direitos autorais
- Tenha permissão para uso comercial (se aplicável)

---

**Nota:** O sistema de música está configurado para funcionar mesmo sem arquivos de música. Se os arquivos não forem encontrados, o jogo continuará funcionando normalmente, apenas sem som.
