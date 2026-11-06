import glob
import json
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from coach.problems import ProblemSchema, load_problem_from_file

REQUIRED_FIELDS = [
    "id", "title", "topic", "difficulty", "track", "statement_md",
    "function_name", "starter_code", "visible_tests", "hidden_tests",
    "hints", "reference_solution", "time_limit_sec"
]

problem_files = sorted(glob.glob("data/problems/*.json"))
print(f"Total problems found: {len(problem_files)}")

missing_fields_per_prob = {}
schema_parse_failures = []
diff_list = []

for p_path in problem_files:
    with open(p_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    
    # Check parse via Pydantic schema
    try:
        p_obj = load_problem_from_file(p_path)
    except Exception as e:
        schema_parse_failures.append((p_path, str(e)))

    # Missing required fields
    missing = [f for f in REQUIRED_FIELDS if f not in raw]
    if missing:
        missing_fields_per_prob[raw.get("id", p_path)] = missing

    # Check top-level signature field vs starter_code line 1
    # Also check statement_md embedded signature vs starter_code line 1
    sig_field = raw.get("signature") # None in all
    starter_l1 = raw.get("starter_code", "").splitlines()[0].strip()

    # Statement markdown embedded signature
    s_md = raw.get("statement_md", "")
    m = re.search(r"###\s*Function Signature\s*```(?:python)?\s*[\r\n]+(.*?)```", s_md, re.DOTALL)
    stmt_sig = m.group(1).strip() if m else None

    # Check differences
    diffs = {}
    if sig_field is None:
        diffs["top_level_signature_field"] = "MISSING / None"
    elif sig_field.splitlines()[0].strip() != starter_l1:
        diffs["top_level_signature_field"] = sig_field.splitlines()[0].strip()

    if stmt_sig and stmt_sig != starter_l1:
        diffs["statement_md_signature"] = stmt_sig

    if diffs:
        diff_list.append({
            "id": raw["id"],
            "starter_code_l1": starter_l1,
            "statement_sig": stmt_sig,
            "signature_field": sig_field,
            "diffs": diffs
        })

print(f"Schema parse failures: {len(schema_parse_failures)}")
print(f"Problems with missing required schema fields: {len(missing_fields_per_prob)}")
print(f"Problems where statement/signature diverges from starter_code: {len(diff_list)} / {len(problem_files)}")
for item in diff_list:
    print(f"\nProblem: {item['id']}")
    print(f"  starter_code line 1 : {item['starter_code_l1']}")
    print(f"  statement_md sig    : {item['statement_sig']}")
    print(f"  signature field     : {item['signature_field']}")
