import json, glob, re

for p in sorted(glob.glob('data/problems/*.json')):
    with open(p, 'r', encoding='utf-8') as f:
        d = json.load(f)
    s = d.get('statement_md', '')
    m = re.search(r'###\s*Function Signature\s*```(?:python)?\s*[\r\n]+(.*?)```', s, re.DOTALL)
    if m:
        prose_before = s[:m.start()].strip()
        sig_in_md = m.group(1).strip()
        rest_after = s[m.end():].strip()
        starter_line1 = d.get('starter_code', '').splitlines()[0].strip()
        print(f"{d['id']}: MATCHED!")
        print(f"  starter line 1: {starter_line1}")
        print(f"  statement md sig: {sig_in_md}")
    else:
        print(f"{d['id']}: NOT MATCHED!")

