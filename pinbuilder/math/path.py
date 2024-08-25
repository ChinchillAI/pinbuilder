import numpy as np
import numpy.typing as npt
from functools import cached_property
from typing import Self, override
from .vectors import Vec, Vec2, Vec3


class Path:
    def __init__(self, array: npt.NDArray[np.float64] | None = None) -> None:
        self.array = np.array([]) if array is None else array

    @classmethod
    def from_points(cls, vecs: list[Vec]) -> Self:
        return cls(np.stack([vec.array for vec in vecs]))

    def __add__(self, other: Self) -> Self:
        if len(self.array) == 0:
            return other
        other_i = 1 if (self.array[-1] == other.array[0]).all() else 0  # pyright: ignore[reportAny]
        return self.__class__(np.concatenate([self.array, other.array[other_i:]]))

    @override
    def __repr__(self) -> str:
        return str(self.array)

    @cached_property
    def point_distances(self) -> npt.NDArray[np.float64]:
        """Returns the distance down the path from start for each point."""
        seg_vec = self.array[1::] - self.array[:-1:]
        return np.add.accumulate(
            np.concatenate(
                (
                    np.array([0]),
                    np.sqrt(np.sum(seg_vec * seg_vec, axis=1)),  # pyright: ignore[reportAny]
                )
            )
        )

    @cached_property
    def length(self) -> float:
        """Returns the total distance covered by this Path."""
        seg_vec = self.array[1::] - self.array[:-1:]
        return np.sum(np.sqrt(np.sum(seg_vec * seg_vec, axis=1)))  # pyright: ignore[reportAny]

    @cached_property
    def scad(self) -> str:
        """Returns this Path as a string in SCAD-compatible array form."""
        vec_class = Vec2 if len(self.array[0]) == 2 else Vec3  # pyright: ignore[reportAny]
        points = ",".join([str(vec_class(point)) for point in self.array])  # pyright: ignore[reportAny]
        return f"[{points}]"
