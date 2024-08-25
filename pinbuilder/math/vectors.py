import numpy as np
import numpy.typing as npt
from typing import Any, Self, override


class Vec:
    def __init__(self, array: npt.NDArray[np.float64]) -> None:
        self.array = array

    @classmethod
    def from_string(cls, raw: str) -> Self:
        return cls(np.fromstring(raw, sep=","))

    def __add__(self, other: Self) -> Self:
        return self.__class__(self.array + other.array)

    def __sub__(self, other: Self) -> Self:
        return self.__class__(self.array - other.array)

    def __truediv__(self, other: float) -> Self:
        return self.__class__(self.array / other)

    def __mul__(self, other: float) -> Self:
        return self.__class__(self.array * other)

    @override
    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return np.array_equal(self.array, other.array)
        return False

    @property
    def length(self) -> float:
        return np.sqrt(self.array.dot(self.array))  # pyright: ignore[reportAny]

    @override
    def __repr__(self) -> str:
        return str(self.array)

    @override
    def __str__(self) -> str:
        return "[" + ",".join([str(np.round(v, 4)) for v in self.array]) + "]"  # pyright: ignore[reportAny,reportUnknownArgumentType]

    @property
    def x(self) -> float:
        return self.array[0]  # pyright: ignore[reportAny]

    @property
    def y(self) -> float:
        return self.array[1]  # pyright: ignore[reportAny]

    @property
    def z(self) -> float:
        return self.array[2]  # pyright: ignore[reportAny]

    def to_svgd(self, dimensions: Any, transform: Any) -> Self:  # pyright: ignore[reportAny]
        return self

    def to_string_svgd(self, dimensions: Any, transform: Any) -> str:  # pyright: ignore[reportAny]
        return "Unimplemented!"


class Vec2(Vec):
    def __init__(self, array: npt.NDArray[np.float64]) -> None:
        super().__init__(array)

    @classmethod
    def from_coords(cls, x: float = 0, y: float = 0) -> Self:
        return cls(np.array([x, y], dtype=np.float64))

    @classmethod
    def from_string_svgd(cls, raw: str, dimensions: Self, transform: Self) -> Self:
        original = cls.from_string(raw) + transform
        return cls.from_coords(original.x, dimensions.y - original.y)

    @override
    def to_svgd(self, dimensions: Self, transform: Self) -> Self:
        return self.__class__.from_coords(self.x, dimensions.y - self.y) - transform

    @override
    def to_string_svgd(self, dimensions: Self, transform: Self) -> str:
        return str(self.to_svgd(dimensions, transform))[1:-1]


class Vec3(Vec):
    def __init__(self, array: npt.NDArray[np.float64]) -> None:
        super().__init__(array)

    @classmethod
    def from_coords(cls, x: float = 0, y: float = 0, z: float = 0) -> Self:
        return cls(np.array([x, y, z], dtype=np.float64))
