import os
from PIL import Image

ASSETS_DIR = 'assets'

for filename in os.listdir(ASSETS_DIR):
    if filename.lower().endswith('.png'):
        path = os.path.join(ASSETS_DIR, filename)
        try:
            img = Image.open(path)
            img.save(path)
            print(f'Limpo: {filename}')
        except Exception as e:
            print(f'Erro ao processar {filename}: {e}') 