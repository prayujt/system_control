from abc import ABC, abstractmethod


class MovementTracker(ABC):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'update') and callable(subclass.update))

    @abstractmethod
    def start(self):
        raise NotImplementedError
