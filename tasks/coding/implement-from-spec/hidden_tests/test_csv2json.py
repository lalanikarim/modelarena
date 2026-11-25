#!/usr/bin/env python3
"""Hidden oracle for csv2json: tests all spec requirements."""
import subprocess, sys, os, json, tempfile

def run_tool(args):
    """Run csv2json.py from the current directory (the workdir)."""
    return subprocess.run(
        [sys.executable, "csv2json.py"] + args,
        capture_output=True, text=True, timeout=15
    )

def write_csv(name, content):
    path = os.path.join(tempfile.gettempdir(), f"mev_test_{name}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

errors = []

# Test 1: Basic CSV -> JSON array of objects
csv1 = write_csv("basic.csv", "name,age,score\nalice,30,95.5\nbob,25,87\n")
r = run_tool([csv1])
if r.returncode != 0:
    errors.append(f"basic: exit {r.returncode}: {r.stderr.strip()[:200]}")
else:
    data = json.loads(r.stdout)
    if not isinstance(data, list) or len(data) != 2:
        errors.append(f"basic: expected list of 2, got {type(data)} len={len(data) if isinstance(data, list) else '?'}")
    else:
        if data[0] != {"name": "alice", "age": 30, "score": 95.5}:
            errors.append(f"basic row 0: {data[0]}")
        if data[1] != {"name": "bob", "age": 25, "score": 87}:
            errors.append(f"basic row 1: {data[1]} (score should be int 87)")

# Test 2: --pretty flag
r = run_tool([csv1, "--pretty"])
if r.returncode != 0:
    errors.append(f"pretty: exit {r.returncode}")
elif "\n  " not in r.stdout:
    errors.append("pretty: output not indented with 2 spaces")

# Test 3: --limit N
csv3 = write_csv("limited.csv", "a,b\n1,2\n3,4\n5,6\n7,8\n")
r = run_tool([csv3, "--limit", "2"])
if r.returncode != 0:
    errors.append(f"limit: exit {r.returncode}")
else:
    data = json.loads(r.stdout)
    if len(data) != 2:
        errors.append(f"limit: expected 2 rows, got {len(data)}")

# Test 4: Empty file -> []
csv4 = write_csv("empty.csv", "")
r = run_tool([csv4])
if r.returncode != 0:
    errors.append(f"empty: exit {r.returncode}: {r.stderr.strip()[:200]}")
elif json.loads(r.stdout) != []:
    errors.append(f"empty: expected [], got {r.stdout.strip()}")

# Test 5: Header only -> []
csv5 = write_csv("header_only.csv", "x,y,z\n")
r = run_tool([csv5])
if r.returncode != 0:
    errors.append(f"header_only: exit {r.returncode}")
elif json.loads(r.stdout) != []:
    errors.append(f"header_only: expected [], got {r.stdout.strip()}")

# Test 6: Row with fewer fields -> pad with ""
csv6 = write_csv("short_row.csv", "a,b,c\n1,2\n")
r = run_tool([csv6])
if r.returncode != 0:
    errors.append(f"short_row: exit {r.returncode}")
else:
    data = json.loads(r.stdout)
    if data[0].get("c") != "":
        errors.append(f"short_row: missing field should be '', got {data[0].get('c')!r}")

# Test 7: Row with more fields -> ignore extras
csv7 = write_csv("long_row.csv", "a,b\n1,2,3,4\n")
r = run_tool([csv7])
if r.returncode != 0:
    errors.append(f"long_row: exit {r.returncode}")
else:
    data = json.loads(r.stdout)
    if len(data[0]) != 2:
        errors.append(f"long_row: extra fields should be ignored, got {data[0]}")

# Test 8: Nonexistent file -> exit 1 + stderr
r = run_tool([os.path.join(tempfile.gettempdir(), "mev_nonexistent_99999.csv")])
if r.returncode != 1:
    errors.append(f"nonexistent: expected exit 1, got {r.returncode}")
elif not r.stderr.strip():
    errors.append("nonexistent: expected error message on stderr")

# Test 9: Negative integers and floats
csv9 = write_csv("negatives.csv", "val\n-42\n-3.14\nhello\n")
r = run_tool([csv9])
if r.returncode != 0:
    errors.append(f"negatives: exit {r.returncode}: {r.stderr.strip()[:200]}")
else:
    data = json.loads(r.stdout)
    if data[0]["val"] != -42 or not isinstance(data[0]["val"], int):
        errors.append(f"negatives: -42 should be int, got {data[0]['val']!r} ({type(data[0]['val'])})")
    if data[1]["val"] != -3.14 or not isinstance(data[1]["val"], float):
        errors.append(f"negatives: -3.14 should be float, got {data[1]['val']!r}")
    if data[2]["val"] != "hello":
        errors.append(f"negatives: 'hello' should stay string, got {data[2]['val']!r}")

# Cleanup
for f in ["basic.csv", "limited.csv", "empty.csv", "header_only.csv", "short_row.csv", "long_row.csv", "negatives.csv"]:
    path = os.path.join(tempfile.gettempdir(), f"mev_test_{f}")
    if os.path.exists(path): os.remove(path)

if errors:
    print(f"FAIL ({len(errors)} issue(s)):")
    for e in errors: print(f"  {e}")
    sys.exit(1)
print("PASS (all 9 spec tests passed)")
