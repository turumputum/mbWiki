"""Проверка собранного сайта (public/): битые внутренние ссылки, картинки и эмбеды.

    python tools/check_links.py            # локальная сборка public/
    python tools/check_links.py --live https://mbwiki.ru   # ещё и HEAD-запросы к серверу
"""
import os, re, sys, io, html
from urllib.parse import unquote, urljoin, urlparse

ROOT = os.path.join(os.path.dirname(__file__), '..', 'public')
live = None
if '--live' in sys.argv:
    live = sys.argv[sys.argv.index('--live') + 1].rstrip('/')

pages = []
for dp, dn, fn in os.walk(ROOT):
    for f in fn:
        if f.endswith('.html'):
            pages.append(os.path.join(dp, f))

attr_re = re.compile(r'(?:href|src)="([^"]+)"')
missing = {}       # target -> [pages]
checked = set()

def exists(target):
    p = os.path.join(ROOT, target)
    if os.path.isfile(p): return True
    if os.path.isfile(p + '.html'): return True
    if os.path.isdir(p) and os.path.isfile(os.path.join(p, 'index.html')): return True
    return False

for page in pages:
    s = io.open(page, encoding='utf-8', errors='ignore').read()
    rel_dir = os.path.relpath(os.path.dirname(page), ROOT).replace('\\', '/')
    for m in attr_re.finditer(s):
        url = html.unescape(m.group(1))
        if url.startswith(('http://', 'https://', 'mailto:', 'data:', '#', 'javascript:')):
            continue
        url = url.split('#')[0].split('?')[0]
        if not url: continue
        if url.startswith('/'):
            target = url.lstrip('/')
        else:
            target = os.path.normpath(os.path.join(rel_dir, url)).replace('\\', '/')
            if target.startswith('..'): target = target.lstrip('./')
        target = unquote(target)
        if target in ('', '.'): target = 'index'
        if not exists(target):
            missing.setdefault(target, []).append(os.path.relpath(page, ROOT).replace('\\', '/'))

# картинки-эмбеды, которых нет: Quartz оставляет <img src="..."> - уже поймано выше;
# ненайденные вики-ссылки Quartz помечает классом "broken"
broken_wiki = {}
for page in pages:
    s = io.open(page, encoding='utf-8', errors='ignore').read()
    for m in re.finditer(r'<a[^>]*class="[^"]*\bbroken\b[^"]*"[^>]*>(.*?)</a>', s):
        broken_wiki.setdefault(m.group(1), []).append(os.path.relpath(page, ROOT).replace('\\', '/'))
    for m in re.finditer(r'не может быть найден|Transclude of .*? not found', s):
        broken_wiki.setdefault('[transclude] ' + m.group(0), []).append(os.path.relpath(page, ROOT).replace('\\', '/'))

print(f'pages: {len(pages)}')
print(f'\n--- missing targets: {len(missing)}')
for t, ps in sorted(missing.items()):
    print(f'  {t}   <- {ps[0]}' + (f' (+{len(ps)-1})' if len(ps) > 1 else ''))
print(f'\n--- broken wikilinks: {len(broken_wiki)}')
for t, ps in sorted(broken_wiki.items()):
    print(f'  {t}   <- {ps[0]}' + (f' (+{len(ps)-1})' if len(ps) > 1 else ''))

if live:
    import urllib.request
    print(f'\n--- live check {live}')
    bad = 0
    for page in sorted(pages):
        rel = os.path.relpath(page, ROOT).replace('\\', '/')
        if rel.startswith(('tags/', 'static/')): continue
        url = live + '/' + rel[:-5] if rel != 'index.html' else live + '/'
        if url.endswith('/index'): url = url[:-5]
        try:
            req = urllib.request.Request(urllib.parse.quote(url, safe=':/'), method='HEAD')
            code = urllib.request.urlopen(req, timeout=15).status
        except Exception as e:
            code = getattr(e, 'code', str(e))
        if code != 200:
            bad += 1; print(f'  {code}  {url}')
    print(f'  live pages not 200: {bad}')
