#!/usr/bin/env python3
"""Hidden oracle: verifies both bugs are fixed and no regressions."""
import subprocess, sys

TESTS = r'''
import sys
sys.path.insert(0, ".")
from calculator import add, subtract, multiply, divide, mean, median, clamp, percentage

errors = []

# Bug 1: subtract was reversed
if subtract(10, 4) != 6: errors.append(f"subtract(10,4)={subtract(10,4)}, expected 6")
if subtract(3, 7) != -4: errors.append(f"subtract(3,7)={subtract(3,7)}, expected -4")

# Bug 2: median even-count should average two middle elements
if median([1, 2, 3, 4]) != 2.5: errors.append(f"median([1,2,3,4])={median([1,2,3,4])}, expected 2.5")
if median([4, 1, 3, 2]) != 2.5: errors.append(f"median shuffled={median([4,1,3,2])}, expected 2.5")

# Regressions: everything else must still work
if add(2, 3) != 5: errors.append("add broken")
if multiply(3, 4) != 12: errors.append("multiply broken")
if divide(10, 2) != 5: errors.append("divide broken")
if mean([1, 2, 3, 4]) != 2.5: errors.append("mean broken")
if median([3, 1, 2]) != 2: errors.append("median odd broken")
if clamp(15, 0, 10) != 10: errors.append("clamp broken")
if percentage(25, 200) != 12.5: errors.append("percentage broken")

# API must be unchanged (no new required args, no removed functions)
try:
    divide(1, 0)
    errors.append("divide by zero should raise")
except ValueError:
    pass
except Exception as e:
    errors.append(f"divide by zero raised {type(e).__name__}, expected ValueError")

if errors:
    print("FAIL:")
    for e in errors: print(f"  {e}")
    sys.exit(1)
print("PASS (both bugs fixed, no regressions)")
'''

r = subprocess.run([sys.executable, "-c", TESTS], capture_output=True, text=True, timeout=15)
print(r.stdout.strip())
if r.stderr.strip(): print(r.stderr.strip(), file=sys.stderr)
sys.exit(r.returncode)
