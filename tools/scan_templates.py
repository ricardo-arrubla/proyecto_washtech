import glob, re
files = glob.glob('templates/**/*.html', recursive=True)
bad = []
for f in files:
    with open(f, encoding='utf-8') as fh:
        c = fh.read()
    b = len(re.findall(r'{%\s*block\b', c))
    e = len(re.findall(r'{%\s*endblock\b', c))
    if b != e:
        bad.append((f, b, e))
print('Scanned', len(files), 'template files')
if bad:
    print('PROBLEMATIC FILES:')
    for f, b, e in bad:
        print(f, 'blocks=', b, 'endblocks=', e)
else:
    print('No problems found: all blocks matched')
