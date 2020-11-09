from .State import State

class Player:
    def __init__(self, name = ""):
        raise NotImplementedError
    
    def get_play(self, state):
        raise NotImplementedError