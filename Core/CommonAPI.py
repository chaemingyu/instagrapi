from abc import ABC, abstractmethod

class CommonAPI(ABC):

    @abstractmethod
    def Initialize(self):
        pass


    @abstractmethod
    def GetInstance(self):
        pass

