#!/usr/bin/env python3

"""Print sample entries and total size of attack and benign datasets."""

import sys
import csv
from pathlib import Path


DATASET_DIR = Path("datasense/dataset")


def run() -> int:
    try:
        print("DATASET SAMPLES AND TOTAL SIZE", end="\n\n")
        for tp in ("attack", "benign"):
            print(f"=== {tp.upper()} DATA SAMPLE ===")
            data_path = DATASET_DIR / f"{tp}_samples_1sec.csv"
            with data_path.open("r") as f:
                csv_data = csv.reader(f)
                columns = next(csv_data)
                padding = max(len(c) for c in columns)
                for entry_idx, entry in enumerate(csv_data):
                    if entry_idx == 1000:
                        for colm, data in zip(columns, entry):
                            print(f">>> {colm.rjust(padding, "_")} : {data}")
            print(f"\nSIZE: {entry_idx + 1}", end=("\n\n\n" if tp == "attack" else "\n"))
        return 0
    except Exception:
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run())
