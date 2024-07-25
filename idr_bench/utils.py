#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field, fields, asdict
from pathlib import Path
from textwrap import indent
from typing import Any, ClassVar, Protocol

EOS = " \\\n"


class Dataclass(Protocol):
    # checking for this attribute is currently the most reliable way
    # to ascertain that something is a dataclass
    __dataclass_fields__: ClassVar[dict[str, Any]]

    def __str__(self) -> str:
        fields_str = ""
        for f in fields(self):
            fields_str += f"{f.name}={self.__getattribute__(f.name)},\n"
        fields_str = indent(fields_str, prefix=" " * 4)
        return f"{self.__class__.__qualname__}(\n{fields_str})"

    def to_cli(self, /, newline: bool = True) -> str:
        strings = []
        for f in fields(self):
            name = f.name
            value = self.__getattribute__(f.name)
            if isinstance(value, bool):
                if value is True:
                    strings.append(f"--{name}")
            else:
                strings.append(f"--{name} {value}")
        string = indent(EOS.join(strings), " " * 4)
        if newline:
            string = EOS.strip(" ") + string
        return string

    def cli_dict(self):
        output = {}
        for key, value in asdict(self).items():
            new_key = key + "_cli"
            if value is True:
                new_value = f"--{key}"
            elif value is False:
                new_value = ""
            else:
                new_value = f"--{key} {value}"
            output[new_key] = new_value
        return output


@dataclass
class Config:
    config: Path
    template: str
    out_dir: str
    dry_run: bool
    constraints: list[str]

    directory: Path = field(init=False)

    def __post_init__(self) -> None:
        self.directory = Path(__file__).parent / self.out_dir
