import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime

def extrair_detalhes_artigo(url_artigo):
    """Extrai título (h1) e descrição (primeiro p) da página do artigo"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url_artigo, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extrair título real (h1)
        titulo_real = ""
        h1 = soup.find('h1')
        if h1:
            titulo_real = h1.get_text(strip=True)
        
        # Extrair descrição real (primeiro parágrafo com mais de 30 caracteres)
        descricao_real = ""
        for p in soup.find_all('p'):
            texto = p.get_text(strip=True)
            if len(texto) > 50 and 'Instalar' not in texto and 'APP' not in texto and 'Cookie' not in texto:
                descricao_real = texto[:350]
                break
        
        return titulo_real, descricao_real
    except Exception as e:
        print(f"     ⚠️ Erro ao aceder {url_artigo}: {e}")
        return "", ""

def extrair_miramar():
    noticias = []
    url = "https://miramar.co.mz/miramar-news"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        links_com_imagem = soup.find_all('a', href=True)
        
        total_processados = 0
        for link in links_com_imagem:
            try:
                img = link.find('img')
                if not img:
                    continue
                
                src = img.get('src', '')
                if 'wp-content/uploads' not in src:
                    continue
                if 'logo' in src.lower() or 'miramar_' in src.lower():
                    continue
                
                src_limpa = re.sub(r'\?.*$', '', src)
                
                # Link do artigo
                artigo_link = link.get('href', '')
                if artigo_link and not artigo_link.startswith('http'):
                    artigo_link = "https://miramar.co.mz" + artigo_link
                
                if not artigo_link or 'miramar.co.mz' not in artigo_link:
                    continue
                
                # Extrair título e descrição da página do artigo
                print(f"  🔍 A processar: {artigo_link.split('/')[-2] if artigo_link.split('/') else '...'}...")
                titulo_real, descricao_real = extrair_detalhes_artigo(artigo_link)
                time.sleep(0.3)  # Pausa para não sobrecarregar
                
                # Usar título real ou fallback
                if titulo_real:
                    titulo = titulo_real[:150]
                else:
                    # Fallback: tentar extrair do link
                    titulo = link.get('title', '') or link.get_text(strip=True)
                    if not titulo or len(titulo) < 10:
                        next_h = link.find_next(['h2', 'h3', 'h4'])
                        if next_h:
                            titulo = next_h.get_text(strip=True)
                    if not titulo or len(titulo) < 10:
                        titulo = "Miramar News"
                
                # Usar descrição real ou fallback
                desc = descricao_real if descricao_real else "Clique para ler a notícia completa"
                
                noticias.append({
                    "data": datetime.now().strftime("%d/%m/%Y"),
                    "titulo": titulo,
                    "desc": desc,
                    "img": src_limpa,
                    "video": "",
                    "tipo": "noticia",
                    "categoria": "Nacional",
                    "fonte": "Miramar News",
                    "link": artigo_link
                })
                total_processados += 1
                print(f"     ✅ {titulo[:50]}...")
                
            except Exception as e:
                continue
        
        print(f"\n📊 Total de notícias do Miramar processadas: {total_processados}")
        return noticias
        
    except Exception as e:
        print(f"❌ Erro ao aceder ao Miramar: {e}")
        return []

if __name__ == "__main__":
    noticias = extrair_miramar()
    with open('miramar_melhorado.json', 'w') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Salvo em miramar_melhorado.json")
