import requests
import json
import time
import re
import random
from urllib.parse import quote

def buscar_imagem_duckduckgo(titulo):
    """Busca a primeira imagem real no DuckDuckGo Imagens"""
    if not titulo:
        return ""
    
    query = titulo[:70].strip()
    query = re.sub(r'[^\w\s]', '', query)
    
    # DuckDuckGo Image Search API (não oficial mas funcional)
    url = f"https://duckduckgo.com/i.js?o=json&q={quote(query)}&vqd=3&l=wt-wt&p=1"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://duckduckgo.com/',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results') and len(data['results']) > 0:
                # Pega a primeira imagem
                img_url = data['results'][0].get('image')
                if img_url and img_url.startswith('http'):
                    return img_url
        
        # Fallback: busca HTML
        return buscar_imagem_duckduckgo_html(titulo)
        
    except Exception as e:
        print(f"     ⚠️ Erro: {e}")
        return ""

def buscar_imagem_duckduckgo_html(titulo):
    """Fallback: busca imagem via HTML do DuckDuckGo"""
    from bs4 import BeautifulSoup
    
    query = titulo[:70].strip()
    url = f"https://duckduckgo.com/?q={quote(query)}&iax=images&ia=images"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Procurar por imagens nos resultados
        for img in soup.find_all('img', src=True):
            src = img.get('src', '')
            if src and src.startswith('http') and 'duckduckgo' not in src and 'logo' not in src.lower():
                if src.endswith('.jpg') or src.endswith('.png') or src.endswith('.jpeg') or src.endswith('.webp'):
                    return src
        return ""
    except:
        return ""

def buscar_imagem_bing(titulo):
    """Busca imagem no Bing (alternativa)"""
    query = titulo[:70].strip()
    url = f"https://www.bing.com/images/search?q={quote(query)}&first=1"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        # Procurar por padrão de imagem no HTML
        padrao = r'https?://[^"\']+\.(jpg|jpeg|png|webp)[^"\']*'
        imagens = re.findall(padrao, response.text, re.I)
        
        for img in imagens:
            if isinstance(img, tuple):
                img = img[0]
            if img and 'gif' not in img and 'logo' not in img.lower():
                return img
        return ""
    except:
        return ""

def atualizar_imagens():
    with open('dados.json', 'r', encoding='utf-8') as f:
        noticias = json.load(f)
    
    print(f"📰 Total de notícias: {len(noticias)}")
    print("="*60)
    print("🔍 A buscar imagens no DuckDuckGo e Bing...")
    print("="*60)
    
    atualizadas = 0
    ja_tem = 0
    
    for i, noticia in enumerate(noticias):
        titulo = noticia.get('titulo', '')
        img_atual = noticia.get('img', '')
        
        # Se já tem imagem real (não é placeholder)
        if img_atual and 'unsplash' not in img_atual and 'picsum' not in img_atual and 'placeholder' not in img_atual:
            print(f"\n{i+1}. ✅ Já tem imagem: {titulo[:40]}...")
            ja_tem += 1
            continue
        
        print(f"\n{i+1}. 🔍 Buscando: {titulo[:50]}...")
        
        # Tentar DuckDuckGo primeiro
        imagem = buscar_imagem_duckduckgo(titulo)
        
        # Se não encontrar, tentar Bing
        if not imagem:
            imagem = buscar_imagem_bing(titulo)
        
        if imagem:
            noticia['img'] = imagem
            atualizadas += 1
            print(f"     ✅ Imagem: {imagem[:80]}...")
        else:
            print(f"     ❌ Nenhuma imagem encontrada")
        
        time.sleep(random.uniform(1, 2))
    
    with open('dados.json', 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print(f"📊 RESUMO:")
    print(f"   ✅ Já tinham imagem real: {ja_tem}")
    print(f"   📸 Novas imagens encontradas: {atualizadas}")
    print(f"   📰 Total: {len(noticias)}")
    print("="*60)

if __name__ == "__main__":
    atualizar_imagens()
