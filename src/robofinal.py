import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime
from urllib.parse import urljoin

class Colors:
    OK = '\033[92m'
    INFO = '\033[94m'
    WARN = '\033[93m'
    RESET = '\033[0m'

print(f"{Colors.INFO}{'='*60}{Colors.RESET}")
print(f"{Colors.INFO}🤖 ROBÔ DE NOTÍCIAS E VAGAS - Nampula é a Cena{Colors.RESET}")
print(f"{Colors.INFO}{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{Colors.RESET}")
print(f"{Colors.INFO}{'='*60}{Colors.RESET}")

todas_vagas = []
todas_noticias = []
titulos_vistos = set()

def extrair_conteudo_completo(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        titulo = ""
        titulo_elem = soup.find('h1')
        if not titulo_elem:
            titulo_elem = soup.find('title')
        if titulo_elem:
            titulo = titulo_elem.get_text(strip=True)
        
        desc = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc = meta_desc['content'].strip()
        else:
            og_desc = soup.find('meta', property='og:description')
            if og_desc and og_desc.get('content'):
                desc = og_desc['content'].strip()
        
        if not desc or len(desc) < 50:
            for p in soup.find_all('p'):
                texto = p.get_text(strip=True)
                if len(texto) > 80 and 'cookie' not in texto.lower():
                    desc = texto[:500]
                    break
        
        img = ""
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            img = og_image['content']
        else:
            primeira_img = soup.find('img')
            if primeira_img and primeira_img.get('src'):
                img = primeira_img['src']
                if img.startswith('/'):
                    img = urljoin(url, img)
        
        return titulo, desc, img
    except Exception as e:
        return "", "", ""

def extrair_vagas_wizandroid():
    vagas = []
    try:
        print(f"\n{Colors.INFO}💼 WizAndroid...{Colors.RESET}")
        url = "https://wizandroidmz.com/emprego/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/emprego/' in href and href not in links:
                links.append(href)
        
        for link in links[:15]:
            try:
                if not link.startswith('http'):
                    link = "https://wizandroidmz.com" + link
                titulo, desc, img = extrair_conteudo_completo(link)
                if not titulo:
                    continue
                if titulo in titulos_vistos:
                    continue
                titulos_vistos.add(titulo)
                vagas.append({
                    "data": datetime.now().strftime("%d/%m/%Y"),
                    "titulo": titulo[:120],
                    "desc": desc[:500] if desc else "Candidate-se através do link",
                    "img": img if img else "https://images.unsplash.com/photo-1523240795612-9a054b0db644?q=80&w=600",
                    "video": "",
                    "tipo": "vaga",
                    "categoria": "Emprego",
                    "fonte": "WizAndroid",
                    "link_vaga": link
                })
                print(f"  {Colors.OK}✅{Colors.RESET} {titulo[:40]}...")
                time.sleep(0.3)
            except:
                continue
    except Exception as e:
        print(f"  {Colors.WARN}⚠️ Erro: {e}{Colors.RESET}")
    return vagas

def extrair_vagas_maisvagas():
    vagas = []
    try:
        print(f"\n{Colors.INFO}💼 MaisVagas...{Colors.RESET}")
        url = "https://maisvagas.co.mz"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'vaga' in href.lower() and href not in links:
                links.append(href)
        
        for link in links[:15]:
            try:
                if not link.startswith('http'):
                    link = "https://maisvagas.co.mz" + link
                titulo, desc, img = extrair_conteudo_completo(link)
                if not titulo:
                    continue
                if titulo in titulos_vistos:
                    continue
                titulos_vistos.add(titulo)
                vagas.append({
                    "data": datetime.now().strftime("%d/%m/%Y"),
                    "titulo": titulo[:120],
                    "desc": desc[:500] if desc else "Candidate-se",
                    "img": img if img else "https://images.unsplash.com/photo-1523240795612-9a054b0db644?q=80&w=600",
                    "video": "",
                    "tipo": "vaga",
                    "categoria": "Emprego",
                    "fonte": "MaisVagas",
                    "link_vaga": link
                })
                print(f"  {Colors.OK}✅{Colors.RESET} {titulo[:40]}...")
                time.sleep(0.3)
            except:
                continue
    except Exception as e:
        print(f"  {Colors.WARN}⚠️ Erro: {e}{Colors.RESET}")
    return vagas

def extrair_vagas_njobs():
    vagas = []
    try:
        print(f"\n{Colors.INFO}💼 nJobs...{Colors.RESET}")
        url = "https://njobs.co.mz"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'vaga' in href.lower() and href not in links:
                links.append(href)
        
        for link in links[:15]:
            try:
                if not link.startswith('http'):
                    link = "https://njobs.co.mz" + link
                titulo, desc, img = extrair_conteudo_completo(link)
                if not titulo:
                    continue
                if titulo in titulos_vistos:
                    continue
                titulos_vistos.add(titulo)
                vagas.append({
                    "data": datetime.now().strftime("%d/%m/%Y"),
                    "titulo": titulo[:120],
                    "desc": desc[:500] if desc else "Candidate-se",
                    "img": img if img else "https://images.unsplash.com/photo-1523240795612-9a054b0db644?q=80&w=600",
                    "video": "",
                    "tipo": "vaga",
                    "categoria": "Emprego",
                    "fonte": "nJOBS",
                    "link_vaga": link
                })
                print(f"  {Colors.OK}✅{Colors.RESET} {titulo[:40]}...")
                time.sleep(0.3)
            except:
                continue
    except Exception as e:
        print(f"  {Colors.WARN}⚠️ Erro: {e}{Colors.RESET}")
    return vagas

def extrair_noticias_generico(nome, url, categoria):
    noticias = []
    try:
        print(f"\n{Colors.INFO}📰 {nome}...{Colors.RESET}")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http') and len(href) > 20 and href not in links:
                if 'facebook' not in href and 'twitter' not in href:
                    links.append(href)
        
        links = links[:25]
        
        for link in links:
            try:
                titulo, desc, img = extrair_conteudo_completo(link)
                if not titulo or len(titulo) < 20:
                    continue
                if titulo in titulos_vistos:
                    continue
                titulos_vistos.add(titulo)
                noticias.append({
                    "data": datetime.now().strftime("%d/%m/%Y"),
                    "titulo": titulo[:150],
                    "desc": desc[:500] if desc else "Clique para ler",
                    "img": img if img else "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?q=80&w=600",
                    "video": "",
                    "tipo": "noticia",
                    "categoria": categoria,
                    "fonte": nome,
                    "link_real": link
                })
                print(f"  {Colors.OK}✅{Colors.RESET} {titulo[:40]}...")
                time.sleep(0.3)
            except:
                continue
    except Exception as e:
        print(f"  {Colors.WARN}⚠️ Erro {nome}: {e}{Colors.RESET}")
    return noticias

def main():
    global todas_vagas, todas_noticias
    
    todas_vagas.extend(extrair_vagas_wizandroid())
    todas_vagas.extend(extrair_vagas_maisvagas())
    todas_vagas.extend(extrair_vagas_njobs())
    
    todas_noticias.extend(extrair_noticias_generico("DW Moçambique", "https://www.dw.com/pt-002/mo%C3%A7ambique/s-30380", "Nacional"))
    todas_noticias.extend(extrair_noticias_generico("BBC News", "https://www.bbc.com/portuguese", "Internacional"))
    todas_noticias.extend(extrair_noticias_generico("IT Forum", "https://itforum.com.br", "Tecnologia"))
    todas_noticias.extend(extrair_noticias_generico("TecMundo", "https://www.tecmundo.com.br/redes-sociais", "Tecnologia"))
    todas_noticias.extend(extrair_noticias_generico("G1 Tecnologia", "https://g1.globo.com/tecnologia/", "Tecnologia"))
    todas_noticias.extend(extrair_noticias_generico("Jornal Notícias", "https://jornalnoticias.co.mz", "Nacional"))
    
    # Combinar dados
    todos_items = list(todas_vagas) + list(todas_noticias)
    
    try:
        with open('dados.json', 'r', encoding='utf-8') as f:
            antigos = json.load(f)
            for n in antigos:
                titulo = n.get('titulo', '')
                if titulo and titulo not in titulos_vistos:
                    todos_items.append(n)
                    titulos_vistos.add(titulo)
    except:
        pass
    
    # SALVAR NOS DOIS LOCAIS
    with open('dados.json', 'w', encoding='utf-8') as f:
        json.dump(todos_items, f, ensure_ascii=False, indent=2)
    
    with open('data/dados.json', 'w', encoding='utf-8') as f:
        json.dump(todos_items, f, ensure_ascii=False, indent=2)
    
    print(f"\n{Colors.INFO}{'='*60}{Colors.RESET}")
    print(f"{Colors.OK}✅ RESULTADO FINAL:{Colors.RESET}")
    print(f"   Total: {len(todos_items)}")
    print(f"   💼 Vagas: {len(todas_vagas)}")
    print(f"   📰 Notícias: {len(todas_noticias)}")
    print(f"   📁 dados.json e data/dados.json atualizados")
    print(f"{Colors.INFO}{'='*60}{Colors.RESET}")

if __name__ == "__main__":
    main()
