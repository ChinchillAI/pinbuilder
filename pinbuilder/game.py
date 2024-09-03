from pathlib import Path

from .svg.parser import parse
from .objects.ramp import Ramp


class Game:
    def __init__(self, path: Path):
        print(path.stem)
        self.svg_features = parse(path)
        self.ramps = Ramp.collate_ramps(self.svg_features)

    def generate(self, out: Path):
        headers = """
        include <BOSL2/beziers.scad>
        include <BOSL2/std.scad>
        """
        out.mkdir(parents=True, exist_ok=True)

        ramp_bodies = (
            "union() {"
            + "".join([ramp.scad for rampid, ramp in self.ramps.items()])
            + "}"
        )

        ramp_cutter = (
            "union() {"
            + "".join([ramp.scad_cutter for rampid, ramp in self.ramps.items()])
            + "}"
        )

        with open(out / "preview.scad", "w") as preview:
            _ = preview.write(headers)
            _ = preview.write("difference() {")
            _ = preview.write(ramp_bodies)
            _ = preview.write(ramp_cutter)
            _ = preview.write("}")
