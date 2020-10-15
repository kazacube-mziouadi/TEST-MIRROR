from abc import ABCMeta, abstractmethod

class IntuizMapInterface:
    __metaclass__ = ABCMeta

    @abstractmethod
    def map_from_intuiz(self, data): raise NotImplementedError
