import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin

def extrair_imagem_real(url_artigo):
    """Extrai a imagem real da página do artigo"""
    if not url_artigo or url_artigo == '#':
        return ""
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-PT,pt;q=0.9,en;q=0.8',
        }
        
        response = requests.get(url_artigo, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. og:image (meta tag do Facebook - mais confiável)
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            img = og_image['content']
            if img.startswith('http'):
                return img
        
        # 2. twitter:image
        twitter_image = soup.find('meta', name='twitter:image')
        if twitter_image and twitter_image.get('content'):
            img = twitter_image['content']
            if img.startswith('http'):
                return img
        
        # 3. Primeira imagem grande do artigo
        imagens = soup.find_all('img')
        for img in imagens:
            src = img.get('src', '')
            if src and 'logo' not in src.lower() and 'icon' not in src.lower() and 'avatar' not in src.lower():
                if src.startswith('http'):
                    # Ignorar imagens muito pequenas (prováveis ícones)
                    if '100x100' not in src and '50x50' not in src and 'thumbnail' not in src.lower():
                        return src
                elif src.startswith('/'):
                    return urljoin(url_artigo, src)
        
        return ""
        
    except Exception as e:
        print(f"     ⚠️ Erro: {str(e)[:50]}")
        return ""

def atualizar_imagens():
    """Lê o JSON, busca imagens reais e atualiza"""
    
    with open('dados.json', 'r', encoding='utf-8') as f:
        noticias = json.load(f)
    
    print(f"📰 Total de notícias: {len(noticias)}")
    print("="*60)
    
    atualizadas = 0
    for i, noticia in enumerate(noticias):
        link = noticia.get('link_real', '')
        
        # Verificar se já tem imagem real (não é do Unsplash)
        img_atual = noticia.get('img', '')
        if img_atual and 'unsplash' not in img_atual and 'picsum' not in img_atual:
            print(f"\n{i+1}. ✅ Já tem imagem real: {noticia['titulo'][:40]}...")
            continue
        
        if not link or link == '#':
            print(f"\n{i+1}. ⚠️ Sem link_real: {noticia['titulo'][:40]}...")
            continue
        
        print(f"\n{i+1}. 🔍 Buscando: {noticia['titulo'][:40]}...")
        print(f"     Link: {link[:60]}...")
        
        imagem_real = extrair_imagem_real(link)
        
        if imagem_real:
            noticia['img'] = imagem_real
            atualizadas += 1
            print(f"     ✅ Imagem encontrada: {imagem_real[:80]}...")
        else:
            print(f"     ❌ Nenhuma imagem encontrada, mantém a atual")
        
        time.sleep(0.5)  # Pausa para não sobrecarregar
    
    # Salvar JSON atualizado
    with open('dados.json', 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print(f"✅ Total de notícias atualizadas com imagem real: {atualizadas}/{len(noticias)}")
    print(f"📁 Arquivo atualizado: dados.json")

if __name__ == "__main__":
    atualizar_imagens()
