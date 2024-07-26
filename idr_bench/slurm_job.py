#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from textwrap import dedent, indent
from uuid import uuid4

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .utils import Config, Dataclass

# Requested by Hatim
namespace_transfer = {
    "min": min,
    "int": int,
}


def new_filename() -> str:
    hour = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    random_id = uuid4().int % (2**32)
    return f"job_{hour}_{random_id}"


def generate_slurm_script(
    config: Config,
    params: Dataclass,
    filepath: Path,
) -> str:
    env = Environment(
        loader=FileSystemLoader(config.template.parent),
        autoescape=select_autoescape(),
    )
    template = env.get_template(config.template.name)

    return template.render(
        output_file=filepath.with_suffix(".out"),
        params=params,
        cli=params.to_cli(newline=True),
        **namespace_transfer,
        **asdict(params),
        **params.cli_dict(),
    )


def write_slurm_script(config: Config, params: Dataclass) -> None:
    filepath = config.out_dir / new_filename()
    slurm_script = generate_slurm_script(config, params, filepath)
    filepath = filepath.with_suffix(".slurm").resolve()
    filepath.parent.mkdir(exist_ok=True, parents=True)
    filepath.write_text(slurm_script)
    params_str = "\n".join(str(params).split("\n")[1:-1])
    params_str = indent(dedent(params_str), "\t>>> ")
    print(
        f"Would submit {filepath} with following params:\n" f"{params_str}\n{'-' * 50}"
    )
    return filepath


def submit_slurm_script(slurm_script: Path) -> bool:
    process = subprocess.run(
        ["sbatch", str(slurm_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = process.stdout.decode("utf-8").strip()
    if process.returncode == 0:
        print(f"\033[1;32m{output}\033[0m")
    else:
        print(f"\033[1;31m{output}\033[0m")
    return process.returncode == 0
