#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
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


def generate_slurm_script(config: Config, params: Dataclass, filepath: Path) -> str:
    env = Environment(
        loader=FileSystemLoader(Path(__file__).parent / "templates"),
        autoescape=select_autoescape(),
    )
    template = env.get_template(config.template)

    return template.render(
        output_file=filepath.with_suffix(".out"),
        params=params,
        cli=params.to_cli(newline=True),
        **namespace_transfer,
        **asdict(params),
        **params.cli_dict(),
    )


def write_slurm_script(config: Config, params: Dataclass, filepath: Path) -> None:
    slurm_script = generate_slurm_script(config, params, filepath)
    filepath.parent.mkdir(exist_ok=True, parents=True)
    filepath.with_suffix(".slurm").write_text(slurm_script)


def submit_slurm_script(config: Config, params: Dataclass) -> None:
    filepath = config.directory / new_filename()
    write_slurm_script(config, params, filepath)
    complete_path = filepath.with_suffix(".slurm")
    if config.dry_run:
        print(f"Would have submitted {complete_path}")
    else:
        process = subprocess.run(
            ["sbatch", str(complete_path)],
            capture_output=True,
        )
        if process.returncode == 0:
            print(process.stdout.decode("utf-8").strip())
        else:
            print(process.stderr.decode("utf-8").strip())
