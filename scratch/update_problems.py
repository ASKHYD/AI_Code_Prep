"""
Script to update all 12 problem definitions:
1. Ensure statement_md contains exact required function signature in a code block with input/output types.
2. Align longest-substring-without-repeating function_name, starter_code, reference_solution to longest_substring.
3. Validate all 12 problems against ProblemSchema.
4. Verify all 12 reference solutions pass 100% through run_solution.
"""

import json
from pathlib import Path
from coach.problems import ProblemSchema, load_all_problems
from coach.judge import run_solution

problems_dir = Path("data/problems")

SIGNATURES = {
    "binary-search": {
        "function_name": "binary_search",
        "sig_block": """### Function Signature
```python
def binary_search(nums: list[int], target: int) -> int:
```
**Inputs**:
- `nums` (`list[int]`): Sorted array of integers in ascending order.
- `target` (`int`): Integer value to search for.

**Output**:
- `int`: Index of `target` in `nums`, or `-1` if not found.
""",
    },
    "climbing-stairs": {
        "function_name": "climb_stairs",
        "sig_block": """### Function Signature
```python
def climb_stairs(n: int) -> int:
```
**Inputs**:
- `n` (`int`): Total number of stairs to reach the top ($n \\ge 1$).

**Output**:
- `int`: Number of distinct ways to climb to the top taking 1 or 2 steps.
""",
    },
    "csv-column-summary": {
        "function_name": "summarize_csv_column",
        "sig_block": """### Function Signature
```python
def summarize_csv_column(csv_text: str, column_name: str) -> dict:
```
**Inputs**:
- `csv_text` (`str`): In-memory CSV formatted string.
- `column_name` (`str`): Target column to summarize.

**Output**:
- `dict`: Dictionary with keys `count` (int), `sum` (float), `mean` (float), `min` (float), `max` (float), or `{}` if empty/invalid.
""",
    },
    "flatten-nested-dict": {
        "function_name": "flatten_dict",
        "sig_block": """### Function Signature
```python
def flatten_dict(nested: dict, prefix: str = "", sep: str = ".") -> dict:
```
**Inputs**:
- `nested` (`dict`): Arbitrarily nested dictionary.
- `prefix` (`str`, optional): Prefix for keys (default `""`).
- `sep` (`str`, optional): Separator character (default `"."`).

**Output**:
- `dict`: Single-level flattened dictionary with compound keys.
""",
    },
    "log-timestamp-filter": {
        "function_name": "filter_log_events",
        "sig_block": """### Function Signature
```python
def filter_log_events(log_lines: list[str], start_time: str, end_time: str) -> list[str]:
```
**Inputs**:
- `log_lines` (`list[str]`): List of log lines formatted as `"YYYY-MM-DD HH:MM:SS [LEVEL] Message"`.
- `start_time` (`str`): Start timestamp threshold (`"YYYY-MM-DD HH:MM:SS"`).
- `end_time` (`str`): End timestamp threshold (`"YYYY-MM-DD HH:MM:SS"`).

**Output**:
- `list[str]`: Matching log lines within the timestamp window (inclusive).
""",
    },
    "longest-substring-without-repeating": {
        "function_name": "longest_substring",
        "starter_code": "def longest_substring(s: str) -> int:\n    # Write your solution here\n    pass\n",
        "reference_solution": """def longest_substring(s: str) -> int:
    last_seen = {}
    left = 0
    max_len = 0
    for right, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= left:
            left = last_seen[ch] + 1
        last_seen[ch] = right
        max_len = max(max_len, right - left + 1)
    return max_len
""",
        "sig_block": """### Function Signature
```python
def longest_substring(s: str) -> int:
```
**Inputs**:
- `s` (`str`): An input string.

**Output**:
- `int`: Length of the longest substring without repeating characters.
""",
    },
    "max-subarray": {
        "function_name": "max_subarray_sum",
        "sig_block": """### Function Signature
```python
def max_subarray_sum(nums: list[int]) -> int:
```
**Inputs**:
- `nums` (`list[int]`): List of integers with length $\\ge 1$.

**Output**:
- `int`: Maximum contiguous subarray sum.
""",
    },
    "reverse-sequence": {
        "function_name": "reverse_sequence",
        "sig_block": """### Function Signature
```python
def reverse_sequence(items: list) -> list:
```
**Inputs**:
- `items` (`list`): List of elements to reverse in place.

**Output**:
- `list`: The same list reversed in place.
""",
    },
    "string-permutations": {
        "function_name": "get_permutations",
        "sig_block": """### Function Signature
```python
def get_permutations(s: str) -> list[str]:
```
**Inputs**:
- `s` (`str`): Input string.

**Output**:
- `list[str]`: Lexicographically sorted unique permutations of `s`.
""",
    },
    "tree-level-order": {
        "function_name": "level_order_traversal",
        "sig_block": """### Function Signature
```python
def level_order_traversal(root: dict | None) -> list[list[int]]:
```
**Inputs**:
- `root` (`dict` or `None`): Root of binary tree with keys `'val'`, `'left'`, `'right'`.

**Output**:
- `list[list[int]]`: Level-by-level node values from top to bottom.
""",
    },
    "two-sum": {
        "function_name": "two_sum",
        "sig_block": """### Function Signature
```python
def two_sum(nums: list[int], target: int) -> list[int]:
```
**Inputs**:
- `nums` (`list[int]`): Array of integers.
- `target` (`int`): Target sum integer.

**Output**:
- `list[int]`: 0-based indices `[i, j]` such that `nums[i] + nums[j] == target`, or `[]`.
""",
    },
    "valid-parentheses": {
        "function_name": "is_valid_parentheses",
        "sig_block": """### Function Signature
```python
def is_valid_parentheses(s: str) -> bool:
```
**Inputs**:
- `s` (`str`): String containing bracket characters `()[]{}`.

**Output**:
- `bool`: `True` if bracket sequence is valid, `False` otherwise.
""",
    },
}


def update_all():
    for f in problems_dir.glob("*.json"):
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)

        pid = data["id"]
        info = SIGNATURES.get(pid)
        if not info:
            continue

        # Update function_name if specified
        if "function_name" in info:
            data["function_name"] = info["function_name"]
        if "starter_code" in info:
            data["starter_code"] = info["starter_code"]
        if "reference_solution" in info:
            data["reference_solution"] = info["reference_solution"]

        # Clean statement_md: strip old signature block if present, append fresh signature block
        base_statement = data["statement_md"].split("### Function Signature")[0].strip()
        data["statement_md"] = f"{base_statement}\n\n{info['sig_block']}".strip()

        # Validate with ProblemSchema
        schema = ProblemSchema(**data)

        # Write back
        with open(f, "w", encoding="utf-8") as fp:
            json.dump(schema.model_dump(), fp, indent=2)

        print(f"Updated {pid} -> {schema.function_name}")


if __name__ == "__main__":
    update_all()
    # Check all reference solutions pass 100%
    probs = load_all_problems("data/problems")
    for p in probs:
        p_dict = p.model_dump()
        res = run_solution(p.reference_solution, p_dict)
        assert res["status"] == "pass", f"Reference solution failed for {p.id}: {res}"
        print(f"Verified {p.id}: PASS ({res['passed']}/{res['total']} in {res['runtime_ms']}ms)")
