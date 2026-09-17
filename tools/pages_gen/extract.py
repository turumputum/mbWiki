import re, glob, json, io, os

BASE = os.environ.get('MB_BUILD', '../moduleBox/build/esp-idf')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manifest_all.json')

pat = re.compile(r'"((?:[^"\\]|\\.)*)"')
out = {}
files = sorted(glob.glob(os.path.join(BASE, '*/generated_files/gen_*.h')))
print("gen files:", len(files))
for f in files:
    s = io.open(f, encoding='utf-8').read()
    raw = ''.join(pat.findall(s))
    txt = raw.encode('utf-8').decode('unicode_escape')
    try:
        txt = txt.encode('latin-1').decode('utf-8')
    except Exception:
        pass
    dec = json.JSONDecoder()
    idx = 0
    found = 0
    while idx < len(txt):
        while idx < len(txt) and txt[idx] not in '{':
            idx += 1
        if idx >= len(txt):
            break
        try:
            d, end = dec.raw_decode(txt, idx)
        except Exception as e:
            print("FAIL", os.path.basename(f), e)
            break
        idx = end
        d['_file'] = os.path.basename(f)
        out[d.get('mode', os.path.basename(f))] = d
        found += 1
    if not found:
        print("EMPTY", os.path.basename(f))

io.open(OUT, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=1))
print("modes:", len(out))
for k in sorted(out):
    v = out[k]
    print("%-16s trig=%-28s act=%-28s slots=%-6s [%s]" % (
        k, v.get('trigger'), v.get('action'), v.get('slots'), v['_file']))
    print("    rep:", [r.get('topic') for r in v.get('reports', [])])
    print("    cmd:", [c.get('command') for c in v.get('commands', [])])
