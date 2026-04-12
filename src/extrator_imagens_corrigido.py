import requests
from bs4 import BeautifulSoup
import json
import re
import time
from urllib.parse import urljoin
import ssl
import urllib3

# Desativar avisos de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def extrair_imagem_real(url_artigo):
    """Extrai a imagem real da página do artigo - VERSÃO CORRIGIDA"""
    try:
        # Ignorar verificação SSL para sites problemáticos
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-PT,pt;q=0.9,en;q=0.8',
        }
        
        # Tentar com verificação SSL desativada
        response = requests.get(url_artigo, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Tentar og:image (meta tag do Facebook)
        og_image = soup.find('meta', attrs={'property': 'og:image'})
        if og_image and og_image.get('content'):
            img = og_image['content']
            if img.startswith('http'):
                return img
        
        # 2. Tentar twitter:image
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            img = twitter_image['content']
            if img.startswith('http'):
                return img
        
        # 3. Tentar primeira imagem grande do artigo
        imagens = soup.find_all('img')
        for img in imagens:
            src = img.get('src', '')
            if src and 'logo' not in src.lower() and 'icon' not in src.lower() and 'avatar' not in src.lower():
                if src.startswith('http'):
                    return src
                elif src.startswith('/'):
                    return urljoin(url_artigo, src)
        
        return ""
        
    except requests.exceptions.SSLError:
        print(f"     ⚠️ Erro SSL (ignorado)")
        return ""
    except requests.exceptions.ConnectionError:
        print(f"     ⚠️ Erro de conexão")
        return ""
    except Exception as e:
        print(f"     ⚠️ Erro: {str(e)[:50]}")
        return ""

def atualizar_imagens_reais(arquivo_json):
    """Lê o JSON, extrai imagens reais de cada link_real e atualiza"""
    
    with open(arquivo_json, 'r', encoding='utf-8') as f:
        noticias = json.load(f)
    
    print(f"📰 Total de notícias: {len(noticias)}")
    print("="*50)
    
    for i, noticia in enumerate(noticias):
        print(f"\n{i+1}. {noticia['titulo'][:50]}...")
        
        link = noticia.get('link_real', '')
        if not link or link == '#':
            print(f"   ⚠️ Sem link_real, ignorando")
            continue
        
        print(f"   🔍 A extrair imagem de: {link[:60]}...")
        imagem_real = extrair_imagem_real(link)
        
        if imagem_real:
            noticia['img'] = imagem_real
            print(f"   ✅ Imagem encontrada: {imagem_real[:80]}...")
        else:
            print(f"   ❌ Nenhuma imagem encontrada, mantém a atual")
        
        time.sleep(0.5)  # Pausa pequena
    
    # Salvar JSON atualizado
    with open(arquivo_json, 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*50)
    com_imagem = len([n for n in noticias if n['img'] and 'unsplash' not in n['img']])
    print(f"✅ Notícias com imagem real: {com_imagem}/{len(noticias)}")
    print(f"📁 Arquivo atualizado: {arquivo_json}")

if __name__ == "__main__":
    import os
    arquivo = 'noticias_com_links.json'
    
    if os.path.exists(arquivo):
        atualizar_imagens_reais(arquivo)
    else:
        print(f"❌ Arquivo {arquivo} não encontrado!")
        print("Crie o arquivo com as notícias e execute novamente.")
