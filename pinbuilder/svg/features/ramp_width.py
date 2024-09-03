from typing import override
from .base import Feature


class RampWidth(Feature):
    @override
    def __repr__(self) -> str:
        return f"<RampWidth '{self.id}' #{self.index}>"

    @property
    def id(self):
        return self.labels[0]

    @property
    def index(self):
        return int(self.labels[1])
