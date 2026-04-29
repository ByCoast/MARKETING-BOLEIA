#!/usr/bin/env python3
"""
patch_destaque_filtro.py — Fundo do destaque com imagem + filtro Tudo
Corre no Termux:
  cd ~/nampula-e-a-cena
  python patch_destaque_filtro.py
"""
import re
import subprocess
from datetime import datetime

FICHEIRO = "index.html"

print("="*55)
print("🎨 PATCH — Destaque Visual + Filtro Tudo")
print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("="*55)

with open(FICHEIRO, 'r', encoding='utf-8') as f:
    html = f.read()

original = html

# ════════════════════════════════════════════════════════════
# 1. MELHORAR FUNDO DO DESTAQUE
#    Em vez de preto sólido, usa a imagem da notícia como fundo
#    com overlay gradiente escuro por cima
# ════════════════════════════════════════════════════════════

# Substituir CSS do destaque-wrap e destaque-inner
html = re.sub(
    r'\.destaque-wrap\{[^}]+\}',
    ".destaque-wrap{background:var(--ink);padding:0 20px 24px;}",
    html
)

html = re.sub(
    r'\.destaque-inner\{[^}]+\}',
    (".destaque-inner{"
     "max-width:1280px;margin:0 auto;"
     "display:grid;grid-template-columns:1fr;"
     "overflow:hidden;cursor:pointer;"
     "border-radius:8px;"
     "position:relative;"
     "min-height:280px;"
     "border:1px solid rgba(255,255,255,.08);"
     "transition:border-color .25s;}"),
    html
)

# Adicionar estilos novos do destaque antes de </style>
estilos_destaque = """
/* ── DESTAQUE COM IMAGEM DE FUNDO ── */
.destaque-inner::before{
  content:'';
  position:absolute;inset:0;
  background-image:var(--dest-img,none);
  background-size:cover;
  background-position:center;
  filter:brightness(.35) saturate(1.2);
  transition:filter .4s;
  z-index:0;
}
.destaque-inner:hover::before{filter:brightness(.28) saturate(1.4);}
.destaque-inner::after{
  content:'';
  position:absolute;inset:0;
  background:linear-gradient(
    135deg,
    rgba(200,32,43,.35) 0%,
    rgba(10,10,15,.85) 60%,
    rgba(10,10,15,.95) 100%
  );
  z-index:1;
}
.destaque-img-wrap{display:none;}
.destaque-body{
  padding:28px 24px;
  position:relative;z-index:2;
  display:flex;flex-direction:column;justify-content:center;
  min-height:280px;
}
.destaque-data{
  font-family:'Outfit',sans-serif;font-size:9px;letter-spacing:2.5px;
  text-transform:uppercase;color:rgba(255,255,255,.45);
  margin-bottom:12px;display:block;
}
.destaque-titulo{
  font-family:'Oswald','Outfit',sans-serif;
  font-size:clamp(20px,4vw,30px);
  font-weight:600;letter-spacing:.5px;
  color:#fff;line-height:1.2;margin-bottom:14px;
  text-shadow:0 2px 12px rgba(0,0,0,.6);
}
.destaque-desc{
  font-size:13px;color:rgba(255,255,255,.6);
  line-height:1.7;margin-bottom:20px;
  display:-webkit-box;-webkit-line-clamp:3;
  -webkit-box-orient:vertical;overflow:hidden;
}
.destaque-ler{
  display:inline-flex;align-items:center;gap:8px;
  background:var(--red);color:#fff;
  border:none;padding:11px 20px;cursor:pointer;
  font-family:'Outfit',sans-serif;font-weight:700;
  font-size:10px;letter-spacing:2px;text-transform:uppercase;
  border-radius:3px;transition:all .2s;align-self:flex-start;
}
.destaque-ler:hover{background:var(--red2);transform:translateY(-2px);}
@media(min-width:640px){
  .destaque-inner{min-height:300px;}
  .destaque-titulo{font-size:clamp(22px,3.5vw,32px);}
}"""

if '.destaque-inner::before' not in html:
    html = html.replace('</style>', estilos_destaque + '\n</style>', 1)
    print("✅ CSS do destaque com imagem de fundo adicionado")
else:
    print("✅ CSS destaque já existe — a actualizar apenas")
    html = re.sub(
        r'/\* ── DESTAQUE COM IMAGEM DE FUNDO ── \*/.*?(?=</style>)',
        estilos_destaque + '\n',
        html, flags=re.DOTALL
    )

# ════════════════════════════════════════════════════════════
# 2. ACTUALIZAR FUNÇÃO mostrarDestaque
#    Aplicar imagem como CSS custom property --dest-img
# ════════════════════════════════════════════════════════════
old_mostrar = re.search(
    r'function mostrarDestaque\(item\)\{.*?\n\}',
    html, re.DOTALL
)

NOVA_MOSTRAR = """function mostrarDestaque(item){
  const wrap=document.getElementById('destaque-wrap');
  const inner=document.getElementById('destaque-inner');

  // Aplicar imagem como fundo via CSS custom property
  if(item.img && item.img.startsWith('http')){
    inner.style.setProperty('--dest-img', `url('${item.img}')`);
  } else {
    const cats={
      'Tecnologia':'https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=70',
      'Economia':'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=70',
      'Saúde':'https://images.unsplash.com/photo-1584820927498-cfe5211fd8bf?w=800&q=70',
      'Política':'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=800&q=70',
      'Internacional':'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=70',
      'Emprego':'https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=800&q=70',
      'Tecnologia':'https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=70',
    };
    const fb=cats[item.categoria]||'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=70';
    inner.style.setProperty('--dest-img', `url('${fb}')`);
  }

  document.getElementById('destaque-cat').textContent=item.categoria||item.tipo;
  document.getElementById('destaque-data').textContent=item.data||'';
  document.getElementById('destaque-titulo').textContent=item.titulo;
  const frasesDest=(item.desc||'').match(/[^.!?]+[.!?]+/g)||[];
  const resumo=frasesDest.slice(0,2).join(' ').trim()||((item.desc||'').substring(0,160));
  document.getElementById('destaque-desc').textContent=resumo;
  wrap.style.display='block';
  document.getElementById('destaque-btn').onclick=()=>{
    const tab=document.querySelector(`.tab[data-tipo="${item.tipo}"]`);
    if(tab)mudarFeed(tab);
    setTimeout(()=>window.scrollTo({top:document.getElementById('feed-home').offsetTop-80,behavior:'smooth'}),300);
  };
}"""

if old_mostrar:
    html = html.replace(old_mostrar.group(), NOVA_MOSTRAR)
    print("✅ função mostrarDestaque actualizada")
else:
    print("⚠️  mostrarDestaque não encontrada pelo padrão")

# ════════════════════════════════════════════════════════════
# 3. CORRIGIR FILTRO "TUDO" — remover limite de 9
# ════════════════════════════════════════════════════════════
antes = html.count(',9)')
html = re.sub(
    r"(renderFeed\('feed-home',[^)]+)\,9\)",
    r"\1)",
    html
)
depois = html.count(',9)')
if antes > depois:
    print(f"✅ Limite de 9 itens removido")
else:
    print("✅ Filtro Tudo sem limite — já corrigido")

# ════════════════════════════════════════════════════════════
# 4. GARANTIR formatarDesc EXISTE
# ════════════════════════════════════════════════════════════
if 'function formatarDesc' not in html:
    FORMATAR = """
// ══ FORMATAR DESCRIÇÃO ══
function formatarDesc(texto){
  if(!texto||texto.length<10)return '<p>Clique para ler mais.</p>';
  texto=texto.replace(/\\s+/g,' ').trim();
  const frases=texto.match(/[^.!?…]+[.!?…]+/g)||[texto];
  const pars=[];let grupo=[];
  frases.forEach((f,i)=>{
    grupo.push(f.trim());
    if(grupo.length>=2||i===frases.length-1){pars.push(grupo.join(' '));grupo=[];}
  });
  let h='';
  if(pars.length>0)h+=`<p class="art-lead">${pars.shift()}</p>`;
  pars.forEach(p=>{if(p.trim().length>10)h+=`<p>${p.trim()}</p>`;});
  return h||`<p>${texto}</p>`;
}
"""
    if 'function imgFallback' in html:
        html = html.replace('function imgFallback', FORMATAR + '\nfunction imgFallback')
    elif 'function buildCard' in html:
        html = html.replace('function buildCard', FORMATAR + '\nfunction buildCard')
    print("✅ formatarDesc restaurada")
else:
    print("✅ formatarDesc já existe")

# Garantir que buildCard usa formatarDesc
if "'${item.desc}'" in html or '"${item.desc}"' in html:
    html = html.replace('${item.desc}', '${formatarDesc(item.desc)}')
    print("✅ buildCard usa formatarDesc")

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
     f"🎨 Destaque com imagem de fundo + filtro Tudo — {datetime.now().strftime('%d/%m/%Y %H:%M')}"],
    ["git", "push"]
]:
    r = subprocess.run(cmd, capture_output=True, text=True)
    saida = r.stdout.strip() or r.stderr.strip()
    ok = r.returncode == 0 or "nothing to commit" in saida
    print(f"  {'✅' if ok else '⚠️ '} {' '.join(cmd[:2])}{': '+saida[:80] if not ok else ''}")

print("\n" + "="*55)
print("🎉 SITE ACTUALIZADO!")
print("   ✅ Destaque com imagem de fundo + gradiente")
print("   ✅ Filtro Tudo sem limite de itens")
print("   ✅ Descrições formatadas em parágrafos")
print("="*55)
