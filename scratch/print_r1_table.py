import json

with open('docs/screenshots/r6/addendum_v2_results.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print("| # | Problem ID | Problem Title | Live Statement Signature (`.signature-pre`) | Live Editor Line 1 (Ace Editor) | Match |")
print("|---|---|---|---|---|:---:|")
for i, row in enumerate(d['r1_all_12_problems'], 1):
    status = "✅ Equal" if row['equal'] else "❌ Diff"
    print(f"| {i} | `{row['id']}` | **{row['title']}** | `{row['statement_sig']}` | `{row['editor_line1']}` | {status} |")

