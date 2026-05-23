#!/usr/bin/env python3

"""Computation of Variance Inflation Factor values."""

import sys
import warnings
from time import monotonic
from pathlib import Path
from joblib import Parallel, delayed

import numpy as np
import pandas as pd

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.compose import make_column_transformer, make_column_selector
from statsmodels.stats.outliers_influence import variance_inflation_factor


RANDOM_STATE = 12345
TRAIN_DATA = Path("datasense/dataset/datasense_1sec_train.parquet")
SAVE_FILE = Path("datasense/dataset/vif_values.csv")


def get_normalizer():
    log1p_transformer = FunctionTransformer(np.log1p, feature_names_out="one-to-one")
    number_selector = make_column_selector(dtype_include="number")
    bool_selector = make_column_selector(dtype_include="bool")
    return make_column_transformer(
        (make_pipeline(log1p_transformer, MinMaxScaler()), number_selector),
        (OneHotEncoder(sparse_output=False), ["device_type"]),
        ("passthrough", bool_selector),
        verbose_feature_names_out=False,
    )


def get_data() -> pd.DataFrame:
    return pd.read_parquet(TRAIN_DATA)


def _vif(data: np.ndarray, i: int):
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=RuntimeWarning)
        return variance_inflation_factor(data, i)


def get_vif_values(num_samples: int = 30000, n_jobs: int = 2) -> pd.Series:
    # Data
    normalizer = get_normalizer()
    data = normalizer.fit_transform(get_data())
    feature_names = normalizer.get_feature_names_out().tolist()
    # Sampling for efficiency & add intercept
    num_samples = max(3, min(num_samples, len(data)))
    rng = np.random.default_rng(seed=RANDOM_STATE)
    sample_idxs = rng.choice(
        len(data),
        size=num_samples,
        replace=False,
        shuffle=False,
    )
    data_sample = np.ones((num_samples, data.shape[1] + 1), dtype=data.dtype)
    data_sample[:, :-1] = data[sample_idxs]
    # VIF values
    vif_values = {"index": [], "data": []}
    num_iter = len(feature_names) - 1
    for i in range(num_iter):
        start = monotonic()
        vifs = np.array(
            Parallel(n_jobs=n_jobs, return_as="list")(
                delayed(_vif)(data_sample, i)
                for i in range(data_sample.shape[1] - 1)
            )
        )
        try:
            max_vif_col = np.nanargmax(vifs).item()
        except ValueError:
            break
        if vifs[max_vif_col] <= 1.0:
            break
        feature_name_out = feature_names.pop(max_vif_col)
        vif_values["data"].append(vifs[max_vif_col].item())
        vif_values["index"].append(feature_name_out)
        data_sample = np.delete(data_sample, max_vif_col, axis=1)
        print(f"\r{i+1:03d}/{num_iter} : {(monotonic() - start):.2f} secs", end="")
    print("\nFinished")
    # Last reamining feature
    vif_values["index"].extend(feature_names)
    vif_values["data"].extend([1.0] * len(feature_names))
    # Save and return
    vif_values = pd.Series(**vif_values, name="vif")
    vif_values.to_csv(SAVE_FILE, index=True, index_label="feature")
    return vif_values


def run() -> int:
    import argparse
    import logging
    import time

    logging.basicConfig(level=logging.INFO, format="[%(name)s:%(levelname)8s] %(message)s")
    logger = logging.getLogger("FEATURES_VIF_VALUES")

    parser = argparse.ArgumentParser(
        description="Computer Variance Inflation Factor of the features"
    )
    parser.add_argument(
        "num_samples", type=int, default=30000,
        help="Number of samples for VIF estimation",
    )
    parser.add_argument(
        "--n_jobs", "-j", type=int, default=-1,
        help="Number of parallel jobs",
    )
    args = parser.parse_args()

    try:
        start = time.monotonic()
        logger.info("Computing VIF values...")
        _ = get_vif_values(args.num_samples, args.n_jobs)
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
