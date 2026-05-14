#!/usr/bin/env python3

"""
DataSense dataset preparation.

- Dropping unwanted columns/attributes
- Merging benign and attack data together
- Converting non-numeric attributes to dummies
- Classifying devices into types (IoT, control, infra)
- Saving prepared dataset as a parquet file
"""

import csv
from pathlib import Path
from ast import literal_eval
from collections.abc import Sequence, Iterable
import pandas as pd


RAW_BENIGN_DATA_PATH = Path("datasense/dataset/benign_samples_1sec.csv")
RAW_ATTACK_DATA_PATH = Path("datasense/dataset/attack_samples_1sec.csv")
SAVE_FULL_DATA_PATH = Path("datasense/dataset/datasense_1sec.parquet")

CONVERTERS = {
    "network_protocols_dst": literal_eval,
    "network_protocols_src": literal_eval,
    "network_ports_dst": literal_eval,
    "network_ports_src": literal_eval,
}

DROP_COLUMNS = frozenset([
    "device_mac", "label_full", "timestamp", "timestamp_start", "timestamp_end",
    "log_data-ranges_avg", "log_data-ranges_max", "log_data-ranges_min",
    "log_data-ranges_std_deviation", "log_data-types", "log_data-types_count",
    "log_interval-messages", "log_messages_count", "network_ips_all",
    "network_ips_dst", "network_ips_src", "network_macs_all", "network_macs_dst",
    "network_macs_src", "network_ports_all", "network_protocols_all",
])

CATEGORY_COLS = ["device_name", "label1", "label2", "label3", "label4"]

DOS_DDOS_PORTS = frozenset([
    "22", "23", "80", "443", "554",
    "557", "1883", "6668", "8000", "9595",
])

DOS_DDOS_PROTOCOLS = frozenset([
    "ssh", "telnet", "http", "icmp", "mqtt", "tcp", "udp", "arp",
])

UNCOMMON_ATTACK_PROTOCOLS = frozenset([
    "xlm", "telnet", "data", "dns", "icmp",
    "data", "icmp", "lbtrm", "telnet", "dns",
])

KEEP_PORTS = DOS_DDOS_PORTS
KEEP_PROTOCOLS = DOS_DDOS_PROTOCOLS.union(UNCOMMON_ATTACK_PROTOCOLS)


def get_csv_columns(csv_path: Path) -> list[str]:
    """
    Return the columns names in a CSV file.
    
    The columns names must be the first entry in the CSV file.
    """
    with open(csv_path, "r") as csv_file:
        column_names = next(csv.reader(csv_file))
    if (
        not isinstance(column_names, Sequence)
        or sum(isinstance(c, str) for c in column_names) != len(column_names)
    ):
        raise TypeError("The CSV first entry must be a column names header")
    return list(column_names)


def gen_dummies(
    dataframe: pd.DataFrame,
    target_column: str,
    keep_items: Iterable[str],
    prefix: str,
) -> pd.DataFrame:
    dummies = {}
    for item in keep_items:
        column_name = f"{prefix}_{item}"
        dummy = [item in entry for entry in dataframe[target_column]]
        if sum(dummy) < 5:
            continue
        dummies[column_name] = dummy
    dummies = pd.DataFrame(dummies, dtype="bool")
    dataframe.drop(columns=target_column, inplace=True)
    return pd.concat((dataframe, dummies), axis=1)


def prepare_dataset():
    target_columns = get_csv_columns(RAW_BENIGN_DATA_PATH)
    target_columns = [c for c in target_columns if c not in DROP_COLUMNS]
    benign_data = pd.read_csv(
        RAW_BENIGN_DATA_PATH,
        usecols=target_columns,
        converters=CONVERTERS,
    )
    attack_data = pd.read_csv(
        RAW_ATTACK_DATA_PATH,
        usecols=target_columns,
        converters=CONVERTERS,
    )
    full_data = pd.concat([benign_data, attack_data], axis=0, ignore_index=True)
    full_data[CATEGORY_COLS] = full_data[CATEGORY_COLS].astype("category")
    full_data["label_extended"] = full_data["label4"].str.cat(full_data["device_name"], sep="/").astype("category")
    # New attributes/columns
    full_data = gen_dummies(full_data, "network_protocols_src", KEEP_PROTOCOLS, "network_protocols_src_has")
    full_data = gen_dummies(full_data, "network_protocols_dst", KEEP_PROTOCOLS, "network_protocols_dst_has")
    full_data = gen_dummies(full_data, "network_ports_src", KEEP_PORTS, "network_ports_src_has")
    full_data = gen_dummies(full_data, "network_ports_dst", KEEP_PORTS, "network_ports_dst_has")
    # Device type column
    all_devices = full_data["device_name"].unique().tolist()
    iot_devices = [
        d for d in all_devices
        if (d.startswith("plug-") or d.endswith("-sensor") or d.endswith("-camera"))
    ]
    control_devices = ["mqtt-broker", "edge1"]
    devices_type = {d: "iot" for d in iot_devices}
    devices_type.update({d: "control" for d in control_devices})
    devices_type.update({d: "infra" for d in all_devices if d not in devices_type})
    full_data["device_type"] = full_data["device_name"].map(devices_type).astype("category")
    # Save full data as parquet
    with SAVE_FULL_DATA_PATH.open("wb") as data_parquet:
        full_data.to_parquet(data_parquet, index=False)
    return


def run() -> int:
    import argparse
    import logging
    import time

    logging.basicConfig(level=logging.INFO, format="[%(name)s:%(levelname)8s] %(message)s")
    logger = logging.getLogger("DATA_PREPARATION")

    parser = argparse.ArgumentParser(description="DataSense dataset preparation")
    parser.parse_args()

    try:
        start = time.monotonic()
        logger.info("Preparing dataset...")
        prepare_dataset()
        end = time.monotonic()
        logger.info(f"Finished in {end - start:.2f} seconds")
        return 0
    except Exception as e:
        import traceback
        logger.error("Error preparing dataset: %s", e)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run())
