#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from dataclasses import asdict, dataclass, fields
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
    template: Path
    out_dir: Path
    dry_run: bool
    constraints: list[str]


def query_yes_no(question, default=None):
    """Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".

    Shamelessly stolen from
    https://stackoverflow.com/questions/3041986/apt-command-line-interface-like-yes-no-input
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        choice = input(question + prompt).lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")
