import requests
from bs4 import BeautifulSoup
import json
import time
import re
import random
from urllib.parse import quote

def buscar_imagem_google(titulo):
    """Busca a primeira imagem real no Google Imagens usando o título como query"""
    if not titulo:
        return ""
    
    # Limitar tamanho da consulta e remover caracteres especiais
    query = titulo[:80].strip()
    query = re.sub(r'[^\w\s]', '', query)
    
    # Construir URL de pesquisa do Google Imagens
    search_url = f"https://www.google.com/search?tbm=isch&q={quote(query)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-PT,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Procurar por imagens nos resultados
        # Google Images usa divs com classe "rg_i" ou "YQ4gaf"
        imagens = soup.find_all('img', class_=re.compile(r'rg_i|YQ4gaf'))
        
        for img in imagens:
            src = img.get('src', '')
            if src and src.startswith('http') and 'gstatic' not in src and 'google' not in src:
                # Limpar URL (remover parâmetros extras)
                src_limpa = src.split('&')[0]
                if src_limpa.endswith('.jpg') or src_limpa.endswith('.png') or src_limpa.endswith('.jpeg') or src_limpa.endswith('.webp'):
                    return src_limpa
        
        # Fallback: procurar por data-src
        for img in soup.find_all('img', attrs={'data-src': re.compile(r'^http')}):
            src = img.get('data-src', '')
            if src and 'gstatic' not in src and 'google' not in src:
                return src.split('&')[0]
        
        return ""
        
    except Exception as e:
        print(f"     ⚠️ Erro na busca: {e}")
        return ""

def atualizar_imagens_por_titulo_google():
    """Lê o JSON e busca imagens reais no Google Imagens para cada notícia"""
    
    with open('dados.json', 'r', encoding='utf-8') as f:
        noticias = json.load(f)
    
    print(f"📰 Total de notícias: {len(noticias)}")
    print("="*60)
    print("🔍 A buscar imagens no Google Imagens para cada título...")
    print("="*60)
    
    atualizadas = 0
    ja_tem_imagem_real = 0
    
    for i, noticia in enumerate(noticias):
        titulo = noticia.get('titulo', '')
        img_atual = noticia.get('img', '')
        
        # Se já tem imagem real (não é do Unsplash nem padrão)
        if img_atual and 'unsplash' not in img_atual and 'picsum' not in img_atual and 'images.unsplash' not in img_atual:
            print(f"\n{i+1}. ✅ Já tem imagem real: {titulo[:40]}...")
            ja_tem_imagem_real += 1
            continue
        
        print(f"\n{i+1}. 🔍 Buscando no Google: {titulo[:50]}...")
        
        imagem = buscar_imagem_google(titulo)
        
        if imagem:
            noticia['img'] = imagem
            atualizadas += 1
            print(f"     ✅ Imagem encontrada: {imagem[:80]}...")
        else:
            print(f"     ❌ Nenhuma imagem encontrada para este título")
        
        # Pausa para não sobrecarregar o Google
        time.sleep(random.uniform(1, 3))
    
    # Salvar JSON atualizado
    with open('dados.json', 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print(f"📊 RESUMO:")
    print(f"   ✅ Notícias que já tinham imagem real: {ja_tem_imagem_real}")
    print(f"   📸 Notícias atualizadas com imagem do Google: {atualizadas}")
    print(f"   📰 Total de notícias: {len(noticias)}")
    print("="*60)

if __name__ == "__main__":
    atualizar_imagens_por_titulo_google()
