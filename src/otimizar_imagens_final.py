import requests
from bs4 import BeautifulSoup
import json
import re
import time
from urllib.parse import urljoin

# Mapeamento de categorias para imagens Unsplash de qualidade
IMAGENS_POR_CATEGORIA = {
    "Política": "https://images.unsplash.com/photo-1529101091764-c3526daf3e8a?q=80&w=600",
    "Economia": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?q=80&w=600",
    "Saúde": "https://images.unsplash.com/photo-1584515933487-779824d29309?q=80&w=600",
    "Educação": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?q=80&w=600",
    "Tecnologia": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?q=80&w=600",
    "Sociedade": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?q=80&w=600",
    "Internacional": "https://images.unsplash.com/photo-1529101091764-c3526daf3e8a?q=80&w=600",
    "Segurança": "https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=600",
    "Ambiente": "https://images.unsplash.com/photo-1509391366360-2e959784a276?q=80&w=600",
    "Cultura": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?q=80&w=600",
    "Desporto": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?q=80&w=600",
    "Emprego": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?q=80&w=600",
    "Conflito Internacional": "https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=600",
    "Gestão": "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?q=80&w=600",
    "Indústria": "https://images.unsplash.com/photo-1581091226033-d5c48150dbaa?q=80&w=600",
    "Engenharia": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?q=80&w=600",
    "Transportes": "https://images.unsplash.com/photo-1517524008697-84bbe3c3fd98?q=80&w=600",
    "Social": "https://images.unsplash.com/photo-1573497620053-e3a0e9f0a54a?q=80&w=600",
    "Vendas": "https://images.unsplash.com/photo-1554774853-aae0a22c8aa4?q=80&w=600",
    "Serviços": "https://images.unsplash.com/photo-1527515637462-cff94eecc1ac?q=80&w=600",
    "Agricultura": "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?q=80&w=600",
    "Finanças": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=600",
    "Pesquisa": "https://images.unsplash.com/photo-1573497620053-e3a0e9f0a54a?q=80&w=600",
    "Saúde e Segurança": "https://images.unsplash.com/photo-1573497620053-e3a0e9f0a54a?q=80&w=600",
    "Comercial": "https://images.unsplash.com/photo-1554774853-aae0a22c8aa4?q=80&w=600",
    "Recursos Humanos": "https://images.unsplash.com/photo-1521791136064-7986c2959210?q=80&w=600",
    "Starlink": "https://images.unsplash.com/photo-1621330396173-e41b1cafd17f?q=80&w=600",
    "Smartphones": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?q=80&w=600",
    "Internet": "https://images.unsplash.com/photo-1563986768609-322da13575f3?q=80&w=600",
    "Drones": "https://images.unsplash.com/photo-1508614589041-895b88991e69?q=80&w=600",
    "Computadores": "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?q=80&w=600",
    "Tablets": "https://images.unsplash.com/photo-1542751110-97427bbecf20?q=80&w=600",
    "Acessórios": "https://images.unsplash.com/photo-1609592424789-743c1f3ea4b0?q=80&w=600",
    "Áudio": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=600",
    "Corrupção": "https://images.unsplash.com/photo-1582213782179-e0d53f98f2ca?q=80&w=600",
    "Infraestrutura": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?q=80&w=600",
    "Média": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=600",
    "Direito": "https://images.unsplash.com/photo-1557804506-669a67965ba0?q=80&w=600",
}

IMAGEM_PADRAO = "https://images.unsplash.com/photo-1582213782179-e0d53f98f2ca?q=80&w=600"

def extrair_imagem_real(url_artigo):
    """Tenta extrair imagem real do link_real"""
    if not url_artigo or url_artigo == '#':
        return ""
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url_artigo, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # og:image
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            img = og_image['content']
            if img.startswith('http') and 'logo' not in img.lower():
                return img
        
        # twitter:image
        twitter_image = soup.find('meta', name='twitter:image')
        if twitter_image and twitter_image.get('content'):
            img = twitter_image['content']
            if img.startswith('http') and 'logo' not in img.lower():
                return img
        
        # Primeira imagem grande
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src and 'logo' not in src.lower() and 'icon' not in src.lower():
                if src.startswith('http'):
                    return src
                elif src.startswith('/'):
                    return urljoin(url_artigo, src)
        return ""
    except:
        return ""

def otimizar_imagens():
    with open('dados.json', 'r', encoding='utf-8') as f:
        noticias = json.load(f)
    
    print("="*60)
    print("📸 OTIMIZAÇÃO DE IMAGENS")
    print("="*60)
    
    estatisticas = {
        'imagem_real_ja_tinha': 0,
        'imagem_real_extraida': 0,
        'imagem_categoria': 0,
        'sem_link_real': 0
    }
    
    for i, noticia in enumerate(noticias):
        titulo = noticia.get('titulo', '')[:40]
        img_atual = noticia.get('img', '')
        link_real = noticia.get('link_real', '')
        categoria = noticia.get('categoria', 'Sociedade')
        
        # Se já tem imagem real (não é Unsplash nem placeholder)
        if img_atual and 'unsplash' not in img_atual and 'picsum' not in img_atual:
            print(f"\n{i+1}. ✅ Já tem imagem real: {titulo}...")
            estatisticas['imagem_real_ja_tinha'] += 1
            continue
        
        # Se tem link_real, tenta extrair imagem real
        if link_real and link_real != '#':
            print(f"\n{i+1}. 🔍 Tentando extrair imagem real: {titulo}...")
            print(f"     Link: {link_real[:60]}...")
            
            imagem_real = extrair_imagem_real(link_real)
            if imagem_real:
                noticia['img'] = imagem_real
                estatisticas['imagem_real_extraida'] += 1
                print(f"     ✅ Imagem real encontrada!")
                continue
            else:
                print(f"     ❌ Não foi possível extrair imagem real")
        
        # Fallback: imagem por categoria
        if not link_real or link_real == '#':
            estatisticas['sem_link_real'] += 1
        
        nova_img = IMAGENS_POR_CATEGORIA.get(categoria, IMAGEM_PADRAO)
        noticia['img'] = nova_img
        estatisticas['imagem_categoria'] += 1
        print(f"\n{i+1}. 🖼️ Usando imagem por categoria ({categoria}): {titulo}...")
    
    # Salvar
    with open('dados.json', 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print("📊 RESUMO FINAL")
    print("="*60)
    print(f"✅ Já tinham imagem real: {estatisticas['imagem_real_ja_tinha']}")
    print(f"📸 Imagens reais extraídas agora: {estatisticas['imagem_real_extraida']}")
    print(f"🖼️ Imagens por categoria (fallback): {estatisticas['imagem_categoria']}")
    print(f"⚠️ Notícias sem link_real: {estatisticas['sem_link_real']}")
    print(f"📰 Total de notícias: {len(noticias)}")
    print("="*60)

if __name__ == "__main__":
    otimizar_imagens()
