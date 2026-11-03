import json
from pathlib import Path

PROBLEMS = [
    {
        "id": "two-sum",
        "title": "Two Sum",
        "topic": "arrays",
        "difficulty": "easy",
        "track": "dsa",
        "statement_md": (
            "Given an array of integers `nums` and an integer `target`, return indices of the "
            "two numbers such that they add up to `target`.\n\n"
            "You may assume that each input would have at most one solution, and you may not use "
            "the same element twice. If no solution exists, return `[]`."
        ),
        "function_name": "two_sum",
        "starter_code": "def two_sum(nums: list, target: int) -> list:\n    # Write your solution here\n    pass\n",
        "visible_tests": [
            {"input_args": [[2, 7, 11, 15], 9], "expected": [0, 1]},
            {"input_args": [[3, 2, 4], 6], "expected": [1, 2]},
        ],
        "hidden_tests": [
            {"input_args": [[3, 3], 6], "expected": [0, 1]},
            {"input_args": [[-1, -2, -3, -4, -5], -8], "expected": [2, 4]},
            {"input_args": [[0, 4, 3, 0], 0], "expected": [0, 3]},
            {"input_args": [[5], 5], "expected": []},
            {"input_args": [[1, 2, 3, 9], 10], "expected": [0, 3]},
            {"input_args": [[-10, 20, 35, 50], 40], "expected": [0, 3]},
        ],
        "hints": [
            "Consider what value you need to find for each element `x`: `target - x`.",
            "Can you use a hash map to store elements you have already seen along with their indices in O(N) time?",
            "Iterate through `nums`. For each number, check if `target - num` is already in your hash map. If so, return `[seen[target - num], current_index]`. Otherwise, store `seen[num] = current_index`."
        ],
        "reference_solution": (
            "def two_sum(nums: list, target: int) -> list:\n"
            "    seen = {}\n"
            "    for i, num in enumerate(nums):\n"
            "        diff = target - num\n"
            "        if diff in seen:\n"
            "            return [seen[diff], i]\n"
            "        seen[num] = i\n"
            "    return []\n"
        ),
        "time_limit_sec": 3.0,
    },
    {
        "id": "valid-parentheses",
        "title": "Valid Parentheses",
        "topic": "stack",
        "difficulty": "easy",
        "track": "dsa",
        "statement_md": (
            "Given a string `s` containing just the characters `'('`, `')'`, `'{'`, `'}'`, `'['` and `']'`, "
            "determine if the input string is valid.\n\n"
            "An input string is valid if:\n"
            "1. Open brackets must be closed by the same type of brackets.\n"
            "2. Open brackets must be closed in the correct order.\n"
            "3. Every close bracket has a corresponding open bracket of the same type."
        ),
        "function_name": "is_valid_parentheses",
        "starter_code": "def is_valid_parentheses(s: str) -> bool:\n    # Write your solution here\n    pass\n",
        "visible_tests": [
            {"input_args": ["()"], "expected": True},
            {"input_args": ["()[]{}"], "expected": True},
        ],
        "hidden_tests": [
            {"input_args": ["(]"], "expected": False},
            {"input_args": ["([)]"], "expected": False},
            {"input_args": ["{[]}"], "expected": True},
            {"input_args": [""], "expected": True},
            {"input_args": [")("], "expected": False},
            {"input_args": ["((("], "expected": False},
        ],
        "hints": [
            "A Last-In-First-Out (LIFO) data structure works well when matching pairs that must close in reverse order.",
            "Push opening brackets onto a stack. When encountering a closing bracket, check if it matches the top of the stack.",
            "Use a mapping dictionary `{')': '(', '}': '{', ']': '['}`. If closing and stack empty or top doesn't match, return False. At the end, return `len(stack) == 0`."
        ],
        "reference_solution": (
            "def is_valid_parentheses(s: str) -> bool:\n"
            "    pairs = {')': '(', '}': '{', ']': '['}\n"
            "    stack = []\n"
            "    for ch in s:\n"
            "        if ch in pairs.values():\n"
            "            stack.append(ch)\n"
            "        elif ch in pairs:\n"
            "            if not stack or stack.pop() != pairs[ch]:\n"
            "                return False\n"
            "        else:\n"
            "            return False\n"
            "    return len(stack) == 0\n"
        ),
        "time_limit_sec": 3.0,
    },
    {
        "id": "longest-substring-without-repeating",
        "title": "Longest Substring Without Repeating Characters",
        "topic": "strings",
        "difficulty": "medium",
        "track": "dsa",
        "statement_md": (
            "Given a string `s`, find the length of the longest substring without repeating characters."
        ),
        "function_name": "length_of_longest_substring",
        "starter_code": "def length_of_longest_substring(s: str) -> int:\n    # Write your solution here\n    pass\n",
        "visible_tests": [
            {"input_args": ["abcabcbb"], "expected": 3},
            {"input_args": ["bbbbb"], "expected": 1},
        ],
        "hidden_tests": [
            {"input_args": ["pwwkew"], "expected": 3},
            {"input_args": [""], "expected": 0},
            {"input_args": [" "], "expected": 1},
            {"input_args": ["au"], "expected": 2},
            {"input_args": ["dvdf"], "expected": 3},
            {"input_args": ["abba"], "expected": 2},
        ],
        "hints": [
            "Use a sliding window defined by two pointers `left` and `right`.",
            "Maintain the last seen index of each character in a dictionary.",
            "As `right` advances, if `s[right]` was seen at index >= `left`, advance `left` to `last_seen[s[right]] + 1`. Update max length at each step."
        ],
        "reference_solution": (
            "def length_of_longest_substring(s: str) -> int:\n"
            "    last_seen = {}\n"
            "    left = 0\n"
            "    max_len = 0\n"
            "    for right, ch in enumerate(s):\n"
            "        if ch in last_seen and last_seen[ch] >= left:\n"
            "            left = last_seen[ch] + 1\n"
            "        last_seen[ch] = right\n"
            "        max_len = max(max_len, right - left + 1)\n"
            "    return max_len\n"
        ),
        "time_limit_sec": 3.0,
    },
    {
        "id": "reverse-sequence",
        "title": "Reverse Sequence In Place",
        "topic": "two-pointers",
        "difficulty": "easy",
        "track": "dsa",
        "statement_md": (
            "Write a function that reverses a list of elements in-place and returns the reversed list.\n\n"
            "Simulate two-pointer swap traversal without using `list.reverse()` or `[::-1]`."
        ),
        "function_name": "reverse_sequence",
        "starter_code": "def reverse_sequence(items: list) -> list:\n    # Write your solution here\n    pass\n",
        "visible_tests": [
            {"input_args": [[1, 2, 3, 4]], "expected": [4, 3, 2, 1]},
            {"input_args": [[10]], "expected": [10]},
        ],
        "hidden_tests": [
            {"input_args": [[]], "expected": []},
            {"input_args": [[1, 1, 1]], "expected": [1, 1, 1]},
            {"input_args": [[-5, 0, 5]], "expected": [5, 0, -5]},
            {"input_args": [[1, 2]], "expected": [2, 1]},
            {"input_args": [[9, 8, 7, 6, 5]], "expected": [5, 6, 7, 8, 9]},
        ],
        "hints": [
            "Use two pointers: one at the start `0` and one at the end `len(items) - 1`.",
            "Swap the elements at the two pointers, then move the left pointer right and right pointer left.",
            "Stop when `left >= right`. Return the modified `items` list."
        ],
        "reference_solution": (
            "def reverse_sequence(items: list) -> list:\n"
            "    left, right = 0, len(items) - 1\n"
            "    while left < right:\n"
            "        items[left], items[right] = items[right], items[left]\n"
            "        left += 1\n"
            "        right -= 1\n"
            "    return items\n"
        ),
        "time_limit_sec": 3.0,
    },
    {
        "id": "binary-search",
        "title": "Binary Search",
        "topic": "binary-search",
        "difficulty": "easy",
        "track": "dsa",
        "statement_md": (
            "Given an array of integers `nums` sorted in ascending order, and an integer `target`, "
            "write a function to search `target` in `nums`. If `target` exists, then return its index. "
            "Otherwise, return `-1`.\n\n"
            "Your algorithm must run in O(log n) runtime complexity."
        ),
        "function_name": "binary_search",
        "starter_code": "def binary_search(nums: list, target: int) -> int:\n    # Write your solution here\n    pass\n",
        "visible_tests": [
            {"input_args": [[-1, 0, 3, 5, 9, 12], 9], "expected": 4},
            {"input_args": [[-1, 0, 3, 5, 9, 12], 2], "expected": -1},
        ],
        "hidden_tests": [
            {"input_args": [[], 5], "expected": -1},
            {"input_args": [[5], 5], "expected": 0},
            {"input_args": [[5], 2], "expected": -1},
            {"input_args": [[2, 5], 5], "expected": 1},
            {"input_args": [[2, 5], 2], "expected": 0},
            {"input_args": [[-10, -5, 0, 3, 7], -10], "expected": 0},
        ],
        "hints": [
            "Maintain search boundaries `low = 0` and `high = len(nums) - 1`.",
            "Calculate `mid = (low + high) // 2`. Compare `nums[mid]` to target.",
            "If `nums[mid] == target`, return `mid`. If `nums[mid] < target`, search right (`low = mid + 1`). Otherwise search left (`high = mid - 1`)."
        ],
        "reference_solution": (
            "def binary_search(nums: list, target: int) -> int:\n"
            "    low, high = 0, len(nums) - 1\n"
            "    while low <= high:\n"
            "        mid = (low + high) // 2\n"
            "        if nums[mid] == target:\n"
            "            return mid\n"
            "        elif nums[mid] < target:\n"
            "            low = mid + 1\n"
            "        else:\n"
            "            high = mid - 1\n"
            "    return -1\n"
        ),
        "time_limit_sec": 3.0,
    },
    {
        "id": "max-subarray",
        "title": "Maximum Subarray Sum",
        "topic": "arrays",
        "difficulty": "medium",
        "track": "dsa",
        "statement_md": (
            "Given an integer array `nums`, find the contiguous subarray (containing at least one number) "
            "which has the largest sum and return its sum."
        ),
        "function_name": "max_subarray_sum",
        "starter_code": "def max_subarray_sum(nums: list) -> int:\n    # Write your solution here\n    pass\n",
        "visible_tests": [
            {"input_args": [[-2, 1, -3, 4, -1, 2, 1, -5, 4]], "expected": 6},
            {"input_args": [[1]], "expected": 1},
        ],
        "hidden_tests": [
            {"input_args": [[5, 4, -1, 7, 8]], "expected": 23},
            {"input_args": [[-1]], "expected": -1},
            {"input_args": [[-3, -2, -5]], "expected": -2},
            {"input_args": [[0, 0, 0]], "expected": 0},
            {"input_args": [[-2, -1]], "expected": -1},
            {"input_args": [[1, 2, 3, 4]], "expected": 10},
        ],
        "hints": [
            "Consider Kadane's algorithm: at each position, decide whether to extend the previous subarray or start a new one.",
            "Track `current_sum = max(num, current_sum + num)` for each number.",
            "Maintain `max_sum = max(max_sum, current_sum)`. Initialize both with `nums[0]`."
        ],
        "reference_solution": (
            "def max_subarray_sum(nums: list) -> int:\n"
            "    if not nums:\n"
            "        return 0\n"
            "    current_sum = max_sum = nums[0]\n"
            "    for num in nums[1:]:\n"
            "        current_sum = max(num, current_sum + num)\n"
            "        max_sum = max(max_sum, current_sum)\n"
            "    return max_sum\n"
        ),
        "time_limit_sec": 3.0,
    },
    {
        "id": "tree-level-order",
        "title": "Binary Tree Level Order Traversal",
        "topic": "tree-traversal",
        "difficulty": "medium",
        "track": "dsa",
        "statement_md": (
            "Given a binary tree represented as nested dictionaries with keys `'val'`, `'left'`, and `'right'` "
            "(or `None` for empty nodes), return the level order traversal of its nodes' values "
            "(i.e., from left to right, level by level).\n\n"
            "Example tree node: `{'val': 3, 'left': None, 'right': None}`."
        ),
        "function_name": "level_order_traversal",
        "starter_code": "def level_order_traversal(root: dict | None) -> list:\n    # Write your solution here\n    pass\n",
        "visible_tests": [
            {
                "input_args": [{
                    "val": 3,
                    "left": {"val": 9, "left": None, "right": None},
                    "right": {
                        "val": 20,
                        "left": {"val": 15, "left": None, "right": None},
                        "right": {"val": 7, "left": None, "right": None}
                    }
                }],
                "expected": [[3], [9, 20], [15, 7]]
            },
            {"input_args": [None], "expected": []},
        ],
        "hidden_tests": [
            {"input_args": [{"val": 1, "left": None, "right": None}], "expected": [[1]]},
            {
                "input_args": [{
                    "val": 1,
                    "left": {"val": 2, "left": {"val": 3, "left": None, "right": None}, "right": None},
                    "right": None
                }],
                "expected": [[1], [2], [3]]
            },
            {
                "input_args": [{
                    "val": 10,
                    "left": None,
                    "right": {"val": 20, "left": None, "right": {"val": 30, "left": None, "right": None}}
                }],
                "expected": [[10], [20], [30]]
            },
            {
                "input_args": [{
                    "val": -1,
                    "left": {"val": -2, "left": None, "right": None},
                    "right": {"val": -3, "left": None, "right": None}
                }],
                "expected": [[-1], [-2, -3]]
            },
            {
                "input_args": [{
                    "val": 5,
                    "left": {"val": 3, "left": {"val": 2, "left": None, "right": None}, "right": {"val": 4, "left": None, "right": None}},
                    "right": {"val": 7, "left": {"val": 6, "left": None, "right": None}, "right": {"val": 8, "left": None, "right": None}}
                }],
                "expected": [[5], [3, 7], [2, 4, 6, 8]]
            },
        ],
        "hints": [
            "Use Breadth-First Search (BFS) with a queue.",
            "Process the queue level by level by recording `level_size = len(queue)` before popping nodes for the current level.",
            "For each node at the current level, record `node['val']`, then append `node['left']` and `node['right']` (if not None) to the queue."
        ],
        "reference_solution": (
            "def level_order_traversal(root: dict | None) -> list:\n"
            "    if not root:\n"
            "        return []\n"
            "    from collections import deque\n"
            "    queue = deque([root])\n"
            "    result = []\n"
            "    while queue:\n"
            "        level = []\n"
            "        for _ in range(len(queue)):\n"
            "            node = queue.popleft()\n"
            "            level.append(node['val'])\n"
            "            if node.get('left'):\n"
            "                queue.append(node['left'])\n"
            "            if node.get('right'):\n"
            "                queue.append(node['right'])\n"
            "        result.append(level)\n"
            "    return result\n"
        ),
        "time_limit_sec": 3.0,
    },
    {
        "id": "climbing-stairs",
        "title": "Climbing Stairs",
        "topic": "dp",
        "difficulty": "easy",
        "track": "dsa",
        "statement_md": (
            "You are climbing a staircase. It takes `n` steps to reach the top.\n\n"
            "Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?"
        ),
        "function_name": "climb_stairs",
        "starter_code": "def climb_stairs(n: int) -> int:\n    # Write your solution here\n    pass\n",
        "visible_tests": [
            {"input_args": [2], "expected": 2},
            {"input_args": [3], "expected": 3},
        ],
        "hidden_tests": [
            {"input_args": [1], "expected": 1},
            {"input_args": [4], "expected": 5},
            {"input_args": [5], "expected": 8},
            {"input_args": [10], "expected": 89},
            {"input_args": [20], "expected": 10946},
        ],
        "hints": [
            "To reach step `n`, you could have arrived from step `n-1` (with a 1-step jump) or step `n-2` (with a 2-step jump).",
            "The recurrence relation is `ways(n) = ways(n-1) + ways(n-2)`, which matches Fibonacci numbers.",
            "Use two variables to track the previous two steps in O(n) time and O(1) space."
        ],
        "reference_solution": (
            "def climb_stairs(n: int) -> int:\n"
            "    if n <= 2:\n"
            "        return n\n"
            "    prev2, prev1 = 1, 2\n"
            "    for _ in range(3, n + 1):\n"
            "        curr = prev1 + prev2\n"
            "        prev2 = prev1\n"
            "        prev1 = curr\n"
            "    return prev1\n"
        ),
        "time_limit_sec": 3.0,
    },
    {
        "id": "string-permutations",
        "title": "String Permutations",
        "topic": "recursion",
        "difficulty": "medium",
        "track": "dsa",
        "statement_md": (
            "Given a string `s`, return all unique permutations of the characters in `s` sorted in lexicographical order.\n\n"
            "If `s` is empty, return `['']`."
        ),
        "function_name": "get_permutations",
        "starter_code": "def get_permutations(s: str) -> list:\n    # Write your solution here\n    pass\n",
        "visible_tests": [
            {"input_args": ["ab"], "expected": ["ab", "ba"]},
            {"input_args": ["a"], "expected": ["a"]},
        ],
        "hidden_tests": [
            {"input_args": [""], "expected": [""]},
            {"input_args": ["abc"], "expected": ["abc", "acb", "bac", "bca", "cab", "cba"]},
            {"input_args": ["aab"], "expected": ["aab", "aba", "baa"]},
            {"input_args": ["xyz"], "expected": ["xyz", "xzy", "yxz", "yzx", "zxy", "zyx"]},
            {"input_args": ["aa"], "expected": ["aa"]},
        ],
        "hints": [
            "Use recursion or backtracking, selecting each unused character at the current position.",
            "Handle duplicate characters by sorting the characters first or using a set to store unique permutations.",
            "Return the sorted list of distinct permutation strings."
        ],
        "reference_solution": (
            "def get_permutations(s: str) -> list:\n"
            "    if not s:\n"
            "        return ['']\n"
            "    chars = sorted(list(s))\n"
            "    result = set()\n"
            "    used = [False] * len(chars)\n"
            "    \n"
            "    def backtrack(path):\n"
            "        if len(path) == len(chars):\n"
            "            result.add(''.join(path))\n"
            "            return\n"
            "        for i in range(len(chars)):\n"
            "            if not used[i]:\n"
            "                used[i] = True\n"
            "                path.append(chars[i])\n"
            "                backtrack(path)\n"
            "                path.pop()\n"
            "                used[i] = False\n"
            "    backtrack([])\n"
            "    return sorted(list(result))\n"
        ),
        "time_limit_sec": 3.0,
    },
    {
        "id": "csv-column-summary",
        "title": "CSV Column Summarizer",
        "topic": "data-transformation",
        "difficulty": "medium",
        "track": "python",
        "statement_md": (
            "Write a function `summarize_csv_column(csv_text: str, column_name: str) -> dict` that parses an "
            "in-memory CSV string and computes numerical summary statistics for the specified column.\n\n"
            "The returned dictionary must have the following keys:\n"
            "- `'count'`: number of valid numeric entries (int)\n"
            "- `'sum'`: sum of values rounded to 2 decimal places (float)\n"
            "- `'mean'`: mean rounded to 2 decimal places (float)\n"
            "- `'min'`: minimum value (float)\n"
            "- `'max'`: maximum value (float)\n\n"
            "If the CSV is empty, the column does not exist, or has no valid numeric rows, return an empty dict `{}`."
        ),
        "function_name": "summarize_csv_column",
        "starter_code": "def summarize_csv_column(csv_text: str, column_name: str) -> dict:\n    # Write your solution here\n    pass\n",
        "visible_tests": [
            {
                "input_args": ["name,age,salary\nAlice,30,70000\nBob,25,50000\nCharlie,35,90000", "salary"],
                "expected": {"count": 3, "sum": 210000.0, "mean": 70000.0, "min": 50000.0, "max": 90000.0}
            },
            {
                "input_args": ["product,score\nA,4.5\nB,3.5\nC,5.0", "score"],
                "expected": {"count": 3, "sum": 13.0, "mean": 4.33, "min": 3.5, "max": 5.0}
            },
        ],
        "hidden_tests": [
            {"input_args": ["", "score"], "expected": {}},
            {"input_args": ["name,age\nAlice,30", "missing_col"], "expected": {}},
            {
                "input_args": ["id,delta\n1,-10.5\n2,20.5\n3,0.0", "delta"],
                "expected": {"count": 3, "sum": 10.0, "mean": 3.33, "min": -10.5, "max": 20.5}
            },
            {
                "input_args": ["val\n100", "val"],
                "expected": {"count": 1, "sum": 100.0, "mean": 100.0, "min": 100.0, "max": 100.0}
            },
            {
                "input_args": ["name,score\nAlice,invalid\nBob,50", "score"],
                "expected": {"count": 1, "sum": 50.0, "mean": 50.0, "min": 50.0, "max": 50.0}
            },
        ],
        "hints": [
            "Use the standard library `csv` module with `io.StringIO`.",
            "Use `csv.DictReader` to easily access fields by column name.",
            "Filter for values that can be parsed with `float(val)`. Compute count, sum, mean, min, max, and round sum/mean to 2 decimal places."
        ],
        "reference_solution": (
            "import csv\n"
            "import io\n"
            "def summarize_csv_column(csv_text: str, column_name: str) -> dict:\n"
            "    if not csv_text or not csv_text.strip():\n"
            "        return {}\n"
            "    reader = csv.DictReader(io.StringIO(csv_text.strip()))\n"
            "    values = []\n"
            "    for row in reader:\n"
            "        if column_name in row and row[column_name] is not None:\n"
            "            try:\n"
            "                values.append(float(row[column_name]))\n"
            "            except ValueError:\n"
            "                continue\n"
            "    if not values:\n"
            "        return {}\n"
            "    total = sum(values)\n"
            "    count = len(values)\n"
            "    return {\n"
            "        'count': count,\n"
            "        'sum': round(total, 2),\n"
            "        'mean': round(total / count, 2),\n"
            "        'min': min(values),\n"
            "        'max': max(values)\n"
            "    }\n"
        ),
        "time_limit_sec": 3.0,
    },
    {
        "id": "log-timestamp-filter",
        "title": "Log Timestamp Filter",
        "topic": "string-parsing",
        "difficulty": "medium",
        "track": "python",
        "statement_md": (
            "Given a list of log lines formatted as `\"YYYY-MM-DD HH:MM:SS [LEVEL] Message\"`, "
            "write a function `filter_log_events(log_lines: list, start_time: str, end_time: str) -> list` "
            "that filters and returns only the log lines where the timestamp falls between `start_time` "
            "and `end_time` (both formatted as `\"YYYY-MM-DD HH:MM:SS\"`, inclusive).\n\n"
            "Lines with malformed timestamps should be excluded."
        ),
        "function_name": "filter_log_events",
        "starter_code": "def filter_log_events(log_lines: list, start_time: str, end_time: str) -> list:\n    # Write your solution here\n    pass\n",
        "visible_tests": [
            {
                "input_args": [
                    [
                        "2026-11-04 10:00:00 [INFO] System boot",
                        "2026-11-04 10:15:30 [WARN] High memory",
                        "2026-11-04 11:00:00 [ERROR] Out of memory"
                    ],
                    "2026-11-04 10:10:00",
                    "2026-11-04 10:30:00"
                ],
                "expected": ["2026-11-04 10:15:30 [WARN] High memory"]
            },
            {
                "input_args": [
                    ["2026-01-01 00:00:00 [INFO] New year"],
                    "2026-01-01 00:00:00",
                    "2026-01-01 00:00:00"
                ],
                "expected": ["2026-01-01 00:00:00 [INFO] New year"]
            },
        ],
        "hidden_tests": [
            {
                "input_args": [[], "2026-01-01 00:00:00", "2026-01-02 00:00:00"],
                "expected": []
            },
            {
                "input_args": [
                    ["invalid log format without timestamp", "2026-11-04 12:00:00 [INFO] Valid"],
                    "2026-11-04 11:00:00",
                    "2026-11-04 13:00:00"
                ],
                "expected": ["2026-11-04 12:00:00 [INFO] Valid"]
            },
            {
                "input_args": [
                    [
                        "2026-11-04 09:00:00 [INFO] Early",
                        "2026-11-04 14:00:00 [INFO] Late"
                    ],
                    "2026-11-04 10:00:00",
                    "2026-11-04 11:00:00"
                ],
                "expected": []
            },
            {
                "input_args": [
                    [
                        "2026-11-04 08:00:00 [DEBUG] Start",
                        "2026-11-04 09:00:00 [INFO] Step 1",
                        "2026-11-04 10:00:00 [INFO] Step 2"
                    ],
                    "2026-11-04 08:00:00",
                    "2026-11-04 10:00:00"
                ],
                "expected": [
                    "2026-11-04 08:00:00 [DEBUG] Start",
                    "2026-11-04 09:00:00 [INFO] Step 1",
                    "2026-11-04 10:00:00 [INFO] Step 2"
                ]
            },
            {
                "input_args": [
                    ["2026-11-04 10:00:00 [ERROR] Fail"],
                    "2026-11-04 10:00:01",
                    "2026-11-04 11:00:00"
                ],
                "expected": []
            },
        ],
        "hints": [
            "ISO date-time formats `YYYY-MM-DD HH:MM:SS` can be compared lexicographically, or parsed using `datetime.strptime`.",
            "Extract the first 19 characters of each log line and verify they represent a valid datetime.",
            "Check `start_time <= ts <= end_time` and retain matching lines in their original order."
        ],
        "reference_solution": (
            "from datetime import datetime\n"
            "def filter_log_events(log_lines: list, start_time: str, end_time: str) -> list:\n"
            "    date_fmt = '%Y-%m-%d %H:%M:%S'\n"
            "    try:\n"
            "        start_dt = datetime.strptime(start_time, date_fmt)\n"
            "        end_dt = datetime.strptime(end_time, date_fmt)\n"
            "    except ValueError:\n"
            "        return []\n"
            "    result = []\n"
            "    for line in log_lines:\n"
            "        if len(line) < 19:\n"
            "            continue\n"
            "        ts_str = line[:19]\n"
            "        try:\n"
            "            ts_dt = datetime.strptime(ts_str, date_fmt)\n"
            "            if start_dt <= ts_dt <= end_dt:\n"
            "                result.append(line)\n"
            "        except ValueError:\n"
            "            continue\n"
            "    return result\n"
        ),
        "time_limit_sec": 3.0,
    },
    {
        "id": "flatten-nested-dict",
        "title": "Flatten Nested Dictionary",
        "topic": "dict-processing",
        "difficulty": "medium",
        "track": "python",
        "statement_md": (
            "Write a function `flatten_dict(nested: dict, prefix: str = '', sep: str = '.') -> dict` "
            "that flattens an arbitrarily deep dictionary into a single-level dictionary with compound "
            "keys joined by `sep`.\n\n"
            "Example: `{'a': 1, 'b': {'c': 2}}` -> `{'a': 1, 'b.c': 2}`."
        ),
        "function_name": "flatten_dict",
        "starter_code": "def flatten_dict(nested: dict, prefix: str = '', sep: str = '.') -> dict:\n    # Write your solution here\n    pass\n",
        "visible_tests": [
            {
                "input_args": [{"a": 1, "b": {"c": 2}}],
                "expected": {"a": 1, "b.c": 2}
            },
            {
                "input_args": [{"user": {"profile": {"name": "Alex", "age": 28}}}],
                "expected": {"user.profile.name": "Alex", "user.profile.age": 28}
            },
        ],
        "hidden_tests": [
            {"input_args": [{}], "expected": {}},
            {
                "input_args": [{"simple": "flat", "number": 42}],
                "expected": {"simple": "flat", "number": 42}
            },
            {
                "input_args": [{"config": {"database": {"host": "localhost", "port": 5432}, "debug": True}}],
                "expected": {"config.database.host": "localhost", "config.database.port": 5432, "config.debug": True}
            },
            {
                "input_args": [{"a": {"b": {"c": {"d": 99}}}}],
                "expected": {"a.b.c.d": 99}
            },
            {
                "input_args": [{"x": {"y": None, "z": False}}],
                "expected": {"x.y": None, "x.z": False}
            },
        ],
        "hints": [
            "Use recursion or an iterative stack to traverse the dictionary keys.",
            "For each key-value pair, if the value is an instance of `dict` (and not empty), recursively flatten it with new prefix `prefix + sep + key` if prefix exists else `key`.",
            "If the value is not a dict, add it directly to the output dictionary: `output[compound_key] = value`."
        ],
        "reference_solution": (
            "def flatten_dict(nested: dict, prefix: str = '', sep: str = '.') -> dict:\n"
            "    output = {}\n"
            "    for k, v in nested.items():\n"
            "        new_key = f'{prefix}{sep}{k}' if prefix else str(k)\n"
            "        if isinstance(v, dict) and v:\n"
            "            output.update(flatten_dict(v, prefix=new_key, sep=sep))\n"
            "        else:\n"
            "            output[new_key] = v\n"
            "    return output\n"
        ),
        "time_limit_sec": 3.0,
    },
]

dest_dir = Path("data/problems")
dest_dir.mkdir(parents=True, exist_ok=True)

for p in PROBLEMS:
    out_file = dest_dir / f"{p['id']}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(p, f, indent=2)
    print(f"Created: {out_file}")
