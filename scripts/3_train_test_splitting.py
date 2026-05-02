import sys
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split


DATASET_PATH = Path("datasense/dataset/datasense_1sec.parquet")
TEST_SIZE = 0.25
RANDOM_STATE = 12345


def _get_split_paths(name: str) -> tuple[Path, Path]:
    return tuple(
        DATASET_PATH.parent / f"_{name}_{split}_".join(DATASET_PATH.name.split("_"))
        for split in ("train", "test")
    )


def data_splitting():
    full_data = pd.read_parquet(DATASET_PATH)
    # Full data
    train_full, test_full = train_test_split(
        full_data,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        shuffle=True,
        stratify=full_data["label_extended"],
    )
    train_path, test_path = _get_split_paths("full")
    ## Saving and freeing memory
    with train_path.open("wb") as train_parquet:
        train_full.to_parquet(train_parquet, index=False)
    del train_full
    with test_path.open("wb") as test_parquet:
        test_full.to_parquet(test_parquet, index=False)
    del test_full
    # Data groups
    for device_type, data in full_data.groupby(by="device_type"):
        train_path, test_path = _get_split_paths(device_type)
        train_dev_type, test_dev_type = train_test_split(
            data,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
            shuffle=True,
            stratify=data["label_extended"],
        )
        ## Saving and freeing memory
        with train_path.open("wb") as train_parquet:
            train_dev_type.to_parquet(train_parquet, index=False)
        del train_dev_type
        with test_path.open("wb") as test_parquet:
            test_dev_type.to_parquet(test_parquet, index=False)
        del test_dev_type
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
    import sys
    sys.exit(run())
