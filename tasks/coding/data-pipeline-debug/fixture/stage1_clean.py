#!/usr/bin/env python3
"""Stage 1: Clean raw input — remove rows with negative values or missing fields."""
import csv

def main():
    with open("input.csv", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            # Skip rows with missing name or id
            if not row.get("name") or not row.get("id"):
                continue
            # Skip rows with negative price or quantity
            try:
                price = float(row["price"])
                qty = int(row["quantity"])
                if price < 0 or qty < 0:
                    continue
            except (ValueError, KeyError):
                continue
            rows.append(row)

    with open("cleaned.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "category", "price", "quantity"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Stage 1: {len(rows)} rows cleaned (from input)")

if __name__ == "__main__":
    main()
