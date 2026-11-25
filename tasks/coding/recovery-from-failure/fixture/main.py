"""Main entry point. Loads and processes data."""
import json
from data_processor import process_records


def main():
    # Read input data
    with open("input.json") as f:
        records = json.load(f)

    # Process (uses pandas internally)
    result = process_records(records)

    # Output summary
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
