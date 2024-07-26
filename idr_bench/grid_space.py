#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from dataclasses import asdict, make_dataclass
from itertools import chain, product
from typing import Any, Iterator

from .utils import Dataclass


class Param:

    def __init__(self, value: str) -> None:
        super().__init__()
        self.numbers_pattern = re.compile(
            r"^(?:\d+(?:\.?\d+)?)(?:(?:[,-])*(?:\d+(?:\.?\d+)?))*$"
        )
        self.value = value

    def __iter__(self) -> Iterator[int | float | str]:
        if self.value is True:
            yield True
            yield False
        elif isinstance(self.value, (int, float)):
            yield self.value
        elif self.numbers_pattern.match(self.value):
            yield from self.extract_numbers(self.value)
        else:
            yield from self.extract_strings(self.value)

    def extract_numbers(self, string: str) -> Iterator[int | float]:
        yield from chain(*[self.extract_range(choice) for choice in string.split(",")])

    def extract_range(self, choice: str) -> Iterator[int | float]:
        splitted = choice.split("-")
        assert len(splitted) in [
            1,
            2,
        ], f"There should not be two consecutive dashes: {splitted}"
        if len(splitted) == 1:
            x = splitted[0]
            if x.isdecimal():
                yield int(x)
            else:
                try:
                    x = float(x)
                except (ValueError, TypeError):
                    pass
                yield x
        else:
            x, y = splitted[0], splitted[1]
            if x.isdecimal() and y.isdecimal():
                x, y = int(x), int(y)
                yield from range(min(x, y), max(x, y) + 1)
            else:
                raise NotImplementedError()

    def extract_strings(self, string: str) -> Iterator[str]:
        yield from string.split(",")


class GridSpace:
    def __init__(self, **attributes: dict[str, Param]) -> None:
        super().__init__()
        self.attributes = attributes
        self.constraints: list[str] = []

    def add_constraints(self, *constraints: str) -> None:
        for constraint in constraints:
            if isinstance(constraint, str):
                self.constraints.append(constraint)
            else:
                self.constraints.extend(constraint)

    def respect_constraints(self, dataclass: Dataclass) -> bool:
        if len(self.constraints) == 0:
            return True
        D = asdict(dataclass)
        for constraint in self.constraints:
            if not eval(constraint, None, D):
                return False
        return True

    @classmethod
    def from_dict(cls, config: dict[str, Any]):
        return cls(**{key: Param(value) for key, value in config.items()})

    def __iter__(self):
        iterables = [
            [(key, value) for value in values]
            for key, values in self.attributes.items()
        ]
        yield from filter(
            self.respect_constraints,
            map(self.to_dict, product(*iterables)),
        )

    @staticmethod
    def to_dict(_tuple: tuple[str, Any], /) -> Dataclass:
        D: dict[str, Any] = {key: value for key, value in _tuple}
        dataclass = make_dataclass(
            cls_name="BenchmarkParameters",
            fields=((k, type(v)) for k, v in D.items()),
            bases=(Dataclass,),
        )
        return dataclass(**D)
