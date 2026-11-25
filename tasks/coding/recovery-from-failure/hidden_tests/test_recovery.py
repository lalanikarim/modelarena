#!/usr/bin/env python3
"""Hidden oracle: verifies the program runs and produces correct output."""
import subprocess, sys, json

r = subprocess.run(
    [sys.executable, "main.py"],
    capture_output=True, text=True, timeout=30, cwd="."
)

if r.returncode != 0:
    print(f"FAIL: main.py exited {r.returncode}")
    print(f"stderr: {r.stderr.strip()[:500]}")
    sys.exit(1)

try:
    output = json.loads(r.stdout)
except json.JSONDecodeError as e:
    print(f"FAIL: stdout is not valid JSON: {e}")
    print(f"stdout: {r.stdout[:300]}")
    sys.exit(1)

errors = []

# Verify structure
for key in ["total_records", "sum_values", "by_category", "max_value", "min_value"]:
    if key not in output:
        errors.append(f"missing key: {key}")

if errors:
    print("FAIL:")
    for e in errors: print(f"  {e}")
    sys.exit(1)

# Verify values against known input data
expected = {
    "total_records": 5,
    "sum_values": 99.0,  # 10+25+7+42+15
    "by_category": {"A": 2, "B": 2, "C": 1},
    "max_value": 42.0,
    "min_value": 7.0,
}

for key, val in expected.items():
    actual = output[key]
    if isinstance(val, float):
        if abs(actual - val) > 0.001:
            errors.append(f"{key}: got {actual}, expected {val}")
    elif actual != val:
        errors.append(f"{key}: got {actual!r}, expected {val!r}")

TOTAL = 10
passed = TOTAL - len(errors)
print(f"SCORE: {passed}/{TOTAL}")
if errors:
    print("FAIL:")
    for e in errors: print(f"  {e}")
    sys.exit(1)

print("PASS (program runs, output correct)")
