#!/usr/bin/env python3

"""DataSense dataset preparation.

- Dropping unwanted columns/attributes
- Merging benign and attack data together
- Converting non-numeric attributes to dummies
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
    "device_mac", "label_full", "label3",
    "timestamp", "timestamp_start", "timestamp_end",
    "log_data-ranges_avg", "log_data-ranges_max", "log_data-ranges_min",
    "log_data-ranges_std_deviation", "log_data-types", "log_data-types_count",
    "log_interval-messages", "log_messages_count", "network_ips_all",
    "network_ips_dst", "network_ips_src", "network_macs_all", "network_macs_dst",
    "network_macs_src", "network_ports_all", "network_protocols_all",
])

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
    for item in keep_items:
        column_name = f"{prefix}_item"
        dataframe[column_name] = pd.Series(
            [item in entry for entry in dataframe[target_column]],
            dtype="bool", name=column_name,
        )
    dataframe.drop(columns=target_column, inplace=True)
    return dataframe


def prepare_datasets():
    target_columns = get_csv_columns(RAW_BENIGN_DATA_PATH)
    target_columns = [c for c in target_columns if c not in DROP_COLUMNS]
    benign_data = pd.read_csv(RAW_BENIGN_DATA_PATH, usecols=target_columns, converters=CONVERTERS)
    attack_data = pd.read_csv(RAW_ATTACK_DATA_PATH, usecols=target_columns, converters=CONVERTERS)
    full_data = pd.concat([benign_data, attack_data], ignore_index=True)
    # New attributes/columns
    full_data = gen_dummies(full_data, "network_protocols_src", KEEP_PROTOCOLS, "network_src_procols_has")
    full_data = gen_dummies(full_data, "network_protocols_dst", KEEP_PROTOCOLS, "network_dst_procols_has")
    full_data = gen_dummies(full_data, "network_ports_src", KEEP_PORTS, "network_src_ports_has")
    full_data = gen_dummies(full_data, "network_ports_dst", KEEP_PORTS, "network_dst_ports_has")
    # Save full data as parquet
    full_data.to_parquet(SAVE_FULL_DATA_PATH, index=False)
    return


def run() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="DataSense dataset preparation")
    args = parser.parse_args()

    try:
        prepare_datasets()
        return 0
    except Exception:
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run())
