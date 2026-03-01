from __future__ import annotations

from itertools import islice
from typing import Iterator, TypeVar

T = TypeVar("T")


def within(size: int, *idxs: int) -> bool:
    if len(idxs) == 0:
        return False

    return all(i >= 0 and i < size for i in idxs)


def slice_itr(items: list[T], index_a: int, index_b: int) -> Iterator[tuple[int, T]]:
    start = min(index_a + 1, index_b)
    stop = max(index_a, index_b + 1)

    yield from islice(enumerate(items), start, stop)
