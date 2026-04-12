import requests
import json
import time
import re
from googlesearch import search
from urllib.parse import urlparse

def extrair_link_real(titulo, site_preferido=None):
    """Pesquisa o título da notícia e tenta encontrar o link original"""
    
    # Palavras-chave para refinar a busca
    termos_pesquisa = titulo[:80]  # Primeiros 80 caracteres
    
    # Lista de sites moçambicanos confiáveis (prioridade)
    sites_prioritarios = [
        'opais.co.mz',
        'mznews.co.mz',
        'cartamz.com',
        'verdade.co.mz',
        'mediafax.co.mz',
        'jornalnoticias.co.mz',
        'canalmoz.co.mz',
        'folhademaputo.co.mz',
        'dw.com',
        'voaportugues.com',
        'bbc.com',
        'rfi.fr'
    ]
    
    try:
        print(f"  🔍 A pesquisar: {termos_pesquisa[:50]}...")
        
        # Pesquisar no Google
        resultados = list(search(termos_pesquisa, num_results=5, lang='pt'))
        
        # Primeiro, tentar encontrar sites prioritários
        for url in resultados:
            for site in sites_prioritarios:
                if site in url:
                    print(f"     ✅ Link encontrado: {url[:80]}...")
                    return url
        
        # Se não encontrou sites prioritários, devolve o primeiro resultado
        if resultados:
            print(f"     ⚠️ Link alternativo: {resultados[0][:80]}...")
            return resultados[0]
        else:
            print(f"     ❌ Nenhum link encontrado")
            return ""
            
    except Exception as e:
        print(f"     ❌ Erro: {e}")
        return ""

def atualizar_links_reais(arquivo_entrada, arquivo_saida):
    """Lê o JSON, extrai links reais e guarda atualizado"""
    
    with open(arquivo_entrada, 'r', encoding='utf-8') as f:
        noticias = json.load(f)
    
    print(f"📰 Total de notícias: {len(noticias)}")
    print("="*50)
    
    for i, noticia in enumerate(noticias):
        print(f"\n{i+1}. {noticia['titulo'][:60]}...")
        
        # Verificar se já tem link_real
        if noticia.get('link_real') and noticia['link_real'].startswith('http'):
            print(f"   ✅ Já tem link: {noticia['link_real'][:60]}...")
            continue
        
        # Extrair link real
        link = extrair_link_real(noticia['titulo'])
        
        if link:
            noticia['link_real'] = link
        else:
            noticia['link_real'] = "#"
        
        # Pausa entre pesquisas (evitar bloqueio)
        time.sleep(2)
    
    # Salvar JSON atualizado
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*50)
    print(f"✅ Arquivo atualizado salvo em: {arquivo_saida}")
    
    # Estatísticas
    com_link = len([n for n in noticias if n.get('link_real') and n['link_real'] != '#'])
    print(f"📊 Notícias com link real: {com_link}/{len(noticias)}")

if __name__ == "__main__":
    # Instalar googlesearch-python se não estiver instalado
    try:
        from googlesearch import search
    except ImportError:
        print("📦 A instalar googlesearch-python...")
        import subprocess
        subprocess.run(['pip', 'install', 'googlesearch-python'])
        from googlesearch import search
    
    # Processar o arquivo
    atualizar_links_reais('noticias_links.json', 'noticias_links_atualizado.json')
