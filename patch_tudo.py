#!/usr/bin/env python3
"""
patch_tudo.py — Filtro Tudo mostra mix de notícias (sem vagas)
Corre no Termux:
  cd ~/nampula-e-a-cena
  python patch_tudo.py
"""
import re
import subprocess
from datetime import datetime

FICHEIRO = "index.html"

print("="*55)
print("🔧 PATCH — Filtro Tudo (mix sem vagas)")
print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("="*55)

with open(FICHEIRO, 'r', encoding='utf-8') as f:
    html = f.read()

original = html

# ════════════════════════════════════════════════════════════
# 1. CORRIGIR mudarFeed — quando tab é "noticia" e cat é "Tudo"
#    mostra MIX de noticia + bolada (sem vaga)
# ════════════════════════════════════════════════════════════

OLD_MUDAR = re.search(r'function mudarFeed\(tab\)\{[^\n]+\n', html)

NOVA_MUDAR = """function mudarFeed(tab){
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  tab.classList.add('active');
  tipoAtivo=tab.getAttribute('data-tipo');
  actualizarFiltrosHome();
  // Tudo na tab Notícias mostra mix (noticia + bolada, sem vaga)
  if(tipoAtivo==='noticia'){
    renderFeed('feed-home', dadosBase.filter(i=>i.tipo!=='vaga'));
  } else {
    renderFeed('feed-home', dadosBase.filter(i=>i.tipo===tipoAtivo));
  }
}
"""

if OLD_MUDAR:
    html = html.replace(OLD_MUDAR.group(), NOVA_MUDAR)
    print("✅ mudarFeed actualizado")
else:
    html = re.sub(
        r'function mudarFeed\(tab\)\{.*?\}',
        NOVA_MUDAR,
        html, flags=re.DOTALL
    )
    print("✅ mudarFeed substituído (regex)")

# ════════════════════════════════════════════════════════════
# 2. CORRIGIR filtrarHome — Tudo mostra mix sem vagas
# ════════════════════════════════════════════════════════════

OLD_FILTRAR = re.search(r'function filtrarHome\(cat,btn\)\{[^\n]+', html)

NOVA_FILTRAR = """function filtrarHome(cat,btn){
  btn.parentElement.querySelectorAll('.btn-f').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  if(tipoAtivo==='noticia'){
    // Tudo = mix de noticia + bolada; categoria filtra só noticias
    const base = cat==='Tudo'
      ? dadosBase.filter(i=>i.tipo!=='vaga')
      : dadosBase.filter(i=>i.tipo===tipoAtivo && i.categoria===cat);
    renderFeed('feed-home', base);
  } else {
    renderFeed('feed-home', dadosBase.filter(i=>i.tipo===tipoAtivo&&(cat==='Tudo'||i.categoria===cat)));
  }
}"""

if OLD_FILTRAR:
    html = html.replace(OLD_FILTRAR.group(), NOVA_FILTRAR)
    print("✅ filtrarHome actualizado")
else:
    html = re.sub(
        r'function filtrarHome\(cat,btn\)\{.*?\}',
        NOVA_FILTRAR,
        html, flags=re.DOTALL
    )
    print("✅ filtrarHome substituído (regex)")

# ════════════════════════════════════════════════════════════
# 3. CORRIGIR actualizarFiltrosHome — carregar com mix inicial
# ════════════════════════════════════════════════════════════

OLD_ACT = re.search(r'function actualizarFiltrosHome\(\)\{.*?\}', html, re.DOTALL)

NOVA_ACT = """function actualizarFiltrosHome(){
  const el=document.getElementById('filtros-home');if(!el)return;
  // Categorias só de noticias (não vagas) para o mix
  const base = tipoAtivo==='noticia'
    ? dadosBase.filter(i=>i.tipo!=='vaga')
    : dadosBase.filter(i=>i.tipo===tipoAtivo);
  const cats=[...new Set(base.filter(i=>i.categoria).map(i=>i.categoria))];
  el.innerHTML=`<button class="btn-f active" onclick="filtrarHome('Tudo',this)">Tudo</button>`
    +cats.map(c=>`<button class="btn-f" onclick="filtrarHome('${c}',this)">${c}</button>`).join('');
}"""

if OLD_ACT:
    html = html.replace(OLD_ACT.group(), NOVA_ACT)
    print("✅ actualizarFiltrosHome actualizado")

# ════════════════════════════════════════════════════════════
# 4. CORRIGIR renderFeed inicial no carregar()
#    Quando página abre, mostrar mix (sem vagas)
# ════════════════════════════════════════════════════════════

# Linha que renderiza o feed inicial após carregar dados
html = re.sub(
    r"renderFeed\('feed-home',dadosBase\.filter\(i=>i\.tipo===.noticia.\),?9?\);",
    "renderFeed('feed-home', dadosBase.filter(i=>i.tipo!=='vaga'));",
    html
)
print("✅ Feed inicial corrigido (mix sem vagas)")

# ════════════════════════════════════════════════════════════
# 5. GUARDAR E PUSH
# ════════════════════════════════════════════════════════════
if html == original:
    print("\n⚠️  Nenhuma alteração aplicada.")
    exit(0)

with open(FICHEIRO, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"\n💾 {FICHEIRO} guardado")

print("\n🚀 A publicar no GitHub...")
for cmd in [
    ["git", "add", "index.html"],
    ["git", "commit", "-m",
     f"🔧 Filtro Tudo: mix notícias sem vagas — {datetime.now().strftime('%d/%m/%Y %H:%M')}"],
    ["git", "push"]
]:
    r = subprocess.run(cmd, capture_output=True, text=True)
    saida = r.stdout.strip() or r.stderr.strip()
    ok = r.returncode == 0 or "nothing to commit" in saida
    print(f"  {'✅' if ok else '⚠️ '} {' '.join(cmd[:2])}{': '+saida[:80] if not ok else ''}")

print("\n" + "="*55)
print("🎉 SITE ACTUALIZADO!")
print("   ✅ Tudo = mix notícias + mercado (sem vagas)")
print("   ✅ Categorias filtram dentro do mix")
print("   ✅ Tab Vagas continua a mostrar só vagas")
print("="*55)
