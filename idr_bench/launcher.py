#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from pathlib import Path
from typing import Any

import yaml

from .grid_space import GridSpace
from .slurm_job import write_slurm_script, submit_slurm_script
from .utils import Config, query_yes_no


def parse_configs() -> tuple[Config, dict[str, Any]]:
    parser = ArgumentParser(description="Benchmark Config", add_help=False)
    parser.add_argument(
        "-c",
        "--config",
        default=None,
        type=Path,
        metavar="FILE",
        help="YAML config file specifying default arguments",
    )
    parser.add_argument(
        "--constraint",
        "--constraints",
        default=None,
        type=str,
        nargs="*",
        action="extend",
        dest="constraints",
        help="Constraints to respect when launching a benchmark.",
    )
    parser.add_argument(
        "--template",
        type=Path,
        required=True,
        help="Name of the benchmark template to submit to Slurm.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("out_log"),
        help="Where to store submission files and logs",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="do not submit anything, just pretend"
    )

    args, remaining = parser.parse_known_args()
    main_config = Config(**vars(args))

    config_file: Path | None = args.config
    child_config: dict[str, Any]
    if config_file is None:
        child_config = {}
    else:
        assert (
            config_file.suffix == ".yaml"
        ), "Flemme to support other extensions for now"
        with config_file.open("r") as file:
            child_config = yaml.safe_load(file)

    argument_names = [arg.split("=")[0] for arg in remaining if arg[:2] == "--"]
    parser = ArgumentParser()
    for arg in argument_names:
        parser.add_argument(arg, nargs="?", type=str, const=True)
    args = parser.parse_args(remaining)
    child_config.update(**vars(args))
    return main_config, child_config


def run():
    main_config, child_config = parse_configs()

    grid_space = GridSpace.from_dict(child_config)
    if main_config.constraints is not None:
        grid_space.add_constraints(main_config.constraints)

    slurm_scripts: list[Path] = []
    for params in grid_space:
        slurm_scripts.append(
            write_slurm_script(main_config, params)
        )

    if query_yes_no("Would you like to submit those slurm files?", default="no"):
        for slurm_script in slurm_scripts:
            has_succeeded = submit_slurm_script(slurm_script)
            if not has_succeeded:
                print(f"\033[1;31mAborted\033[0m")
                return
    else:
        print(f"\033[1;31mAborted\033[0m")
