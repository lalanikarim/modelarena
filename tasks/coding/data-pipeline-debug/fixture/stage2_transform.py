#!/usr/bin/env python3
"""Stage 2: Transform cleaned data — add computed fields for analytics."""
import csv

# Price tier thresholds
TIER_THRESHOLDS = [
    (0, 20, "budget"),
    (20, 50, "mid"),
    (50, float("inf"), "premium"),
]

def get_tier(price):
    for low, high, label in TIER_THRESHOLDS:
        if low <= price < high:
            return label
    return "unknown"

def main():
    with open("cleaned.csv", newline="") as f:
        rows = list(csv.DictReader(f))

    transformed = []
    for row in rows:
        price = float(row["price"])
        qty = int(row["quantity"])

        # Compute total revenue for this product line
        total_revenue = price + qty  # BUG: should be price * qty

        # Assign price tier
        tier = get_tier(price)

        out = {
            "id": row["id"],
            "name": row["name"],
            "category": row["category"],
            "price": str(price),
            "quantity": str(qty),
            "total_revenue": str(round(total_revenue, 2)),
            "tier": tier,
        }
        transformed.append(out)

    with open("transformed.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "category", "price", "quantity", "total_revenue", "tier"])
        writer.writeheader()
        writer.writerows(transformed)

    print(f"Stage 2: {len(transformed)} rows transformed")

if __name__ == "__main__":
    main()
