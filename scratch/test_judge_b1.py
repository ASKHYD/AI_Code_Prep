import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import glob
from coach.judge import run_solution
from coach.problems import load_problem_from_file

for p_path in sorted(glob.glob('data/problems/*.json')):
    p = load_problem_from_file(p_path).model_dump()
    res = run_solution(p['reference_solution'], p)
    print(f"{p['id']}: status={res.get('status')} {res.get('passed')}/{res.get('total')} ({res.get('runtime_ms')}ms)")
    if res.get('status') != 'pass':
        print("  FAILED:", res)
