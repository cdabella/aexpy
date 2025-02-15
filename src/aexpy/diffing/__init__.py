from abc import abstractmethod
from ..models import ApiDescription, ApiDifference
from ..producers import Producer


class Differ(Producer):
    @abstractmethod
    def diff(self, old: ApiDescription, new: ApiDescription, product: ApiDifference):
        """Diff two versions of the API and return the differences."""
        pass
