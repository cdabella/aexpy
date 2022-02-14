from ..producer import Producer
from abc import ABC, abstractmethod
from ..models import ApiDifference, ApiBreaking


class Evaluator(Producer):
    @abstractmethod
    def eval(self, diff: "ApiDifference") -> "ApiBreaking":
        pass


def getDefault() -> "Evaluator":
    from .default import Evaluator
    return Evaluator()
