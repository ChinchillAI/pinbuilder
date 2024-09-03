from typing import override
from .base import Feature


class RampPath(Feature):
    @override
    def __repr__(self) -> str:
        return f"<RampPath '{self.id}'>"

    @property
    def id(self):
        return self.labels[0]
