#!/usr/bin/env python3
"""Hidden oracle for data-pipeline-debug: verifies pipeline produces correct output."""
import subprocess, sys, os, json

errors = []
TOTAL = 8

# Run the full pipeline fresh
for stage in ["stage1_clean.py", "stage2_transform.py", "stage3_aggregate.py"]:
    r = subprocess.run([sys.executable, stage], capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        errors.append(f"{stage} failed (exit {r.returncode}): {r.stderr.strip()[:200]}")
        break

# Check output.json exists and is valid JSON
if not errors:
    if not os.path.exists("output.json"):
        errors.append("output.json not produced")
    else:
        with open("output.json") as f:
            out = json.load(f)

        # 1. total_items should be 9 (11 input rows - 2 invalid)
        if out.get("total_items") != 9:
            errors.append(f"total_items: expected 9, got {out.get('total_items')}")

        # 2. grand_total_revenue should be 62105.25 (sum of price*qty for valid rows)
        expected_revenue = 62105.25
        actual_revenue = out.get("grand_total_revenue", 0)
        if abs(actual_revenue - expected_revenue) > 0.01:
            errors.append(f"grand_total_revenue: expected {expected_revenue}, got {actual_revenue}")

        # 3. by_category should have exactly 3 categories
        cats = out.get("by_category", {})
        if set(cats.keys()) != {"electronics", "home", "office"}:
            errors.append(f"by_category keys: expected {{electronics, home, office}}, got {set(cats.keys())}")

        # 4. electronics: 3 items, revenue = 29.99*150 + 49.99*200 + 9.99*500 = 4498.5+9998+4995 = 19491.5
        # Wait let me recalculate: 29.99*150=4498.5, 49.99*200=9998, 9.99*500=4995 => total=19491.5
        elec = cats.get("electronics", {})
        if elec.get("item_count") != 3:
            errors.append(f"electronics.item_count: expected 3, got {elec.get('item_count')}")
        if abs(elec.get("total_revenue", 0) - 19491.50) > 0.01:
            errors.append(f"electronics.total_revenue: expected 19491.50, got {elec.get('total_revenue')}")

        # 5. home: 3 items, revenue = 19.99*300 + 24.99*175 + 14.99*400 = 5997+4373.25+5996 = 16366.25
        home = cats.get("home", {})
        if home.get("item_count") != 3:
            errors.append(f"home.item_count: expected 3, got {home.get('item_count')}")
        if abs(home.get("total_revenue", 0) - 16366.25) > 0.01:
            errors.append(f"home.total_revenue: expected 16366.25, got {home.get('total_revenue')}")

        # 6. office: 3 items, revenue = 99.99*50 + 149.99*75 + 79.99*125 = 4999.5+11249.25+9998.75 = 26247.5
        office = cats.get("office", {})
        if office.get("item_count") != 3:
            errors.append(f"office.item_count: expected 3, got {office.get('item_count')}")
        if abs(office.get("total_revenue", 0) - 26247.50) > 0.01:
            errors.append(f"office.total_revenue: expected 26247.50, got {office.get('total_revenue')}")

        # 7. by_tier: budget (price<20): items 3,7,8 => 3; mid (20-50): items 1,4 => wait
        # Actually: budget=<20: 9.99(7), 14.99(8), 19.99(3) = 3
        # mid=20-50: 24.99(4), 29.99(1) = 2... hmm let me recount
        # Items after cleaning: 1001(29.99), 1002(49.99), 1003(19.99), 1004(24.99), 1005(99.99), 1006(149.99), 1007(9.99), 1008(14.99), 1010(79.99)
        # budget (<20): 1003(19.99), 1007(9.99), 1008(14.99) = 3
        # mid (20-50): 1001(29.99), 1002(49.99), 1004(24.99) = 3
        # premium (>=50): 1005(99.99), 1006(149.99), 1010(79.99) = 3
        tiers = out.get("by_tier", {})
        if tiers.get("budget") != 3:
            errors.append(f"by_tier.budget: expected 3, got {tiers.get('budget')}")
        if tiers.get("mid") != 3:
            errors.append(f"by_tier.mid: expected 3, got {tiers.get('mid')}")
        if tiers.get("premium") != 3:
            errors.append(f"by_tier.premium: expected 3, got {tiers.get('premium')}")

        # 8. Verify grand total matches sum of categories
        cat_sum = sum(c.get("total_revenue", 0) for c in cats.values())
        if abs(cat_sum - out.get("grand_total_revenue", 0)) > 0.1:
            errors.append(f"internal inconsistency: category sum {cat_sum} != grand total {out.get('grand_total_revenue')}")

passed = TOTAL - len(errors)
print(f"SCORE: {passed}/{TOTAL}")
if errors:
    print(f"FAIL ({len(errors)} issue(s)):")
    for e in errors: print(f"  {e}")
    sys.exit(1)
print("PASS (pipeline produces correct output)")
