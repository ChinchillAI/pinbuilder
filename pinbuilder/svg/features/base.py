import xml.etree.ElementTree as ET
from typing import override
from ...math.vectors import Vec2
from ...math.bezier_path import BezierPath


class Feature:
    aliases: list[str] = []

    def __init__(
        self,
        *,
        node: ET.Element,
        dimensions: Vec2,
        transform: Vec2,
        labels: list[str],
    ):
        svgd = node.get("d", None)
        self.bezierpath = (
            BezierPath.from_svgd(svgd, dimensions, transform) if svgd else None
        )

        cx, cy = node.get("cx", None), node.get("cy", None)
        self.center = (
            Vec2.from_coords(float(cx), dimensions.y - float(cy)) if cx and cy else None
        )

        self.node = node
        self.dimensions = dimensions
        self.transform = transform
        self.labels = labels

    @override
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    @classmethod
    def names(cls) -> list[str]:
        return [cls.__name__] + cls.aliases
