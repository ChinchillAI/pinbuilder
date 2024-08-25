import xml.etree.ElementTree as ET
from itertools import chain
from pathlib import Path
import re
from ..math.vectors import Vec2
from .features import Feature, PlayfieldDimensions, Unknown


def parse_dimensions(node: ET.Element) -> Vec2:
    width = float(node.get("width", "0mm")[:-2])
    height = float(node.get("height", "0mm")[:-2])
    return Vec2.from_coords(width, height)


def parse_transform(node: ET.Element, transform: Vec2) -> Vec2:
    exp = r"translate\(([0-9.-]*),([0-9.-]*)\)"
    raw = node.get("transform", "translate(0,0)")
    results = re.match(exp, raw)
    if not results:
        raise ValueError(f"Got bad transform: {raw}")
    return transform + Vec2.from_coords(
        float(results.group(1)), float(results.group(2))
    )


features_dict = {
    name: feat for feat in Feature.__subclasses__() for name in feat.names()
}


def parse_tree(
    node: ET.Element, dimensions: Vec2 | None = None, transform: Vec2 | None = None
) -> list[Feature]:
    if not dimensions:
        dimensions = Vec2.from_coords(0, 0)
    if not transform:
        transform = Vec2.from_coords(0, 0)

    match node.tag:
        case "{http://www.w3.org/2000/svg}svg":
            dimensions = parse_dimensions(node)
            return [
                PlayfieldDimensions(
                    node=node, dimensions=dimensions, transform=transform, labels=[]
                )
            ] + list(
                chain(*[parse_tree(child, dimensions, transform) for child in node])
            )
        case (
            "{http://www.w3.org/2000/svg}defs"
            | "{http://www.w3.org/2000/svg}image"
            | "{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}namedview"
        ):
            return []
        case "{http://www.w3.org/2000/svg}g":
            return list(
                chain(
                    *[
                        parse_tree(child, dimensions, parse_transform(node, transform))
                        for child in node
                    ]
                )
            )
        case "{http://www.w3.org/2000/svg}path" | "{http://www.w3.org/2000/svg}circle":
            feature_type, *rest = node.get(
                "{http://www.inkscape.org/namespaces/inkscape}label", "Unknown"
            ).split(" ")

            return [
                features_dict.get(feature_type, Unknown)(
                    node=node,
                    dimensions=dimensions,
                    transform=parse_transform(node, transform),
                    labels=rest,
                )
            ]
        case _:
            raise ValueError(f"Unknown SVG tag: {node.tag}")


def parse(path: Path) -> list[Feature]:
    tree = ET.parse(path)
    root = tree.getroot()
    return parse_tree(root)
