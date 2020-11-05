from .State import State
from .Player import Play

class InvalidMechanicError(Exception):
    pass

class SystemMechanic:
    @staticmethod
    def is_valid(state: State) -> bool:
        raise NotImplementedError

    @staticmethod
    def reduce(state: State) -> State:
        raise NotImplementedError


class PlayerMechanic:
    @staticmethod
    def is_valid(state: State, play: Play) -> bool:
        pass
    
    @staticmethod
    def reduce(state: State, play: Play) -> State:
        pass
    
    @staticmethod
    def who_plays(sate: State) -> int:
        pass