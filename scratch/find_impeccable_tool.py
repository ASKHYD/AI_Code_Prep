import json

with open(r'C:\Users\MS Computer\.gemini\antigravity\brain\a88a339d-8602-40c1-9fa8-9253ebf3f144\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'impeccable' in line.lower() and 'tool_calls' in line:
            d = json.loads(line)
            tc = d.get('tool_calls', [])
            for call in tc:
                if 'impeccable' in str(call).lower():
                    print(f'Line {i}: {call}')

