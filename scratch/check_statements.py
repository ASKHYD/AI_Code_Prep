import json, glob

for p in sorted(glob.glob('data/problems/*.json')):
    with open(p, 'r', encoding='utf-8') as f:
        d = json.load(f)
    s = d.get('statement_md', '')
    lines = s.splitlines()
    for i, line in enumerate(lines):
        if 'Function Signature' in line or 'def ' in line:
            print(f"{d['id']}: L{i}: {line}")

