import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Parse the benchmark result")
    parser.add_argument("--logdir_path", type=Path, default="./out_log")
    parser.add_argument("--csv_path", type=Path, default="./bench_result.csv")
    return parser.parse_args()


def get_namespace_args(log: str) -> dict:
    if "Namespace" not in log:
        return {}

    # Extract the namespace information
    args_info_str = re.search(r"Namespace\((.*)\)", log)[1]
    # replace ", " with "," when it's between [ ]
    args_info_str = re.sub(
        r"\[(.*?)\]|\((.*?)\)|\}(.*?)\}",
        lambda x: x.group(0).replace(", ", ","),
        args_info_str,
    )
    args_info_list = args_info_str.split(", ")
    return {config.split("=")[0]: config.split("=")[1] for config in args_info_list}


def get_bench_info(log: str) -> dict:
    if "BenchmarkParameters(" not in log:
        return {}

    bench_info_str = re.search(
        r"BenchmarkParameters\(\n(.*?)\n\)\n", log, flags=re.DOTALL
    )[1]
    bench_info_str = bench_info_str.replace("    ", "")
    bench_info_str = bench_info_str.split(",\n")
    print(bench_info_str)
    return {config.split("=")[0]: config.split("=")[1] for config in bench_info_str}


def get_iteration_info(log: str) -> dict:
    if "Epoch" not in log:
        return {}

    iteration_info_str = re.findall(
        r"Epoch: \[[0-9]*\]  \[[0-9/ ]*\].* time: ([0-9\.]*)"
        + r"  data: ([0-9\.]*)  max mem: ([0-9\.]*)",
        log,
    )
    iteration_times = np.array([float(time[0]) for time in iteration_info_str])
    iteration_data_times = np.array([float(time[1]) for time in iteration_info_str])
    iteration_max_mem = np.array([float(time[2]) for time in iteration_info_str])
    start_idx = 20
    return {
        "max_iteration_time": iteration_times[start_idx:].max(),
        "avg_iteration_time": iteration_times[start_idx:].mean(),
        "max_iteration_data_time": iteration_data_times[start_idx:].max(),
        "avg_iteration_data_times": iteration_data_times[start_idx:].mean(),
        "max_iteration_mem": iteration_max_mem[start_idx:].max(),
    }


def update_df(new_info: dict | pd.DataFrame, df: pd.DataFrame):
    if isinstance(new_info, dict):
        new_info = pd.DataFrame([new_info])

    df = pd.concat([df, new_info], ignore_index=True, sort=False)
    return df


def gather_results():
    args = parse_args()

    if args.csv_path.exists():
        df = pd.read_csv(args.csv_path)
    else:
        df = pd.DataFrame(columns=["log_name"])

    for log_path in args.logdir_path.glob("*.out"):
        if log_path.name not in df["log_name"].values:
            print(f"Processing {log_path}")
            config_dict = {"log_name": log_path.name}
            log = log_path.read_text()
            config_dict.update(get_namespace_args(log))
            config_dict.update(get_bench_info(log))
            config_dict.update(get_iteration_info(log))
            df = update_df(config_dict, df)
            print(f"Processed {log_path}")

    df.to_csv(args.csv_path, index=False)
    print(f"Saved to {args.csv_path}")


if __name__ == "__main__":
    gather_results()
