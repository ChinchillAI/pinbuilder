from typing import Self
import numpy as np
import numpy.typing as npt
from itertools import pairwise

from ..svg.features import Feature, RampPath, RampWidth, RampHeight
from ..math.path import Path


class Ramp:
    def __init__(
        self, basepath: RampPath, widths: list[RampWidth], heightpath: RampHeight
    ):
        self.basepath = basepath
        self.widths = widths
        self.heightpath = heightpath

    @staticmethod
    def cross_section_box(
        h: float = 25, w: float = 20, t: float = 2, o: float = 5
    ) -> Path:
        return Path(
            np.array(
                [
                    [w, 0],
                    [w, h],
                    [w + t + o, h],
                    [w + t + o, h - t],
                    [w + t, h - t],
                    [w + t, -t],
                    [-w - t, -t],
                    [-w - t, h - t],
                    [-w - t - o, h - t],
                    [-w - t - o, h],
                    [-w, h],
                    [-w, 0],
                ]
            )
        )

    @staticmethod
    def cross_section_outer(
        h: float = 25, w: float = 20, t: float = 2, o: float = 5
    ) -> Path:
        return Path(
            np.array(
                [
                    [w + t + o, h],
                    [w + t + o, h - t],
                    [w + t, h - t],
                    [w + t, -t],
                    [-w - t, -t],
                    [-w - t, h - t],
                    [-w - t - o, h - t],
                    [-w - t - o, h],
                ]
            )
        )

    @staticmethod
    def cross_section_inner(
        h: float = 100, w: float = 20, t: float = 2, o: float = 5
    ) -> Path:
        return Path(np.array(list(reversed([[w, 0], [w, h], [-w, h], [-w, 0]]))))

    @staticmethod
    def cross_section_inner_both(
        h: float = 25, w: float = 20, t: float = 2, o: float = 5, c: float = 25
    ) -> Path:
        return Path(
            np.array(
                [
                    [w, 0],
                    [w, h],
                    [w + o + t, h],
                    [w + o + t, h + c],
                    [-w - o - t, h + c],
                    [-w - o - t, h],
                    [-w, h],
                    [-w, 0],
                ]
            )
        )

    @staticmethod
    def cross_section_inner_left(
        h: float = 25, w: float = 20, t: float = 2, o: float = 5, c: float = 25
    ) -> Path:
        return Path(
            np.array(
                [
                    [w, 0],
                    [w, h + c],
                    [-w - o - t, h + c],
                    [-w - o - t, h],
                    [-w, h],
                    [-w, 0],
                ]
            )
        )

    @staticmethod
    def cross_section_inner_right(
        h: float = 25, w: float = 20, t: float = 2, o: float = 5, c: float = 25
    ) -> Path:
        return Path(
            np.array(
                [
                    [w, 0],
                    [w, h],
                    [w + o + t, h],
                    [w + o + t, h + c],
                    [-w, h + c],
                    [-w, 0],
                ]
            )
        )

    @classmethod
    def collate_ramps(cls, features: list[Feature]) -> dict[str, Self]:
        basepaths = {f.id: f for f in features if isinstance(f, RampPath)}
        widths = {
            k: sorted(
                [w for w in features if isinstance(w, RampWidth) and w.id == k],
                key=lambda x: x.index,
            )
            for k in basepaths.keys()
        }
        heightpaths = {hp.id: hp for hp in features if isinstance(hp, RampHeight)}
        return {
            k: cls(basepaths[k], widths[k], heightpaths[k]) for k in basepaths.keys()
        }

    @property
    def has_widths(self) -> bool:
        if self.basepath.bezierpath is None:
            return False
        return len(self.widths) == len(self.basepath.bezierpath.beziers) + 1

    @property
    def has_heightpath(self) -> bool:
        if self.basepath.bezierpath is None or self.heightpath.bezierpath is None:
            return False

        fits = self.basepath.bezierpath.fits()

        print(
            f"{self.basepath.bezierpath.length(fits)} == {self.heightpath.bezierpath.x_length}"
        )

        return bool(
            np.isclose(
                self.basepath.bezierpath.length(fits),
                self.heightpath.bezierpath.x_length,
                atol=1e-3,
            )
        )

    @property
    def is_valid(self) -> bool:
        return self.has_widths and self.has_heightpath

    @property
    def scad(self) -> str:
        if self.basepath.bezierpath is None or self.heightpath.bezierpath is None:
            raise ValueError("Missing path!")

        path = self.basepath.bezierpath.with_height(self.heightpath.bezierpath)
        fits = self.basepath.bezierpath.fits()
        width_samples = [w.bezierpath.length(1) for w in self.widths]
        widths = np.concatenate(
            [
                np.linspace(start, end, fits[i] + 1)
                for i, (start, end) in enumerate(pairwise(width_samples))
            ]
        )
        x_scales = widths / widths[0]
        scales = Path(np.array([[xs, 1] for xs in x_scales] + [[x_scales[-1], 1]]))
        cross_section = self.cross_section_box(w=widths[0] / 2)
        return f"""
        path_sweep({cross_section.scad}, path3d(path_merge_collinear({path.scad})), method = "manual", normal = UP, scale={scales.scad}, relaxed=true);
        """

    @property
    def scad_cutter(self) -> str:
        if self.basepath.bezierpath is None or self.heightpath.bezierpath is None:
            raise ValueError("Missing path!")

        path = self.basepath.bezierpath.with_height(self.heightpath.bezierpath)
        fits = self.basepath.bezierpath.fits()
        width_samples = [w.bezierpath.length(1) for w in self.widths]
        widths = np.concatenate(
            [
                np.linspace(start, end, fits[i] + 1)
                for i, (start, end) in enumerate(pairwise(width_samples))
            ]
        )
        x_scales = widths / widths[0]
        scales = Path(np.array([[xs, 1] for xs in x_scales] + [[x_scales[-1], 1]]))
        cross_section = self.cross_section_inner_right(w=widths[0] / 2)
        return f"""
        path_sweep({cross_section.scad}, path3d(path_merge_collinear({path.scad})), method = "manual", normal=UP, scale={scales.scad}, relaxed=true);
        """
