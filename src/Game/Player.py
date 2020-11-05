from .State import State

class Play:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError

class Player:
    def __init__(self, name = ""):
        raise NotImplementedError
    
    def play(self, state: State, mechanic ) -> Play:
        raise NotImplementedError