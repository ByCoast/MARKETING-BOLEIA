import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def extrair_vagas_njobs():
    vagas = []
    url = "https://njobs.co.mz"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        job_elements = soup.find_all(['div', 'article', 'li'], class_=re.compile(r'job|vaga|emprego', re.I))
        for elem in job_elements[:10]:
            try:
                titulo_elem = elem.find(['h2', 'h3', 'h4', 'strong'])
                titulo = titulo_elem.get_text(strip=True) if titulo_elem else ""
                if not titulo or len(titulo) < 8:
                    continue
                desc_elem = elem.find('p')
                desc = desc_elem.get_text(strip=True)[:250] if desc_elem else ""
                link_elem = elem.find('a', href=True)
                link = link_elem['href'] if link_elem else ""
                if link and not link.startswith('http'):
                    link = "https://njobs.co.mz" + link
                vagas.append({
                    "data": datetime.now().strftime("%d/%m/%Y"),
                    "titulo": titulo[:100],
                    "desc": desc if desc else "Candidate-se a esta oportunidade",
                    "img": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?q=80&w=600",
                    "video": "",
                    "tipo": "vaga",
                    "categoria": "Emprego",
                    "fonte": "nJOBS",
                    "link_vaga": link
                })
            except: continue
    except Exception as e: print(f"  ⚠️ nJOBS: {e}")
    return vagas

def extrair_vagas_emprego_co_mz():
    vagas = []
    url = "https://www.emprego.co.mz"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        job_elements = soup.find_all(['div', 'article'], class_=re.compile(r'vaga|job|oferta', re.I))
        for elem in job_elements[:10]:
            try:
                titulo_elem = elem.find(['h2', 'h3', 'h4'])
                titulo = titulo_elem.get_text(strip=True) if titulo_elem else ""
                if not titulo or len(titulo) < 8:
                    continue
                desc_elem = elem.find('p')
                desc = desc_elem.get_text(strip=True)[:250] if desc_elem else ""
                link_elem = elem.find('a', href=True)
                link = link_elem['href'] if link_elem else ""
                if link and not link.startswith('http'):
                    link = "https://www.emprego.co.mz" + link
                vagas.append({
                    "data": datetime.now().strftime("%d/%m/%Y"),
                    "titulo": titulo[:100],
                    "desc": desc if desc else "Candidate-se a esta oportunidade",
                    "img": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?q=80&w=600",
                    "video": "",
                    "tipo": "vaga",
                    "categoria": "Emprego",
                    "fonte": "emprego.co.mz",
                    "link_vaga": link
                })
            except: continue
    except Exception as e: print(f"  ⚠️ emprego.co.mz: {e}")
    return vagas

def extrair_vagas_mmo():
    vagas = []
    url = "https://emprego.mmo.co.mz/local/varios-locais/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        artigos = soup.find_all('article')
        if not artigos:
            artigos = soup.find_all('div', class_=re.compile(r'job|vaga|item|post', re.I))
        for elem in artigos[:10]:
            try:
                titulo_elem = elem.find(['h2', 'h3', 'h4'])
                titulo = titulo_elem.get_text(strip=True) if titulo_elem else ""
                if not titulo or len(titulo) < 8:
                    link_elem = elem.find('a', href=True)
                    if link_elem:
                        titulo = link_elem.get_text(strip=True)
                if not titulo or len(titulo) < 8:
                    continue
                desc_elem = elem.find('p')
                desc = desc_elem.get_text(strip=True)[:250] if desc_elem else ""
                link_elem = elem.find('a', href=True)
                link = link_elem['href'] if link_elem else ""
                if link and not link.startswith('http'):
                    link = "https://emprego.mmo.co.mz" + link
                vagas.append({
                    "data": datetime.now().strftime("%d/%m/%Y"),
                    "titulo": titulo[:100],
                    "desc": desc if desc else "Candidate-se a esta oportunidade",
                    "img": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?q=80&w=600",
                    "video": "",
                    "tipo": "vaga",
                    "categoria": "Emprego",
                    "fonte": "MMO Emprego",
                    "link_vaga": link
                })
            except: continue
    except Exception as e: print(f"  ⚠️ MMO Emprego: {e}")
    return vagas

def extrair_todas_vagas():
    print("📢 A buscar vagas de emprego...")
    print("  🔹 nJOBS...")
    vagas1 = extrair_vagas_njobs()
    print(f"     ✅ {len(vagas1)} vagas")
    print("  🔹 emprego.co.mz...")
    vagas2 = extrair_vagas_emprego_co_mz()
    print(f"     ✅ {len(vagas2)} vagas")
    print("  🔹 MMO Emprego...")
    vagas3 = extrair_vagas_mmo()
    print(f"     ✅ {len(vagas3)} vagas")
    todas = vagas1 + vagas2 + vagas3
    print(f"\n📊 Total de vagas: {len(todas)}")
    return todas

if __name__ == "__main__":
    vagas = extrair_todas_vagas()
    with open('vagas_completo.json', 'w') as f:
        json.dump(vagas, f, ensure_ascii=False, indent=2)
    print("✅ Salvo em vagas_completo.json")
