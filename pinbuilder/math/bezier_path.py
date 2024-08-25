import numpy as np
import numpy.typing as npt
from collections import deque
from functools import cached_property
from typing import Self
from .bezier import Bezier
from .path import Path
from .vectors import Vec2, Vec3


class BezierPath:
    def __init__(self, beziers: list[Bezier]) -> None:
        self.beziers = beziers

    @classmethod
    def from_svgd(cls, svgd: str, dimensions: Vec2, transform: Vec2) -> Self:
        """Create a BezierPath from an SVG D attribute and associated data."""
        tokens = deque(svgd.split(" "))
        points: deque[Vec2] = deque()

        def linear_control_points(p1: Vec2, p2: Vec2) -> tuple[Vec2, Vec2]:
            return ((p2 - p1) / 4 + p1, (p2 - p1) / 4 * 3 + p1)

        while len(tokens) > 0:
            cmd = tokens.popleft()
            match cmd:
                case "M":
                    p1 = Vec2.from_string_svgd(tokens.popleft(), dimensions, transform)
                    points.append(p1)
                case "L":
                    p1 = points.pop()
                    p2 = Vec2.from_string_svgd(tokens.popleft(), dimensions, transform)
                    c1, c2 = linear_control_points(p1, p2)
                    points.extend((p1, c1, c2, p2))
                case "V":
                    p1 = points.pop()
                    p2 = Vec2.from_coords(
                        p1.x, dimensions.y - (float(tokens.popleft()) + transform.y)
                    )
                    c1, c2 = linear_control_points(p1, p2)
                    points.extend((p1, c1, c2, p2))
                case "H":
                    p1 = points.pop()
                    p2 = Vec2.from_coords(float(tokens.popleft()) + transform.x, p1.y)
                    c1, c2 = linear_control_points(p1, p2)
                    points.extend((p1, c1, c2, p2))
                case "C":
                    c1 = Vec2.from_string_svgd(tokens.popleft(), dimensions, transform)
                    c2 = Vec2.from_string_svgd(tokens.popleft(), dimensions, transform)
                    p2 = Vec2.from_string_svgd(tokens.popleft(), dimensions, transform)
                    points.extend((c1, c2, p2))
                case "Z":
                    p1 = points.pop()
                    p2 = points.popleft()
                    c1, c2 = linear_control_points(p1, p2)
                    points.appendleft(p2)
                    points.extend((p1, c1, c2, p2))
                case _:
                    raise ValueError(f"Unknown svgd command: {cmd}")
        return cls.from_scad(Path.from_points(list(points)).scad)

    @classmethod
    def from_scad(cls, scad: str) -> Self:
        """Create a BezierPath from an SCAD bezpath array string."""
        point_strings = "".join(scad.split())[2:-2].split("],[")
        vec_type = Vec2 if len(point_strings[0].split(",")) == 2 else Vec3
        points = [vec_type.from_string(point_string) for point_string in point_strings]
        beziers = [
            Bezier.from_points(*points[i : i + 4]) for i in range(0, len(points) - 3, 3)
        ]
        return cls(beziers)

    def path(self, samples: int | list[int] | npt.NDArray[np.int64]) -> Path:
        """Returns a Path instance covering all segments at the given number of samples."""
        if isinstance(samples, int):
            return sum((bezier.path(samples) for bezier in self.beziers), Path())
        if len(samples) != len(self.beziers):
            raise ValueError("Number of beziers doesn't match number of samples")
        return sum(
            (self.beziers[i].path(samples[i]) for i in range(len(samples))), Path()
        )

    def fits(self, threshold: float = 1e-2) -> npt.NDArray[np.int64]:
        """Returns the number of samples needed for each segment of the bezier path to achieve a given error distance."""
        return np.array([bezier.fit(threshold) for bezier in self.beziers])

    def bezier_lengths(self, samples: int | list[int]) -> npt.NDArray[np.float64]:
        """Returns the path length for each segment in the bezier path at the given number of samples."""
        if isinstance(samples, int):
            return np.array([beizer.path(samples).length for beizer in self.beziers])
        if len(samples) != len(self.beziers):
            raise ValueError("Number of beziers doesn't match number of samples")
        return np.array(
            [self.beziers[i].path(samples[i]).length for i in range(len(samples))]
        )

    def length(self, samples: int | list[int]) -> float:
        """Returns the total length of this path at the given number of samples."""
        return sum(self.bezier_lengths(samples))

    @cached_property
    def x_length(self) -> np.float64:
        """Return the total length over x for the bezier path."""
        return np.sum([bezier.x_length for bezier in self.beziers])

    def with_height(self, height: Self) -> Path:
        """Stitch a 3D path using self as a basepath and the parameter as a function of height over distance."""
        fits = self.fits()
        basepath = self.path(fits)
        ux = basepath.point_distances / basepath.length * height.x_length
        x_extents = [bezier.x_extent[1] for bezier in height.beziers]

        def z_sample(ux: float) -> float:
            bezier_i = np.searchsorted(x_extents, ux, side="left")
            bezier = height.beziers[np.clip(bezier_i, 0, len(height.beziers) - 1)]
            return bezier.xpoint(ux).y

        z_values = np.array([[z_sample(ux[i])] for i in range(len(basepath.array))])  # pyright: ignore[reportAny]
        return Path(np.concatenate((basepath.array, z_values), axis=1))

    @cached_property
    def scad(self) -> str:
        """Returns this bezier path as a string in BOSL-compatible SCAD bezpath array form."""

        def bezier_to_string(bezier: Bezier, points: int = 4) -> str:
            return ",".join(str(point) for point in bezier.array[:points])  # pyright: ignore[reportAny]

        def beziers_to_string(beziers: list[Bezier], points: int = 4) -> str:
            return ",".join(bezier_to_string(bezier, points) for bezier in beziers)

        return f"[{beziers_to_string(self.beziers[:-1], 3)},{bezier_to_string(self.beziers[-1])}]"

    def svgd(self, dimensions: Vec2, transform: Vec2) -> str:
        """Returns the bezier path as a d attribute for use in SVGs."""
        output: deque[str] = deque()

        output.extend(("M", self.beziers[0].p1.to_string_svgd(dimensions, transform)))
        for i, bezier in enumerate(self.beziers):
            bezier_type = (
                bezier.is_vline,
                bezier.is_hline,
                bezier.is_line,
                i == len(self.beziers) - 1
                and bezier.is_line
                and bezier.p2 == self.beziers[0].p1,
            )
            match bezier_type:
                case (True, _, _, False):
                    output.extend(
                        ("V", str(bezier.p2.to_svgd(dimensions, transform).y))
                    )
                case (_, True, _, False):
                    output.extend(
                        ("H", str(bezier.p2.to_svgd(dimensions, transform).x))
                    )
                case (_, _, True, False):
                    output.extend(
                        ("L", bezier.p2.to_string_svgd(dimensions, transform))
                    )
                case (_, _, True, True):
                    output.extend(("Z"))
                case _:
                    output.extend(
                        (
                            "C",
                            bezier.c1.to_string_svgd(dimensions, transform),
                            bezier.c2.to_string_svgd(dimensions, transform),
                            bezier.p2.to_string_svgd(dimensions, transform),
                        )
                    )

        return " ".join(list(output))
