import numpy as np
import numpy.typing as npt
from functools import cached_property
from typing import Self
from .vectors import Vec, Vec2, Vec3
from .path import Path


class Bezier:
    def __init__(self, array: npt.NDArray[np.float64]) -> None:
        self.array = array

    @classmethod
    def from_points(cls, p1: Vec, c1: Vec, c2: Vec, p2: Vec) -> Self:
        return cls(np.stack((p1.array, c1.array, c2.array, p2.array)))

    def path(self, samples: int = 0) -> Path:
        """Returns a Path instance containing the number of samples as points on this bezier."""
        u = np.linspace(0, 1.0, num=samples + 2)[np.newaxis, :, np.newaxis]
        d = self.array
        a = (d[1:] - d[:-1])[:, np.newaxis, :] * u + d[:-1, np.newaxis]
        b = (a[1:] - a[:-1]) * u + a[:-1]
        return Path(((b[1] - b[0]) * u + b[0])[0])  # pyright: ignore[reportAny]

    def fit(self, threshold: float = 1e-1) -> int:
        """Returns the number of samples needed to acheive the given error rate for this bezier."""

        def estimator(samples: int = 8, last_length: float | None = None) -> int:
            estimate = self.path(samples).length
            if not last_length or np.abs(estimate - last_length) > threshold:
                return estimator(samples * 2, estimate)
            return samples

        return estimator()

    def upoint(self, u: float) -> Vec:
        """Return for point on the bezier curve at the given u value."""
        vec = Vec2 if len(self.array[0]) == 2 else Vec3  # pyright: ignore[reportAny]
        d = self.array
        a = (d[1:] - d[:-1]) * u + d[:-1]
        b = (a[1:] - a[:-1]) * u + a[:-1]
        return vec((b[1] - b[0]) * u + b[0])  # pyright: ignore[reportAny]

    def xpoint(self, x: float, threshold: float = 1e-8) -> Vec:
        """Find a point on the bezier curve within threshold of the given x value."""
        if np.isclose(x, self.array[0][0], rtol=1e-3):  # pyright: ignore[reportAny]
            return Vec(self.array[0])  # pyright: ignore[reportAny]
        if np.isclose(x, self.array[-1][0], rtol=1e-3):  # pyright: ignore[reportAny]
            return Vec(self.array[-1])  # pyright: ignore[reportAny]

        def estimator(u: float = 0.5) -> Vec:
            point = self.upoint(u)
            difference = point.x - x
            if np.abs(difference) > threshold:
                e = 1e-6
                point_e = self.upoint(u + e)
                dxdu = (point_e.x - point.x) / e
                return estimator(np.clip(u - (difference / dxdu), 0, 1))  # pyright: ignore[reportAny]
            return point

        return estimator()

    @cached_property
    def x_extent(self) -> tuple[np.float64, np.float64]:
        """Returns the interval of x values this bezier spans."""
        p12x = self.array[::3, 0]
        return (np.min(p12x), np.max(p12x))

    @cached_property
    def x_length(self) -> np.float64:
        """Returns the length over the x axis for this bezier."""
        xmin, xmax = self.x_extent
        return xmax - xmin

    @cached_property
    def is_line(self) -> bool:
        units = self.array / np.linalg.norm(self.array, axis=1)[:, np.newaxis]  # pyright: ignore[reportAny]
        return np.allclose(units, units[0], atol=1e-2)  # pyright: ignore[reportAny]

    @cached_property
    def is_vline(self) -> bool:
        return self.is_line and np.allclose(
            self.p1.x,
            self.array[:, 0],
            atol=1e-2,
        )

    @cached_property
    def is_hline(self) -> bool:
        return self.is_line and np.allclose(
            self.p1.y,
            self.array[:, 1],
            atol=1e-2,
        )

    @cached_property
    def p1(self) -> Vec:
        vec_class = Vec2 if len(self.array[0]) == 2 else Vec3  # pyright: ignore[reportAny]
        return vec_class(self.array[0])  # pyright: ignore[reportAny]

    @cached_property
    def c1(self) -> Vec:
        vec_class = Vec2 if len(self.array[1]) == 2 else Vec3  # pyright: ignore[reportAny]
        return vec_class(self.array[1])  # pyright: ignore[reportAny]

    @cached_property
    def c2(self) -> Vec:
        vec_class = Vec2 if len(self.array[2]) == 2 else Vec3  # pyright: ignore[reportAny]
        return vec_class(self.array[2])  # pyright: ignore[reportAny]

    @cached_property
    def p2(self) -> Vec:
        vec_class = Vec2 if len(self.array[3]) == 2 else Vec3  # pyright: ignore[reportAny]
        return vec_class(self.array[3])  # pyright: ignore[reportAny]
