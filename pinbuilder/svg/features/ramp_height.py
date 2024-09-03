from .base import Feature


class RampHeight(Feature):
    @property
    def id(self):
        return self.labels[0]
