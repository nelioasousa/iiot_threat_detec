import csv
from pathlib import Path
from ast import literal_eval
import pandas as pd
from collections.abc import Sequence


RAW_BENIGN_DATA_PATH = Path("datasense/dataset/benign_samples_1sec.csv")
RAW_ATTACK_DATA_PATH = Path("datasense/dataset/attack_samples_1sec.csv")
CONVERTERS = {
    "network_protocols_dst": literal_eval,
    "network_protocols_src": literal_eval,
    "network_ports_dst": literal_eval,
    "network_ports_src": literal_eval,
}
DROP_COLUMNS = frozenset([
    "device_mac", "timestamp", "timestamp_start", "timestamp_end",
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

IOT_KEEP_PROTOCOLS = frozenset(["mqtt", "data"])
IOT_KEEP_PORTS = frozenset([
    "80", "443", "1883", "8883", "5683",
    "5684", "5671", "5672", "5353", "1900",
])

BROKER_KEEP_PROTOCOLS = frozenset(["mqtt"])
BROKER_KEEP_PORTS = frozenset([])

GENERAL_KEEP_PROTOCOLS = 40
GENERAL_KEEP_PORTS = frozenset([])


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
        raise TypeError("The CSV first entry wasn't a column names header")
    return list(column_names)


def prepare_datasets():
    target_columns = get_csv_columns(RAW_BENIGN_DATA_PATH)
    target_columns = [c for c in target_columns if c not in DROP_COLUMNS]
    benign_data = pd.read_csv(RAW_BENIGN_DATA_PATH, usecols=target_columns, converters=CONVERTERS)
    attack_data = pd.read_csv(RAW_ATTACK_DATA_PATH, usecols=target_columns, converters=CONVERTERS)
    
    return


def run() -> int:
    try:
        prepare_datasets()
        return 0
    except Exception:
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run())
