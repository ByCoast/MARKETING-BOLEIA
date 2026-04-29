import re
import subprocess
from datetime import datetime

FICHEIRO = "index.html"

print("="*55)
print("✏️  PATCH DE TIPOGRAFIA — Nampula é a Cena")
print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("="*55)

with open(FICHEIRO, 'r', encoding='utf-8') as f:
    html = f.read()

original = html

# 1. TROCAR IMPORTAÇÃO DE FONTES
html = re.sub(
    r'<link href="https://fonts\.googleapis\.com/css2\?[^"]*Bebas[^"]*"[^>]*>',
    '<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Outfit:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">',
    html
)
print("✅ Importação de fontes actualizada")

# 2. SUBSTITUIR REFERÊNCIAS DA FONTE
html = html.replace("'Bebas Neue',sans-serif", "'Oswald',sans-serif")
html = html.replace('"Bebas Neue",sans-serif', '"Oswald",sans-serif')
print("✅ Bebas Neue → Oswald")

# 3. AJUSTAR TÍTULO DO DESTAQUE
html = re.sub(
    r'(\.destaque-titulo\{[^}]*?)font-size:[^;]+;',
    r'\1font-size:clamp(18px,3.2vw,24px);',
    html
)
html = re.sub(
    r'(\.destaque-titulo\{[^}]*?)letter-spacing:[^;]+;',
    r'\1letter-spacing:0.5px;',
    html
)
print("✅ Título do destaque ajustado")

# 4. AJUSTAR TÍTULOS DOS CARDS
html = re.sub(
    r'(\.c-title\{[^}]*?)font-size:[^;]+;',
    r'\1font-size:16px;',
    html
)
html = re.sub(
    r'(\.c-title\{[^}]*?)letter-spacing:[^;]+;',
    r'\1letter-spacing:0.3px;',
    html
)
html = re.sub(
    r'(\.c-title\{[^}]*?)line-height:[^;]+;',
    r'\1line-height:1.3;',
    html
)
print("✅ Títulos dos cards ajustados")

# 5. AJUSTAR LOGO
html = re.sub(
    r'(\.logo-name\{[^}]*?)letter-spacing:[^;]+;',
    r'\1letter-spacing:4px;',
    html
)
print("✅ Logo ajustado")

# 6. NEWSLETTER
html = re.sub(
    r'(\.nl-title\{[^}]*?)font-weight:[^;]+;',
    r'\1font-weight:700;',
    html
)
print("✅ Título newsletter ajustado")

if html == original:
    print("\n⚠️ Nenhuma alteração detectada.")
    exit(0)

with open(FICHEIRO, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"\n💾 {FICHEIRO} guardado")

print("\n🚀 A publicar no GitHub...")
cmds = [
    ["git", "add", "index.html"],
    ["git", "commit", "-m", f"✏️ Melhoria tipografia"],
    ["git", "push"]
]
for cmd in cmds:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 or "nothing to commit" in result.stdout:
        print(f"  ✅ {' '.join(cmd)}")
    else:
        print(f"  ⚠️ {result.stderr[:100]}")

print("\n" + "="*55)
print("🎉 TIPOGRAFIA ACTUALIZADA!")
print("="*55)
