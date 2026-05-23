#!/usr/bin/env python3

"""Train-test data splitting."""

import sys
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split


DATASET_PATH = Path("datasense/dataset/datasense_1sec.parquet")
TEST_SIZE = 0.25
RANDOM_STATE = 12345


def _get_split_paths() -> tuple[Path, Path]:
    return tuple(
        DATASET_PATH.parent / f"{DATASET_PATH.stem}_{split}{DATASET_PATH.suffix}"
        for split in ("train", "test")
    )


def data_splitting():
    data = pd.read_parquet(DATASET_PATH)
    train_split, test_split = train_test_split(
        data,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        shuffle=True,
        stratify=data["label_full"],
    )
    train_path, test_path = _get_split_paths()
    train_split.to_parquet(train_path, index=False, compression="gzip")
    test_split.to_parquet(test_path, index=False, compression="gzip")
    return


def run() -> int:
    import argparse
    import logging
    import time

    logging.basicConfig(level=logging.INFO, format="[%(name)s:%(levelname)8s] %(message)s")
    logger = logging.getLogger("TRAIN_TEST_SPLIT")

    parser = argparse.ArgumentParser(description="Train-test dataset splitting")
    parser.parse_args()

    try:
        start = time.monotonic()
        logger.info("Splitting dataset...")
        data_splitting()
        end = time.monotonic()
        logger.info(f"Finished in {end - start:.2f} seconds")
        return 0
    except Exception as e:
        import traceback
        logger.error("Error: %s", e)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run())
