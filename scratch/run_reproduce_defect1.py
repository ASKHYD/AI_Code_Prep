import subprocess
import time
import sqlite3
import os

db_path = "coach.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM attempts")
attempts_before = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM attempts WHERE status = 'pass'")
passes_before = cur.fetchone()[0]
cur.execute("SELECT id, problem_id, status, runtime_ms, hints_used, mode FROM attempts")
all_before = cur.fetchall()
conn.close()

print(f"STORE BEFORE: attempts={attempts_before}, passes={passes_before}")
print(f"RECORDS BEFORE: {all_before}")

# Start Streamlit
env = os.environ.copy()
env["PYTHONPATH"] = "."
st_proc = subprocess.Popen(
    [r".venv\Scripts\python.exe", "-m", "streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"],
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

time.sleep(3)

try:
    # Run node script
    res = subprocess.run(["node", "scratch/reproduce_defect1.js"], capture_output=True, text=True)
    print("NODE STDOUT:\n", res.stdout)
    if res.stderr:
        print("NODE STDERR:\n", res.stderr)
finally:
    st_proc.terminate()
    st_proc.wait()

conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM attempts")
attempts_after = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM attempts WHERE status = 'pass'")
passes_after = cur.fetchone()[0]
cur.execute("SELECT id, problem_id, status, runtime_ms, hints_used, mode FROM attempts")
all_after = cur.fetchall()
conn.close()

print(f"STORE AFTER: attempts={attempts_after}, passes={passes_after}")
print(f"RECORDS AFTER: {all_after}")

