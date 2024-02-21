from aexpy.models import ApiDescription

from aexpy.models.description import ApiEntry
from aexpy.models.difference import DiffEntry


def add(
    a: ApiEntry | None,
    b: ApiEntry | None,
    old: ApiDescription,
    new: ApiDescription,
) -> list[DiffEntry]:
    if a is None and b is not None:
        return [
            DiffEntry(
                message=f"Add {b.__class__.__name__.removesuffix('Entry').lower()} ({b.parent}): {b.name}."
            )
        ]
    return []


def remove(
    a: ApiEntry | None,
    b: ApiEntry | None,
    old: ApiDescription,
    new: ApiDescription,
) -> list[DiffEntry]:
    if a is not None and b is None:
        if a.parent in old and a.parent not in new:
            # only report if parent exisits
            return []
        return [
            DiffEntry(
                message=f"Remove {a.__class__.__name__.removesuffix('Entry').lower()} ({a.parent}): {a.name}."
            )
        ]
    return []
