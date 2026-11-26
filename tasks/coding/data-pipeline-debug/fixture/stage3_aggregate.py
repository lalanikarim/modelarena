#!/usr/bin/env python3
"""Stage 3: Aggregate transformed data into summary statistics."""
import csv
import json
from collections import defaultdict

def main():
    with open("transformed.csv", newline="") as f:
        rows = list(csv.DictReader(f))

    # Group by category
    by_category = defaultdict(lambda: {"count": 0, "total_revenue": 0.0, "total_quantity": 0})
    tier_counts = defaultdict(int)
    total_items = len(rows)
    grand_revenue = 0.0

    for row in rows:
        cat = row["category"]
        revenue = float(row["total_revenue"])
        qty = int(row["quantity"])

        by_category[cat]["count"] += 1
        by_category[cat]["total_revenue"] += revenue
        by_category[cat]["total_quantity"] += qty
        tier_counts[row["tier"]] += 1
        grand_revenue += revenue

    # Build output
    output = {
        "total_items": total_items,
        "grand_total_revenue": round(grand_revenue, 2),
        "by_category": {},
        "by_tier": dict(tier_counts),
    }

    for cat in sorted(by_category.keys()):
        data = by_category[cat]
        output["by_category"][cat] = {
            "item_count": data["count"],
            "total_revenue": round(data["total_revenue"], 2),
            "total_quantity": data["total_quantity"],
            "avg_revenue_per_item": round(data["total_revenue"] / data["count"], 2) if data["count"] else 0,
        }

    with open("output.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Stage 3: {total_items} items aggregated -> output.json")

if __name__ == "__main__":
    main()
