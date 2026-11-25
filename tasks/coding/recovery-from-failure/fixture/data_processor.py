"""Data processing module. Uses pandas (not installed in this environment)."""
import pandas as pd


def process_records(records: list[dict]) -> dict:
    """Process a list of records and return a summary.

    Expected input: list of dicts with keys: 'name' (str), 'value' (int/float), 'category' (str)

    Returns a dict with:
      - total_records: int
      - sum_values: number
      - by_category: dict mapping category -> count of records
      - max_value: number (the largest 'value')
      - min_value: number (the smallest 'value')
    """
    df = pd.DataFrame(records)

    summary = {
        "total_records": len(df),
        "sum_values": float(df["value"].sum()),
        "by_category": df["category"].value_counts().to_dict(),
        "max_value": float(df["value"].max()),
        "min_value": float(df["value"].min()),
    }
    return summary
